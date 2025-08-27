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
    پاکسازی OTP های منقضی شده
    
    این تسک به صورت دوره‌ای اجرا می‌شود و OTP های قدیمی را حذف می‌کند
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
    پاکسازی توکن‌های منقضی از blacklist
    
    این تسک توکن‌هایی که زمان انقضایشان گذشته را از blacklist حذف می‌کند
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
    بررسی و بروزرسانی محدودیت‌های نرخ
    
    این تسک محدودیت‌های نرخ را بررسی و در صورت نیاز ریست می‌کند
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
    ارسال OTP به صورت غیرهمزمان
    
    برای موارد خاص که نیاز به ارسال در background دارید
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
    تولید گزارش استفاده از OTP
    
    این تسک آمار استفاده از سیستم OTP را تولید می‌کند
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