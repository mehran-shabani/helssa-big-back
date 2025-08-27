"""
ویوهای تکمیلی سیستم احراز هویت OTP
Extended OTP Authentication Views
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
import logging

from .serializers import (
    OTPStatusSerializer,
    RateLimitStatusSerializer,
    RegisterSerializer,
    UserInfoSerializer
)
from .services import OTPService, AuthService
from .models import OTPRequest, OTPRateLimit
from .services.kavenegar_service import KavenegarService

logger = logging.getLogger(__name__)


# ====================================
# OTP Status Endpoint
# ====================================

@api_view(['GET'])
@permission_classes([AllowAny])
def otp_status(request, otp_id):
    """
    دریافت وضعیت OTP
    
    Path Parameters:
        - otp_id: شناسه OTP
        
    Returns:
        200: وضعیت OTP
        404: OTP یافت نشد
    """
    try:
        otp_request = OTPRequest.objects.filter(id=otp_id).first()
        
        if not otp_request:
            return Response(
                {
                    'error': 'not_found',
                    'message': 'OTP یافت نشد'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = OTPStatusSerializer(otp_request)
        
        return Response(
            {
                'success': True,
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error in otp_status: {str(e)}")
        return Response(
            {
                'success': False,
                'error': 'internal_error',
                'message': 'خطای سیستمی'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ====================================
# Rate Limit Status Endpoint
# ====================================

@api_view(['GET'])
@permission_classes([AllowAny])
def rate_limit_status(request, phone_number):
    """
    دریافت وضعیت محدودیت نرخ برای شماره
    
    Path Parameters:
        - phone_number: شماره موبایل
        
    Returns:
        200: وضعیت محدودیت
    """
    try:
        # بررسی فرمت شماره
        formatted_phone = KavenegarService.format_phone_number(phone_number)
        
        # دریافت rate limit
        rate_limit, created = OTPRateLimit.objects.get_or_create(
            phone_number=formatted_phone
        )
        
        # بررسی وضعیت
        rate_limit.check_and_update_windows()
        can_send, message = rate_limit.can_send_otp()
        
        data = {
            'can_send': can_send,
            'message': message,
            'minute_limit': 1,
            'minute_remaining': max(0, 1 - rate_limit.minute_count),
            'hour_limit': 5,
            'hour_remaining': max(0, 5 - rate_limit.hour_count),
            'is_blocked': rate_limit.is_blocked,
            'blocked_until': rate_limit.blocked_until
        }
        
        serializer = RateLimitStatusSerializer(data)
        
        return Response(
            {
                'success': True,
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error in rate_limit_status: {str(e)}")
        return Response(
            {
                'success': False,
                'error': 'internal_error',
                'message': 'خطای سیستمی'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ====================================
# User Sessions Endpoint
# ====================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_sessions(request):
    """
    دریافت نشست‌های فعال کاربر
    
    Returns:
        200: لیست نشست‌ها
    """
    try:
        sessions = AuthService.get_active_sessions(request.user)
        
        return Response(
            {
                'success': True,
                'data': {
                    'sessions': sessions,
                    'count': len(sessions)
                }
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error in user_sessions: {str(e)}")
        return Response(
            {
                'success': False,
                'error': 'internal_error',
                'message': 'خطای سیستمی'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ====================================
# Revoke Session Endpoint
# ====================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def revoke_session(request, session_id):
    """
    لغو یک نشست خاص
    
    Path Parameters:
        - session_id: شناسه نشست
        
    Returns:
        200: نشست لغو شد
        404: نشست یافت نشد
    """
    try:
        success = AuthService.revoke_session(request.user, session_id)
        
        if success:
            return Response(
                {
                    'success': True,
                    'message': 'نشست با موفقیت لغو شد'
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    'success': False,
                    'error': 'not_found',
                    'message': 'نشست یافت نشد یا قبلاً لغو شده'
                },
                status=status.HTTP_404_NOT_FOUND
            )
            
    except Exception as e:
        logger.error(f"Error in revoke_session: {str(e)}")
        return Response(
            {
                'success': False,
                'error': 'internal_error',
                'message': 'خطای سیستمی'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ====================================
# Register Endpoint (Optional)
# ====================================

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    ثبت‌نام کاربر جدید (بعد از تأیید OTP)
    
    Request Body:
        - phone_number: شماره موبایل (الزامی)
        - user_type: نوع کاربر (patient/doctor)
        - first_name: نام
        - last_name: نام خانوادگی
        - email: ایمیل
        
    Returns:
        201: ثبت‌نام موفق
        400: خطای اعتبارسنجی
    """
    try:
        # این endpoint فقط برای کاربرانی که OTP تأیید کرده‌اند
        # می‌توانید از session یا token موقت برای بررسی استفاده کنید
        
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    'error': 'validation_error',
                    'message': 'داده‌های ورودی نامعتبر',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ایجاد کاربر
        user = serializer.save()
        
        return Response(
            {
                'success': True,
                'data': UserInfoSerializer(user).data,
                'message': 'ثبت‌نام با موفقیت انجام شد'
            },
            status=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        logger.error(f"Error in register: {str(e)}")
        return Response(
            {
                'success': False,
                'error': 'internal_error',
                'message': 'خطای سیستمی در ثبت‌نام'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ====================================
# Resend OTP Endpoint
# ====================================

@api_view(['POST'])
@permission_classes([AllowAny])
def resend_otp(request):
    """
    ارسال مجدد کد OTP
    
    Request Body:
        - phone_number: شماره موبایل (الزامی)
        - purpose: هدف (login/register/reset_password/verify_phone)
        - sent_via: روش ارسال (sms/call)
        
    Returns:
        201: OTP ارسال شد
        400: خطای اعتبارسنجی
        429: محدودیت نرخ
        500: خطای سرور
    """
    # از همان send_otp استفاده می‌کنیم
    from .views import send_otp as send_otp_view
    return send_otp_view(request)