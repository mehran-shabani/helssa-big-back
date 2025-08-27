"""
دستور مدیریت برای پاکسازی داده‌های منقضی OTP
Management Command for Cleaning Up Expired OTP Data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import logging

from auth_otp.services import OTPService, AuthService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    پاکسازی OTP ها و توکن‌های منقضی شده
    
    استفاده:
        python manage.py cleanup_otp
        python manage.py cleanup_otp --dry-run
    """
    help = 'پاکسازی OTP ها و توکن‌های منقضی شده'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='نمایش تعداد رکوردهای قابل حذف بدون انجام عملیات',
        )
        
        parser.add_argument(
            '--otp-age-hours',
            type=int,
            default=24,
            help='حداقل سن OTP برای حذف (به ساعت)',
        )
    
    def handle(self, *args, **options):
        """اجرای دستور"""
        dry_run = options['dry_run']
        otp_age_hours = options['otp_age_hours']
        
        self.stdout.write(
            self.style.SUCCESS('شروع پاکسازی داده‌های منقضی...')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('حالت Dry Run - هیچ داده‌ای حذف نخواهد شد')
            )
        
        # پاکسازی OTP های قدیمی
        otp_count = self._cleanup_otps(dry_run, otp_age_hours)
        
        # پاکسازی توکن‌های منقضی از blacklist
        token_count = self._cleanup_tokens(dry_run)
        
        # نمایش خلاصه
        self.stdout.write(
            self.style.SUCCESS(
                f'\nخلاصه پاکسازی:\n'
                f'- OTP های حذف شده: {otp_count}\n'
                f'- توکن‌های حذف شده از blacklist: {token_count}'
            )
        )
    
    def _cleanup_otps(self, dry_run, age_hours):
        """پاکسازی OTP های قدیمی"""
        if dry_run:
            from auth_otp.models import OTPRequest
            cutoff = timezone.now() - timedelta(hours=age_hours)
            count = OTPRequest.objects.filter(created_at__lt=cutoff).count()
            self.stdout.write(
                f'تعداد OTP های قابل حذف (قدیمی‌تر از {age_hours} ساعت): {count}'
            )
            return count
        else:
            count = OTPService.cleanup_expired_otps()
            self.stdout.write(
                self.style.SUCCESS(f'{count} OTP قدیمی حذف شد')
            )
            return count
    
    def _cleanup_tokens(self, dry_run):
        """پاکسازی توکن‌های منقضی"""
        if dry_run:
            from auth_otp.models import TokenBlacklist
            count = TokenBlacklist.objects.filter(
                expires_at__lt=timezone.now()
            ).count()
            self.stdout.write(
                f'تعداد توکن‌های منقضی در blacklist: {count}'
            )
            return count
        else:
            count = AuthService.cleanup_expired_blacklist()
            self.stdout.write(
                self.style.SUCCESS(f'{count} توکن منقضی از blacklist حذف شد')
            )
            return count