"""
سرویس تطبیق پاسخ‌ها
Response Matcher Service
"""

import re
from typing import List, Optional, Dict, Any
from django.db.models import Q
from ..models import ChatbotResponse


class ResponseMatcherService:
    """
    سرویس تطبیق پاسخ‌های از پیش تعریف شده
    """
    
    def __init__(self, target_user: str = 'both'):
        """
        مقداردهی اولیه
        
        Args:
            target_user: نوع کاربر هدف (patient, doctor, both)
        """
        self.target_user = target_user
    
    def find_matching_response(
        self, 
        message: str, 
        category: Optional[str] = None
    ) -> Optional[ChatbotResponse]:
        """
        یافتن پاسخ منطبق با پیام
        
        Args:
            message: پیام کاربر
            category: دسته‌بندی مورد نظر
            
        Returns:
            ChatbotResponse: پاسخ منطبق یا None
        """
        # فیلتر کردن پاسخ‌های فعال
        queryset = ChatbotResponse.objects.filter(
            is_active=True
        ).filter(
            Q(target_user=self.target_user) | Q(target_user='both')
        )
        
        # فیلتر بر اساس دسته‌بندی
        if category:
            queryset = queryset.filter(category=category)
        
        # مرتب‌سازی بر اساس اولویت
        responses = queryset.order_by('-priority', '-created_at')
        
        message_lower = message.lower().strip()
        
        # جستجو برای تطبیق کلمات کلیدی
        for response in responses:
            if self._matches_keywords(message_lower, response.trigger_keywords):
                return response
        
        return None
    
    def get_responses_by_category(self, category: str) -> List[ChatbotResponse]:
        """
        دریافت پاسخ‌ها بر اساس دسته‌بندی
        
        Args:
            category: دسته‌بندی
            
        Returns:
            List[ChatbotResponse]: فهرست پاسخ‌ها
        """
        return list(
            ChatbotResponse.objects.filter(
                category=category,
                is_active=True
            ).filter(
                Q(target_user=self.target_user) | Q(target_user='both')
            ).order_by('-priority', '-created_at')
        )
    
    def get_greeting_response(self) -> Optional[ChatbotResponse]:
        """
        دریافت پیام خوشامدگویی
        
        Returns:
            ChatbotResponse: پیام خوشامدگویی
        """
        responses = self.get_responses_by_category('greeting')
        return responses[0] if responses else None
    
    def get_error_response(self) -> Optional[ChatbotResponse]:
        """
        دریافت پیام خطا
        
        Returns:
            ChatbotResponse: پیام خطا
        """
        responses = self.get_responses_by_category('error')
        return responses[0] if responses else None
    
    def get_unknown_response(self) -> Optional[ChatbotResponse]:
        """
        دریافت پیام نامشخص
        
        Returns:
            ChatbotResponse: پیام نامشخص
        """
        responses = self.get_responses_by_category('unknown')
        return responses[0] if responses else None
    
    def _matches_keywords(self, message: str, keywords: List[str]) -> bool:
        """
        بررسی تطبیق کلمات کلیدی
        
        Args:
            message: پیام کاربر
            keywords: فهرست کلمات کلیدی
            
        Returns:
            bool: آیا پیام با کلمات کلیدی منطبق است؟
        """
        if not keywords:
            return False
        
        for keyword in keywords:
            keyword_lower = keyword.lower().strip()
            
            # تطبیق دقیق
            if keyword_lower in message:
                return True
            
            # تطبیق با regex (برای کلمات کلیدی پیچیده)
            if self._regex_match(keyword_lower, message):
                return True
        
        return False
    
    def _regex_match(self, pattern: str, message: str) -> bool:
        """
        تطبیق با regex
        
        Args:
            pattern: الگوی regex
            message: پیام
            
        Returns:
            bool: نتیجه تطبیق
        """
        try:
            # بررسی اینکه آیا pattern یک regex است
            if any(char in pattern for char in r'.*+?[]{}()|^$\\'):
                return bool(re.search(pattern, message))
            else:
                # تطبیق ساده کلمه
                return bool(re.search(r'\b' + re.escape(pattern) + r'\b', message))
        except re.error:
            return False
    
    def analyze_message_intent(self, message: str) -> Dict[str, Any]:
        """
        تحلیل هدف پیام
        
        Args:
            message: پیام کاربر
            
        Returns:
            Dict: تحلیل هدف
        """
        message_lower = message.lower().strip()
        
        # کلمات کلیدی برای دسته‌بندی‌های مختلف
        intent_keywords = {
            'greeting': ['سلام', 'درود', 'صبح بخیر', 'عصر بخیر', 'hello', 'hi'],
            'symptom_inquiry': ['علائم', 'درد', 'تب', 'سردرد', 'مشکل', 'بیماری'],
            'medication_info': ['دارو', 'قرص', 'کپسول', 'شربت', 'مصرف', 'دوز'],
            'appointment': ['نوبت', 'وقت', 'رزرو', 'appointment'],
            'emergency': ['اورژانس', 'فوری', 'emergency', 'urgent'],
            'farewell': ['خداحافظ', 'خدانگهدار', 'bye', 'goodbye']
        }
        
        detected_intents = []
        confidence_scores = {}
        
        for intent, keywords in intent_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in message_lower)
            if matches > 0:
                detected_intents.append(intent)
                confidence_scores[intent] = matches / len(keywords)
        
        # تعیین هدف اصلی
        primary_intent = None
        if detected_intents:
            primary_intent = max(detected_intents, key=lambda x: confidence_scores[x])
        
        return {
            'primary_intent': primary_intent,
            'detected_intents': detected_intents,
            'confidence_scores': confidence_scores,
            'message_length': len(message),
            'word_count': len(message.split())
        }