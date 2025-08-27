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
    ارسال کد OTP به شماره موبایل
    
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
    تأیید کد OTP و ورود/ثبت‌نام
    
    Request Body:
        - phone_number: شماره موبایل (الزامی)
        - otp_code: کد 6 رقمی (الزامی)
        - purpose: هدف (login/register)
        - device_id: شناسه دستگاه
        - device_name: نام دستگاه
        
    Returns:
        200: ورود موفق
        400: کد نامعتبر
        404: OTP یافت نشد
        500: خطای سرور
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
    تازه‌سازی Access Token
    
    Request Body:
        - refresh: Refresh Token (الزامی)
        
    Returns:
        200: توکن جدید
        401: توکن نامعتبر
        500: خطای سرور
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
    خروج از سیستم
    
    Request Body:
        - refresh: Refresh Token برای مسدود کردن
        - logout_all_devices: خروج از همه دستگاه‌ها (اختیاری)
        
    Returns:
        200: خروج موفق
        400: خطای ورودی
        500: خطای سرور
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