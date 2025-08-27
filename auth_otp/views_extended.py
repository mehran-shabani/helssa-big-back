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
    یکبار-رمز (OTP) مشخص را بر اساس شناسه بازیابی و وضعیت آن را بازمی‌گرداند.
    
    تابع شناسه OTP را از پارامتر مسیر دریافت می‌کند و تلاش می‌کند رکورد متناظر در مدل OTPRequest را بازیابی کند. اگر رکورد موجود باشد، آن را با OTPStatusSerializer سریالایز کرده و در بدنه پاسخ با کلید `data` بازمی‌گرداند؛ در غیر این صورت پاسخ 404 با خطای `not_found` برمی‌گردد. در صورت بروز هرگونه خطای داخلی، پاسخ 500 با شناسه خطای `internal_error` بازگردانده می‌شود.
    
    Parameters:
        otp_id: شناسه مسیر (path parameter) مربوط به درخواست OTP که برای یافتن رکورد در مدل OTPRequest استفاده می‌شود.
    
    Returns:
        Response حاوی:
          - 200: {'success': True, 'data': <serialized OTP status>} وقتی رکورد پیدا و سریالایز شده باشد.
          - 404: {'error': 'not_found', 'message': 'OTP یافت نشد'} وقتی رکوردی با آن شناسه وجود نداشته باشد.
          - 500: {'success': False, 'error': 'internal_error', 'message': 'خطای سیستمی'} در صورت بروز خطای داخلی.
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
@permission_classes([IsAuthenticated])
def rate_limit_status(request, phone_number):
    """
    وضعیت محدودیت نرخ (rate limit) برای ارسال OTP برای یک شمارهٔ موبایل را برمی‌گرداند.
    
    این تابع وضعیت فعلی محدودیت ارسال OTP را برای شمارهٔ مسیر (path) مشخص‌شده محاسبه می‌کند: شماره را با KavenegarService قالب‌بندی می‌کند، رکورد OTPRateLimit مربوطه را ایجاد یا بازیابی می‌کند، پنجره‌های زمانی (`minute`/`hour`) را بررسی و به‌روز می‌کند و مشخص می‌کند آیا در حال حاضر ارسال OTP امکان‌پذیر است یا خیر. در پاسخ یک شیء داده شامل میزان مجازِ ارسال و باقیمانده‌ها و وضعیت بلوک شدن بازگردانده می‌شود.
    
    پارامترها:
        phone_number (str): شمارهٔ موبایل مورد پرس‌وجو؛ ورودی مسیر (path). تابع شماره را با KavenegarService.format_phone_number پیش‌پردازش می‌کند، بنابراین ورودی می‌تواند در فرمت‌های معمول پیش از قالب‌بندی باشد.
    
    رفتار جانبی:
        - در صورت عدم وجود، یک رکورد OTPRateLimit جدید برای شماره ایجاد می‌شود.
        - وضعیت داخلی آن رکورد (شمارش‌های دقیقه/ساعت و وضعیت بلوک) ممکن است توسط check_and_update_windows() به‌روز شود.
    
    مقدار بازگشتی:
        - در حالت موفق (HTTP 200): پاسخ JSON با کلیدهای زیر در فیلد `data`:
            - can_send (bool): آیا می‌توان اکنون OTP ارسال کرد.
            - message (str): پیام توصیفی کوتاه در مورد وضعیت ارسال.
            - minute_limit (int): حد ارسال در هر دقیقه (مثلاً 1).
            - minute_remaining (int): تعداد مجاز باقیمانده در بازهٔ دقیقه جاری.
            - hour_limit (int): حد ارسال در هر ساعت (مثلاً 5).
            - hour_remaining (int): تعداد مجاز باقیمانده در بازهٔ ساعت جاری.
            - is_blocked (bool): آیا شماره فعلاً بلاک شده است.
            - blocked_until (datetime|None): زمان رفع بلاک در صورت بلاک بودن، یا None.
        - در خطاهای داخلی (HTTP 500): پاسخ JSON حاوی خطای `internal_error` و پیام کوتاه «خطای سیستمی».
    
    توجه:
        - مقادیر `minute_limit` و `hour_limit` در پاسخ بر اساس منطق فعلی کد ثابت (1 و 5) بازگردانده می‌شوند.
        - این تابع استثناها را می‌گیرد و در صورت بروز هر خطای غیرمنتظره، پاسخ 500 بازمی‌گرداند؛ استثناهای خاصی به صورت جداگانه پرتاب نمی‌شوند.
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
    بازگرداندن نشست‌های فعال کاربر احرازشده.
    
    این نما لیستی از نشست‌های فعال کاربر جاری را با استفاده از AuthService.get_active_sessions تهیه می‌کند و پاسخ JSON شامل فیلدهای زیر را برمی‌گرداند:
    - success (bool): نشان‌دهنده موفقیت درخواست.
    - data (dict):
        - sessions (list): چکیده/ساختار نشست‌ها همان‌طور که توسط AuthService بازگردانده می‌شود.
        - count (int): تعداد نشست‌های بازگردانده‌شده.
    
    وضعیت‌های HTTP:
    - 200: عملیات موفق و برگشت داده‌های نشست.
    - 500: خطای داخلی سرور در صورت بروز استثنا.
    
    توجه: این نما برای کاربر احرازشده در نظر گرفته شده و از درخواست جاری (request.user) استفاده می‌کند.
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
    لغو یک نشست کاربری مشخص برای درخواست‌دهنده (کاربر احراز هویت‌شده).
    
    این تابع تلاش می‌کند نشست با شناسه‌ی داده‌شده را برای کاربر جاری (request.user) از طریق AuthService لغو کند.
    - اگر عملیات موفق باشد، پاسخ 200 با فیلد `success: True` و پیام تأیید برمی‌گرداند.
    - اگر نشست یافت نشود یا قبلاً لغو شده باشد، پاسخ 404 با `error: "not_found"` و پیام مناسب برمی‌گرداند.
    - در صورت بروز هرگونه خطای داخلی، پاسخ 500 با `error: "internal_error"` و پیام عمومی خطای سیستمی برمی‌گردد.
    
    Parameters:
        session_id (str): شناسهٔ نشست که قرار است لغو شود (معمولاً UUID یا شناسهٔ رشته‌ای).
    
    Returns:
        rest_framework.response.Response: پاسخ HTTP حاوی وضعیت عملیات:
            - 200: نشست با موفقیت لغو شد.
            - 404: نشست یافت نشد یا قبلاً لغو شده.
            - 500: خطای داخلی سرور.
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
    ثبت‌نام کاربر جدید پس از تأیید OTP و ایجاد حساب کاربری.
    
    این تابع ورودی را از بدنهٔ درخواست با استفاده از RegisterSerializer اعتبارسنجی می‌کند و در صورت اعتبارسنجی موفق کاربر جدید را ایجاد می‌نماید.
    
    بایدهای بدنهٔ درخواست:
    - phone_number (str, الزامی): شماره موبایل معتبر که قبلاً با OTP تأیید شده است.
    - user_type (str, الزامی): نوع کاربر، مثلاً "patient" یا "doctor".
    - first_name (str, اختیاری): نام کوچک کاربر.
    - last_name (str, اختیاری): نام خانوادگی کاربر.
    - email (str, اختیاری): ایمیل کاربر.
    
    رفتار و پاسخ‌ها:
    - اگر داده‌ها نامعتبر باشند: پاسخ 400 با ساختار {'error': 'validation_error', 'message': 'داده‌های ورودی نامعتبر', 'details': <خطاهای serializer>} برمی‌گردد.
    - در صورت موفقیت: پاسخ 201 با ساختار {'success': True, 'data': <اطلاعات کاربر از UserInfoSerializer>, 'message': 'ثبت‌نام با موفقیت انجام شد'} برمی‌گردد.
    - در صورت خطای غیرمنتظره: پاسخ 500 با {'success': False, 'error': 'internal_error', 'message': 'خطای سیستمی در ثبت‌نام'} برمی‌گردد.
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
    فراخوانی مجددِ ارسال کد OTP؛ این نما صرفاً درخواست را به تابع موجود `send_otp` ارجاع می‌دهد و همان رفتار، اعتبارسنجی و پاسخ‌ها را بازمی‌گرداند.
    
    توضیحات:
    - این تابع هیچ منطق جدیدی پیاده‌سازی نمی‌کند و به‌عنوان یک شِمِه (forwarder) عمل می‌کند تا endpoint مجدد ارسال OTP را با همان پیاده‌سازی موجود فراهم کند.
    - عمل واقعی ارسال (SMS/تماس)، بررسی محدودیت نرخ، اعتبارسنجی ورودی و ثبت رخدادها توسط `send_otp` انجام می‌شود؛ بنابراین هر تأثیر جانبی (ارسال پیام، ایجاد رکورد OTP، افزایش شمارش نرخ) توسط آن تابع است.
    
    بدنه درخواست (JSON):
    - phone_number (رشته، الزامی): شماره موبایل مقصد (فرمت باید توسط سرویس قالب‌بندی شماره مدیریت شود).
    - purpose (رشته، اختیاری): هدف استفاده از OTP، مثلاً "login", "register", "reset_password", "verify_phone".
    - sent_via (رشته، اختیاری): روش ارسال، معمولاً "sms" یا "call".
    
    نتایج متداول HTTP:
    - 201 Created: OTP با موفقیت ارسال شد (یا فرایند ارسال آغاز شد).
    - 400 Bad Request: خطای اعتبارسنجی ورودی — جزئیات در پاسخ بازگردانده می‌شود.
    - 429 Too Many Requests: درخواست به‌دلیل محدودیت نرخ رد شده است.
    - 500 Internal Server Error: خطای سیستمی هنگام پردازش.
    
    نکته‌ها:
    - هرگونه تغییر در رفتار، پیام‌ها یا قوانین نرخ باید در تابع `send_otp` اعمال شود چون این نما صرفاً درخواست را به آن منتقل می‌کند.
    """
    # از همان send_otp استفاده می‌کنیم
    from .views import send_otp as send_otp_view
    return send_otp_view(request)