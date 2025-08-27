"""
تسک‌های Celery برای auth_otp
Celery Tasks for auth_otp
"""

from celery import shared_task
from django.utils import timezone
import logging

from .services import OTPService, AuthService

logger = logging.getLogger(__name__)


@shared_task(name='auth_otp.tasks.cleanup_expired_otp')
def cleanup_expired_otp():
    """
    پاکسازی و حذف درخواست‌های OTP منقضی شده.
    
    این تسک پس از فراخوانی OTPService.cleanup_expired_otps() تمامی OTPهای منقضی را حذف می‌کند و برای استفاده در اجراهای دوره‌ای (مثلاً از طریق Celery) طراحی شده است. در صورت اجرای موفق، تعداد آیتم‌های حذف‌شده را برمی‌گرداند؛ در صورت بروز خطا، پیام خطا را بازمی‌گرداند. زمان اجرای عملیات در قالب ISO 8601 در خروجی ثبت می‌شود.
    
    Return:
        dict: یک دیکشنری با یکی از ساختارهای زیر:
            - موفق:
                {
                    'status': 'success',
                    'deleted_count': int,            # تعداد رکوردهای حذف‌شده
                    'timestamp': str                 # زمان اجرای عملیات به صورت ISO 8601
                }
            - خطا:
                {
                    'status': 'error',
                    'error': str,                    # پیام خطا
                    'timestamp': str                 # زمان وقوع خطا به صورت ISO 8601
                }
    
    Side effects:
        - فراخوانی متد OTPService.cleanup_expired_otps() که ممکن است رکوردها را از پایگاه‌داده حذف کند.
    """
    try:
        logger.info("Starting OTP cleanup task")
        
        deleted_count = OTPService.cleanup_expired_otps()
        
        logger.info(f"Successfully cleaned up {deleted_count} expired OTP requests")
        
        return {
            'status': 'success',
            'deleted_count': deleted_count,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in OTP cleanup task: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task(name='auth_otp.tasks.cleanup_expired_tokens')
def cleanup_expired_tokens():
    """
    پاکسازی توکن‌های منقضی از لیست سیاه (blacklist).
    
    این تسک پس‌زمینه، رکوردهای توکنِ قرار گرفته در blacklist را که تاریخ انقضای آن‌ها گذشته است حذف می‌کند و تعداد حذف‌شده را بازمی‌گرداند. خروجی تابع یک دیکشنری ساخت‌یافته شامل وضعیت اجرای تسک، شمار توکن‌های حذف‌شده و زمان اجرای عملیات است. در صورت بروز خطا، به‌جای پرتاب استثنا، یک دیکشنری با کلیدهای وضعیت 'error'، پیام خطا و زمان بازگردانده می‌شود.
    
    Returns:
        dict: در حالت موفق:
            {
                'status': 'success',
                'deleted_count': int,         # تعداد توکن‌های حذف‌شده از blacklist
                'timestamp': str             # زمان (ISO 8601) تولید نتیجه
            }
            در حالت خطا:
            {
                'status': 'error',
                'error': str,                # پیام خطای تولیدشده
                'timestamp': str             # زمان (ISO 8601) تولید نتیجه
            }
    """
    try:
        logger.info("Starting token blacklist cleanup task")
        
        deleted_count = AuthService.cleanup_expired_blacklist()
        
        logger.info(f"Successfully cleaned up {deleted_count} expired blacklisted tokens")
        
        return {
            'status': 'success',
            'deleted_count': deleted_count,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in token cleanup task: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task(name='auth_otp.tasks.check_rate_limits')
def check_rate_limits():
    """
    بررسی و به‌روزرسانی پنجره‌های نرخ (rate limits) و گزارش وضعیت تغییرات.
    
    این تسک همهٔ رکوردهای OTPRateLimit را بارگذاری می‌کند، برای هر رکورد متد check_and_update_windows() را اجرا می‌کند، سپس بر اساس مقدارهای minute_count و hour_count شمارش می‌کند که کدام رکوردها در پنجره‌ها ریست یا به‌روزرسانی شده‌اند و همچنین مشخص می‌کند کدام رکوردها از حالت مسدود خارج شده‌اند. هر نمونه پس از بررسی ذخیره می‌شود (side effect: فراخوانی save() روی هر OTPRateLimit). در پایان یک ساختار خلاصه با شمارش‌ها و timestamp بازگردانده می‌شود. در صورت بروز استثنا، یک دیکشنری خطا با پیام و timestamp بازگردانده می‌شود.
    
    Return:
        dict: در صورت موفقیت ساختاری با کلیدهای زیر بازمی‌گرداند:
            - status (str): 'success'
            - total_checked (int): تعداد کل رکوردهای بررسی‌شده
            - updated_count (int): تعداد رکوردهایی که پنجره‌شان ریست یا به‌روزرسانی شده (minute_count یا hour_count برابر 0)
            - unblocked_count (int): تعداد رکوردهایی که از حالت مسدود خارج شده‌اند (is_blocked == False و blocked_until تنظیم شده)
            - timestamp (str): زمان تولید نتیجه به صورت ISO 8601
    
        در صورت خطا:
            - status (str): 'error'
            - error (str): پیام خطا
            - timestamp (str): زمان وقوع خطا به صورت ISO 8601
    """
    try:
        from .models import OTPRateLimit
        
        logger.info("Starting rate limit check task")
        
        # دریافت تمام rate limit ها
        rate_limits = OTPRateLimit.objects.all()
        
        updated_count = 0
        unblocked_count = 0
        
        for rate_limit in rate_limits:
            # بررسی و بروزرسانی پنجره‌های زمانی
            rate_limit.check_and_update_windows()
            
            # شمارش موارد بروزرسانی شده
            if rate_limit.minute_count == 0 or rate_limit.hour_count == 0:
                updated_count += 1
            
            # شمارش موارد رفع مسدودیت
            if not rate_limit.is_blocked and rate_limit.blocked_until:
                unblocked_count += 1
            
            rate_limit.save()
        
        logger.info(
            f"Rate limit check completed: "
            f"{updated_count} updated, {unblocked_count} unblocked"
        )
        
        return {
            'status': 'success',
            'total_checked': rate_limits.count(),
            'updated_count': updated_count,
            'unblocked_count': unblocked_count,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in rate limit check task: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task(name='auth_otp.tasks.send_otp_async')
def send_otp_async(phone_number, purpose='login', sent_via='sms'):
    """
    OTP را به صورت غیرهمزمان ارسال می‌کند و نتیجه را به صورت ساختارمند بازمی‌گرداند.
    
    جزئیات:
    - این تابع درخواست ارسال یک کد یک‌بارمصرف (OTP) را با استفاده از سرویس OTPService انجام می‌دهد و برای اجرا در پس‌زمینه مناسب است.
    - تابع با استفاده از phone_number مقصد را مشخص می‌کند، purpose منظور استفاده یا هدف OTP را تعیین می‌کند (مثلاً 'login') و sent_via کانال ارسال را مشخص می‌کند (معمولاً 'sms' یا 'call').
    - خروجی یک دیکشنری ساختاریافته است که وضعیت عملیات و اطلاعات تکمیلی را شامل می‌شود؛ در حالت بروز استثنا هم خطا گرفته شده و در قالب پاسخ بازگردانده می‌شود.
    - اثری جانبی: درخواست ارسال واقعی OTP را به سرویس ارسال (مثلاً درگاه پیامک/تماس) ارسال می‌کند.
    
    پارامترها:
        phone_number (str): شماره تلفن مقصد، بهتر است در فرمت بین‌المللی قرار داشته باشد.
        purpose (str, optional): هدف استفاده از OTP (پیش‌فرض: 'login').
        sent_via (str, optional): کانال ارسال OTP، مثلاً 'sms' یا 'call' (پیش‌فرض: 'sms').
    
    مقدار بازگشتی:
        dict: دیکشنری با کلیدهای زیر
            - status (str): یکی از 'success' (ارسال موفق)، 'failed' (ارسال ناموفق اما پردازش بدون استثنا)، یا 'error' (خطای غیرمنتظره و ثبت‌شده).
            - result (any): مقدار بازگشتی یا پیام خطای سرویس در صورت وضعیت 'success' یا 'failed'.
            - error (str, optional): متن خطا در صورت وقوع استثنای داخلی (فقط زمانی که status == 'error' موجود است).
            - timestamp (str): زمان ایجاد نتیجه به صورت ISO 8601.
    
    توضیحات اضافی:
    - تابع خود استثناها را گرفته و آن‌ها را به صورت مقدار بازگشتی گزارش می‌کند؛ بنابراین هیچ استثنای بیرونی پرتاب نمی‌شود.
    """
    try:
        from .services import OTPService
        
        logger.info(f"Sending OTP asynchronously to {phone_number}")
        
        otp_service = OTPService()
        success, result = otp_service.send_otp(
            phone_number=phone_number,
            purpose=purpose,
            sent_via=sent_via
        )
        
        if success:
            logger.info(f"OTP sent successfully to {phone_number}")
        else:
            logger.error(f"Failed to send OTP to {phone_number}: {result}")
        
        return {
            'status': 'success' if success else 'failed',
            'result': result,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in async OTP send: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task(name='auth_otp.tasks.generate_otp_report')
def generate_otp_report(start_date=None, end_date=None):
    """
    تولید گزارش خلاصهٔ استفاده و وضعیت درخواست‌ها و تأییدیه‌های OTP در یک بازهٔ زمانی مشخص.
    
    این تابع آمارهایی را از مدل‌های OTPRequest و OTPVerification استخراج می‌کند و گزارشی شامل تعداد کل درخواست‌ها، درخواست‌های استفاده‌شده، تعداد ارسال‌ها برحسب روش (sms/call)، آمار تأییدها، تفکیک بر اساس `purpose` و نرخ موفقیت (درصد درخواست‌های استفاده‌شده نسبت به کل) تولید می‌کند. در صورت عدم تعیین، بازهٔ پیش‌فرض انتهای آن برابر زمان فعلی و شروع آن هفت روز قبل است. تابع خروجی‌ای از نوع dict برمی‌گرداند که در صورت موفقیت شامل کلیدهای `period`, `otp_stats`, `verification_stats`, `purpose_breakdown`, `success_rate`, و `generated_at` است؛ در صورت خطا دیکشنری‌ای با `status: 'error'`, `error` و `timestamp` بازگردانده می‌شود.
    
    Parameters:
        start_date (datetime.datetime | None): زمان شروع بازهٔ گزارش. اگر None باشد، به‌صورت پیش‌فرض برابر با end_date - 7 روز قرار می‌گیرد.
        end_date (datetime.datetime | None): زمان پایان بازهٔ گزارش. اگر None باشد، به‌صورت پیش‌فرض برابر با زمان فعلی (timezone.now()) قرار می‌گیرد.
    
    Returns:
        dict: در حالت موفقیت، دیکشنری گزارش شامل:
            - period: {'start': ISO8601, 'end': ISO8601}
            - otp_stats: مجموع شمارش‌ها (total_requests, used_requests, sms_requests, call_requests)
            - verification_stats: شمارش‌های تأیید (total_verifications, active_sessions)
            - purpose_breakdown: لیستی از شمارش‌ها گروه‌بندی‌شده بر اساس `purpose`
            - success_rate: درصد استفاده‌شدگی OTP (عدد بین 0 تا 100)
            - generated_at: timestamp تولید گزارش (ISO8601)
        در صورت خطا، دیکشنری شامل:
            - status: 'error'
            - error: پیام خطا
            - timestamp: زمان وقوع خطا (ISO8601)
    """
    try:
        from .models import OTPRequest, OTPVerification
        from django.db.models import Count, Q
        from datetime import timedelta
        
        logger.info("Generating OTP usage report")
        
        # تعیین بازه زمانی
        if not end_date:
            end_date = timezone.now()
        if not start_date:
            start_date = end_date - timedelta(days=7)
        
        # آمار درخواست‌های OTP
        otp_stats = OTPRequest.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).aggregate(
            total_requests=Count('id'),
            used_requests=Count('id', filter=Q(is_used=True)),
            sms_requests=Count('id', filter=Q(sent_via='sms')),
            call_requests=Count('id', filter=Q(sent_via='call')),
        )
        
        # آمار تأییدیه‌ها
        verification_stats = OTPVerification.objects.filter(
            verified_at__gte=start_date,
            verified_at__lte=end_date
        ).aggregate(
            total_verifications=Count('id'),
            active_sessions=Count('id', filter=Q(is_active=True)),
        )
        
        # آمار بر اساس purpose
        purpose_stats = OTPRequest.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).values('purpose').annotate(count=Count('id'))
        
        report = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'otp_stats': otp_stats,
            'verification_stats': verification_stats,
            'purpose_breakdown': list(purpose_stats),
            'success_rate': (
                (otp_stats['used_requests'] / otp_stats['total_requests'] * 100)
                if otp_stats['total_requests'] > 0 else 0
            ),
            'generated_at': timezone.now().isoformat()
        }
        
        logger.info(f"OTP report generated successfully: {report}")
        
        return report
        
    except Exception as e:
        logger.error(f"Error generating OTP report: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }