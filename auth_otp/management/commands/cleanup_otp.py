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
        """
        افزودن آرگومان‌های خط فرمان برای فرمان مدیریت.
        
        این متد دو گزینه را ثبت می‌کند:
        - `--dry-run` (فلگ): اجرای شبیه‌سازی که فقط تعداد رکوردهای قابل حذف را نمایش می‌دهد بدون اینکه حذف واقعی انجام شود.
        - `--otp-age-hours` (عدد صحیح، پیش‌فرض 24): حداقل سن (بر حسب ساعت) برای درخواست‌های OTP که به‌عنوان منقضی در نظر گرفته شده و واجد حذف هستند.
        """
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
        """
        اجرای فرمان پاکسازی OTPها و توکن‌های بلک‌لیست.
        
        این متد ورودی‌های CLI را خوانده و فرایند پاکسازی را اجرا یا شبیه‌سازی می‌کند:
        - اگر گزینه `dry_run` فعال باشد، حذف‌ها شبیه‌سازی شده و فقط شمار آیتم‌هایی که حذف می‌شدند گزارش می‌شوند.
        - در غیر این صورت، حذف واقعی با فراخوانی متدهای داخلی `_cleanup_otps` و `_cleanup_tokens` انجام می‌شود.
        
        پارامترهای options (مهم‌ترین کلیدها):
        - dry_run: اگر True باشد، عملیات در حالت شبیه‌سازی اجرا می‌شود و هیچ داده‌ای حذف نمی‌شود.
        - otp_age_hours: آستانه سنی (به ساعت) برای تعیین OTPهای قدیمی که باید در پاکسازی مدنظر قرار گیرند.
        
        اثرات جانبی:
        - پیغام‌های وضعیت و خلاصهٔ عملیات را به خروجی استاندارد مدیریت فرمان می‌نویسد.
        - بسته به مقدار `dry_run` ممکن است رکوردهایی از پایگاه داده حذف شوند (از طریق `_cleanup_otps` و `_cleanup_tokens`).
        """
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
        """
        یک‌خطی: پاک‌سازی یا شمارش OTPهای منقضی شده بر اساس سن مشخص.
        
        توضیحات:
        این متد یا شمار OTPهای قدیمی‌تر از بازهٔ مشخص‌شده را برمی‌شمارد (حالت dry-run)
        یا عملیات حذف واقعی را اجرا می‌کند و تعداد رکوردهای حذف‌شده را بازمی‌گرداند.
        در حالت dry-run از مدل OTPRequest به‌صورت محلی ایمپورت شده و شمارش با استفاده از فیلتر created_at انجام می‌شود تا از وارد شدن تغییر واقعی در داده‌ها جلوگیری گردد.
        در حالت واقعی، حذف با استفاده از OTPService.cleanup_expired_otps() انجام می‌شود.
        
        Parameters:
            dry_run (bool): اگر True باشد، حذف انجام نمی‌شود و فقط تعداد OTPهای واجد شرایط برگردانده می‌شود.
            age_hours (int): آستانهٔ سنی به ساعت؛ تمام OTPهایی که مقدار created_at آنها از اکنون بیشتر از این تعداد ساعت قدیمی‌تر است، واجد حذف/شمارش در نظر گرفته می‌شوند.
        
        Returns:
            int: تعداد OTPهای شمرده‌شده (در dry-run) یا تعداد OTPهای حذف‌شده (در اجرای واقعی).
        """
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
        """
        یک‌خطی:
        توکن‌های منقضی‌شده را از لیست سیاه شمارش یا حذف می‌کند.
        
        توضیح جزئی:
        اگر dry_run True باشد، تعداد رکوردهای TokenBlacklist با expires_at کمتر از زمان فعلی (timezone-aware) را شمارش و برمی‌گرداند بدون اینکه حذف واقعی انجام دهد. اگر dry_run False باشد، پاک‌سازی واقعی را با فراخوانی AuthService.cleanup_expired_blacklist() انجام می‌دهد و تعداد توکن‌های حذف‌شده را برمی‌گرداند. در هر حالت، خلاصه‌ای از نتیجه به stdout نوشته می‌شود.
        
        Parameters:
            dry_run (bool): اگر True باشد عملیات شبیه‌سازی می‌شود (فقط شمارش، بدون حذف).
        
        Returns:
            int: تعداد توکن‌هایی که شناسایی شده‌اند (در حالت dry-run تعداد قابل حذف، در حالت واقعی تعداد حذف‌شده).
        """
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