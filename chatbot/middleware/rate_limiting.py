"""
محدودسازی نرخ درخواست (Rate Limiting) برای چت‌بات
Rate Limiting Middleware for Chatbot
"""

import time
from typing import Dict, Optional
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class ChatbotRateLimitMiddleware(MiddlewareMixin):
    """
    میان‌افزار محدودسازی نرخ درخواست برای API های چت‌بات
    """
    
    # تنظیمات پیش‌فرض rate limiting
    DEFAULT_LIMITS = {
        'chatbot_message': {
            'requests': 30,  # حداکثر 30 پیام
            'window': 60,    # در 60 ثانیه
            'description': 'ارسال پیام چت‌بات'
        },
        'chatbot_session': {
            'requests': 5,   # حداکثر 5 جلسه جدید
            'window': 300,   # در 5 دقیقه
            'description': 'ایجاد جلسه چت‌بات'
        },
        'diagnosis_support': {
            'requests': 10,  # حداکثر 10 درخواست تشخیص
            'window': 600,   # در 10 دقیقه
            'description': 'پشتیبانی تشخیصی'
        },
        'medication_info': {
            'requests': 20,  # حداکثر 20 جستجوی دارو
            'window': 300,   # در 5 دقیقه
            'description': 'اطلاعات دارویی'
        }
    }
    
    def __init__(self, get_response):
        """
        مقداردهی اولیه middleware
        """
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        پردازش درخواست برای بررسی rate limit
        """
        # فقط API های چت‌بات را بررسی کن
        if not self._is_chatbot_api(request.path):
            return None
        
        # اگر کاربر احراز هویت نشده، محدودیت IP اعمال کن
        if not request.user.is_authenticated:
            return self._check_ip_rate_limit(request)
        
        # برای کاربران احراز هویت شده
        return self._check_user_rate_limit(request)
    
    def _is_chatbot_api(self, path: str) -> bool:
        """
        بررسی اینکه آیا path مربوط به API چت‌بات است
        """
        chatbot_paths = [
            '/chatbot/api/',
            '/api/chatbot/',
        ]
        return any(path.startswith(chatbot_path) for chatbot_path in chatbot_paths)
    
    def _check_ip_rate_limit(self, request) -> Optional[JsonResponse]:
        """
        بررسی محدودیت بر اساس IP
        """
        client_ip = self._get_client_ip(request)
        cache_key = f"rate_limit:ip:{client_ip}"
        
        # محدودیت سخت‌گیرانه‌تر برای IP های ناشناس
        limit_config = {
            'requests': 10,
            'window': 300,  # 5 دقیقه
            'description': 'درخواست بدون احراز هویت'
        }
        
        return self._check_rate_limit(cache_key, limit_config, request)
    
    def _check_user_rate_limit(self, request) -> Optional[JsonResponse]:
        """
        بررسی محدودیت بر اساس کاربر
        """
        user_id = request.user.id
        endpoint_type = self._get_endpoint_type(request.path)
        
        if not endpoint_type:
            return None
        
        cache_key = f"rate_limit:user:{user_id}:{endpoint_type}"
        limit_config = self.DEFAULT_LIMITS.get(endpoint_type)
        
        if not limit_config:
            return None
        
        return self._check_rate_limit(cache_key, limit_config, request)
    
    def _get_endpoint_type(self, path: str) -> Optional[str]:
        """
        تشخیص نوع endpoint بر اساس path
        """
        endpoint_mappings = {
            'send-message': 'chatbot_message',
            'start-session': 'chatbot_session',
            'diagnosis-support': 'diagnosis_support',
            'medication-info': 'medication_info',
        }
        
        for endpoint, limit_type in endpoint_mappings.items():
            if endpoint in path:
                return limit_type
        
        return None
    
    def _check_rate_limit(
        self, 
        cache_key: str, 
        limit_config: Dict, 
        request
    ) -> Optional[JsonResponse]:
        """
        بررسی اصلی rate limit
        """
        current_time = int(time.time())
        window_start = current_time - limit_config['window']
        
        # دریافت درخواست‌های فعلی از cache
        requests_data = cache.get(cache_key, [])
        
        # فیلتر کردن درخواست‌های قدیمی
        recent_requests = [
            req_time for req_time in requests_data 
            if req_time > window_start
        ]
        
        # بررسی تعداد درخواست‌ها
        if len(recent_requests) >= limit_config['requests']:
            logger.warning(
                f"Rate limit exceeded for {cache_key}. "
                f"Requests: {len(recent_requests)}/{limit_config['requests']}"
            )
            
            return self._create_rate_limit_response(limit_config, recent_requests)
        
        # اضافه کردن درخواست فعلی
        recent_requests.append(current_time)
        
        # ذخیره در cache
        cache.set(cache_key, recent_requests, limit_config['window'] + 60)
        
        return None
    
    def _create_rate_limit_response(
        self, 
        limit_config: Dict, 
        recent_requests: list
    ) -> JsonResponse:
        """
        ایجاد پاسخ محدودیت نرخ
        """
        # محاسبه زمان باقی‌مانده
        oldest_request = min(recent_requests)
        time_remaining = limit_config['window'] - (int(time.time()) - oldest_request)
        
        return JsonResponse({
            'error': 'محدودیت تعداد درخواست',
            'message': f"شما برای {limit_config['description']} بیش از حد مجاز درخواست ارسال کرده‌اید.",
            'details': {
                'limit': limit_config['requests'],
                'window_seconds': limit_config['window'],
                'retry_after_seconds': max(time_remaining, 0),
                'retry_after_minutes': max(time_remaining // 60, 0)
            }
        }, status=429)
    
    def _get_client_ip(self, request) -> str:
        """
        دریافت IP کلاینت
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or 'unknown'


class ChatbotSecurityMiddleware(MiddlewareMixin):
    """
    میان‌افزار امنیتی برای چت‌بات
    """
    
    # کلمات حساس که باید فیلتر شوند
    SENSITIVE_KEYWORDS = [
        'password', 'رمز عبور', 'پسورد',
        'social security', 'کد ملی',
        'credit card', 'کارت اعتباری',
        'bank account', 'حساب بانکی'
    ]
    
    def __init__(self, get_response):
        """
        مقداردهی اولیه
        """
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        پردازش درخواست برای بررسی امنیت
        """
        if not self._is_chatbot_api(request.path):
            return None
        
        # بررسی محتوای حساس در درخواست
        if request.method == 'POST' and hasattr(request, 'body'):
            try:
                body_content = request.body.decode('utf-8').lower()
                if self._contains_sensitive_content(body_content):
                    logger.warning(
                        f"Sensitive content detected from user {request.user.id if request.user.is_authenticated else 'anonymous'}"
                    )
                    
                    return JsonResponse({
                        'error': 'محتوای حساس',
                        'message': 'لطفاً از ارسال اطلاعات حساس مانند رمز عبور یا شماره کارت خودداری کنید.',
                        'code': 'SENSITIVE_CONTENT_DETECTED'
                    }, status=400)
            except (UnicodeDecodeError, AttributeError):
                pass
        
        return None
    
    def _is_chatbot_api(self, path: str) -> bool:
        """
        بررسی اینکه آیا path مربوط به API چت‌بات است
        """
        chatbot_paths = [
            '/chatbot/api/',
            '/api/chatbot/',
        ]
        return any(path.startswith(chatbot_path) for chatbot_path in chatbot_paths)
    
    def _contains_sensitive_content(self, content: str) -> bool:
        """
        بررسی محتوای حساس
        """
        for keyword in self.SENSITIVE_KEYWORDS:
            if keyword.lower() in content:
                return True
        return False