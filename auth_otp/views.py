"""
ویوهای سیستم احراز هویت OTP
OTP Authentication System Views
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
import logging

from .serializers import (
    OTPRequestSerializer,
    OTPVerifySerializer,
    OTPLoginResponseSerializer,
    RefreshTokenSerializer,
    TokenSerializer,
    OTPStatusSerializer,
    RateLimitStatusSerializer,
    RegisterSerializer,
    LogoutSerializer,
    UserInfoSerializer
)
from .services import OTPService, AuthService
from .models import OTPRequest, OTPRateLimit

logger = logging.getLogger(__name__)


# ====================================
# OTP Send Endpoint
# ====================================

@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp(request):
    """
    ارسال کد OTP به شماره موبایل و مدیریت پاسخ‌های مرتبط
    
    این نما (view) ورودی را با OTPRequestSerializer اعتبارسنجی می‌کند (انتظار فیلدهایی مانند phone_number، purpose و اختیاری sent_via را دارد)، سپس آدرس IP و User-Agent درخواست را استخراج کرده و از OTPService.send_otp برای ایجاد/ارسال کد استفاده می‌کند. در صورت موفقیت، پاسخ 201 همراه با داده‌های سرویس بازگردانده می‌شود؛ در صورت شکست ناشی از محدودیت نرخ، پاسخ 429 و در دیگر خطاهای معتبرسازی یا تجاری پاسخ 400 با جزئیات خطا بازگردانده می‌شود. در صورت بروز استثنای غیرمنتظره، پاسخ 500 با پیام خطای داخلی ارسال می‌شود.
    """
    try:
        # اعتبارسنجی ورودی
        serializer = OTPRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    'error': 'validation_error',
                    'message': 'داده‌های ورودی نامعتبر',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # دریافت IP و User Agent
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # ارسال OTP
        otp_service = OTPService()
        success, result = otp_service.send_otp(
            phone_number=serializer.validated_data['phone_number'],
            purpose=serializer.validated_data['purpose'],
            sent_via=serializer.validated_data.get('sent_via', 'sms'),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if success:
            return Response(
                {
                    'success': True,
                    'data': result
                },
                status=status.HTTP_201_CREATED
            )
        else:
            # تعیین کد وضعیت بر اساس نوع خطا
            if result.get('error') == 'rate_limit_exceeded':
                status_code = status.HTTP_429_TOO_MANY_REQUESTS
            else:
                status_code = status.HTTP_400_BAD_REQUEST
            
            return Response(
                {
                    'success': False,
                    'error': result.get('error'),
                    'message': result.get('message'),
                    'details': result
                },
                status=status_code
            )
            
    except Exception as e:
        logger.error(f"Error in send_otp: {str(e)}")
        return Response(
            {
                'success': False,
                'error': 'internal_error',
                'message': 'خطای سیستمی در ارسال کد تأیید'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ====================================
# OTP Verify Endpoint
# ====================================

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """
    تأیید کد OTP و ورود یا ثبت‌نام کاربر.
    
    این تابع کد OTP ارسالی را اعتبارسنجی می‌کند، در صورت موفقیت:
    - در صورت وجود نداشتن کاربر، کاربر جدیدی با user_type پیش‌فرض 'patient' ایجاد می‌کند.
    - توکن‌های احراز هویت را تولید می‌کند.
    - یک رکورد تأیید (verification) شامل اطلاعات دستگاه و session key ایجاد می‌کند.
    - پاسخ شامل توکن‌ها، اطلاعات کاربر، و پرچم is_new_user خواهد بود.
    
    ورودی (بدنۀ درخواست JSON):
    - phone_number: شماره موبایل (الزامی).
    - otp_code: کد چهار/شش رقمی ارسالی (الزامی).
    - purpose: هدف استفاده از OTP (مثلاً "login" یا "register") (الزامی).
    - device_id: شناسه دستگاه (اختیاری، برای ثبت دستگاه).
    - device_name: نام یا توصیف دستگاه (اختیاری).
    
    پاسخ‌ها:
    - 200: موفق — بدنه شامل {'success': True, 'data': {...tokens, user, is_new_user, message...}}.
    - 400: خطای اعتبارسنجی ورودی یا نامعتبر بودن/انقضای OTP — بدنه شامل جزئیات خطا.
    - 500: خطای داخلی سرور — بدنه شامل {'success': False, 'error': 'internal_error', 'message': 'خطای سیستمی در تأیید کد'}.
    
    اثرات جانبی:
    - ایجاد یا بازیابی کاربر در پایگاه داده (در صورت موفقیت).
    - تولید و ذخیره توکن‌ها و رکورد تأیید با اطلاعات دستگاه و session key (در صورت موجود).
    """
    try:
        # اعتبارسنجی ورودی
        serializer = OTPVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    'error': 'validation_error',
                    'message': 'داده‌های ورودی نامعتبر',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # تأیید OTP
        otp_service = OTPService()
        success, result = otp_service.verify_otp(
            phone_number=serializer.validated_data['phone_number'],
            otp_code=serializer.validated_data['otp_code'],
            purpose=serializer.validated_data['purpose']
        )
        
        if not success:
            return Response(
                {
                    'success': False,
                    'error': result.get('error'),
                    'message': result.get('message'),
                    'details': result
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # OTP تأیید شد
        otp_request = result['otp_request']
        
        # ایجاد یا دریافت کاربر
        user, is_new = AuthService.create_user_if_not_exists(
            phone_number=otp_request.phone_number,
            user_type='patient'  # نوع پیش‌فرض
        )
        
        # تولید توکن‌ها
        tokens = AuthService.generate_tokens(user)
        
        # ایجاد رکورد verification
        verification = AuthService.create_verification_record(
            otp_request=otp_request,
            user=user,
            tokens=tokens,
            device_id=serializer.validated_data.get('device_id'),
            device_name=serializer.validated_data.get('device_name'),
            session_key=request.session.session_key if hasattr(request, 'session') else None
        )
        
        # آماده‌سازی پاسخ
        response_data = {
            'tokens': tokens,
            'user': UserInfoSerializer(user).data,
            'is_new_user': is_new,
            'message': 'ورود موفقیت‌آمیز' if not is_new else 'ثبت‌نام و ورود موفقیت‌آمیز'
        }
        
        return Response(
            {
                'success': True,
                'data': response_data
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error in verify_otp: {str(e)}")
        return Response(
            {
                'success': False,
                'error': 'internal_error',
                'message': 'خطای سیستمی در تأیید کد'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ====================================
# Token Refresh Endpoint
# ====================================

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    تازه‌سازی توکن دسترسی (Access Token) با استفاده از Refresh Token.
    
    این اندپوینت یک Refresh Token در بدنه‌ی درخواست انتظار دارد و در صورت معتبر بودن، یک جفت توکن (یا داده‌ی مرتبط شامل توکن دسترسی جدید) برمی‌گرداند. جریان اصلی:
    - بدنهٔ درخواست باید شامل فیلد `refresh` باشد.
    - ورودی از طریق `RefreshTokenSerializer` اعتبارسنجی می‌شود؛ در صورت نامعتبر بودن، پاسخ 400 با جزئیات خطا بازگردانده می‌شود.
    - پس از اعتبارسنجی، `AuthService.refresh_access_token` برای تولید توکن جدید فراخوانی می‌شود.
    - در صورت موفقیت، پاسخ 200 با ساختار {'success': True, 'data': ...} برگردانده می‌شود.
    - در صورت ناموفق بودن (مثلاً توکن نامعتبر/منقضی)، پاسخ 401 با اطلاعات خطا برگردانده می‌شود.
    - در صورت بروز خطای غیرمنتظره، پاسخ 500 با خطای سیستمی بازگردانده می‌شود.
    
    پارامترهای بدنه (درخواست):
    - refresh: Refresh Token به‌صورت رشته (الزامی)
    
    مقادیر بازگشتی (HTTP):
    - 200: موفق — شامل داده‌های توکن جدید در کلید `data`.
    - 400: بدنهٔ درخواست نامعتبر — شامل جزئیات اعتبارسنجی.
    - 401: Refresh Token نامعتبر یا قابل استفاده نیست.
    - 500: خطای داخلی سرور (خطای غیرمنتظره).
    """
    try:
        # اعتبارسنجی ورودی
        serializer = RefreshTokenSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    'error': 'validation_error',
                    'message': 'داده‌های ورودی نامعتبر',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # تازه‌سازی توکن
        success, result = AuthService.refresh_access_token(
            refresh_token=serializer.validated_data['refresh']
        )
        
        if success:
            return Response(
                {
                    'success': True,
                    'data': result
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    'success': False,
                    'error': result.get('error'),
                    'message': result.get('message')
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
            
    except Exception as e:
        logger.error(f"Error in refresh_token: {str(e)}")
        return Response(
            {
                'success': False,
                'error': 'internal_error',
                'message': 'خطای سیستمی در تازه‌سازی توکن'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ====================================
# Logout Endpoint
# ====================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    خروج کاربر از سیستم با لغو (بلک‌لیست) توکن رفرش یا خروج از همه دستگاه‌ها.
    
    تابع یک درخواست POST دریافت می‌کند که باید شامل توکن رفرش (`refresh`) باشد و در صورت تمایل میدان بولی `logout_all_devices` برای خروج از همه دستگاه‌ها. پس از اعتبارسنجی ورودی، از AuthService.logout برای لغو توکن یا خروج از همه دستگاه‌ها استفاده می‌کند و بر اساس نتیجه پاسخ مناسب با کد وضعیت HTTP برمی‌گرداند.
    
    ورودی (بدنه‌ی درخواست):
        - refresh (str): توکن رفرش که باید لغو شود.
        - logout_all_devices (bool, اختیاری): در صورت True، تمام نشست‌ها/دستگاه‌های کاربر نیز خاتمه داده می‌شوند.
    
    اثرات جانبی:
        - توکن رفرش ارائه‌شده در صورت موفقیت با مکانیزم سرویس احراز هویت بلاک یا منقضی می‌شود.
        - در حالت logout_all_devices=True، ممکن است نشست‌ها/توکن‌های دیگر کاربر نیز با مکانیزم سرویس حذف یا غیرفعال شوند.
    
    خروجی:
        - 200 OK: { "success": True, "message": "..."} در صورت خروج موفق (متن پیام بسته به نوع خروج تغییر می‌کند).
        - 400 Bad Request: { "success": False, "error": "validation_error" | "logout_failed", "message": ..., "details"?: ... } در صورت داده‌های نامعتبر یا شکست عملیات خروج.
        - 500 Internal Server Error: { "success": False, "error": "internal_error", "message": "خطای سیستمی در خروج" } در صورت بروز استثناء داخلی.
    """
    try:
        # اعتبارسنجی ورودی
        serializer = LogoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    'error': 'validation_error',
                    'message': 'داده‌های ورودی نامعتبر',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # خروج
        success = AuthService.logout(
            user=request.user,
            refresh_token=serializer.validated_data['refresh'],
            logout_all=serializer.validated_data.get('logout_all_devices', False)
        )
        
        if success:
            message = 'خروج موفقیت‌آمیز'
            if serializer.validated_data.get('logout_all_devices'):
                message = 'خروج از همه دستگاه‌ها موفقیت‌آمیز'
            
            return Response(
                {
                    'success': True,
                    'message': message
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    'success': False,
                    'error': 'logout_failed',
                    'message': 'خطا در خروج از سیستم'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        logger.error(f"Error in logout: {str(e)}")
        return Response(
            {
                'success': False,
                'error': 'internal_error',
                'message': 'خطای سیستمی در خروج'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )