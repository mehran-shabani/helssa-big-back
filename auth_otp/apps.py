"""
تنظیمات اپلیکیشن احراز هویت OTP
OTP Authentication App Configuration
"""

from django.apps import AppConfig


class AuthOtpConfig(AppConfig):
    """
    پیکربندی اپلیکیشن auth_otp
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_otp'
    verbose_name = 'احراز هویت OTP'
    
    def ready(self):
        """
        اجرای تنظیمات در زمان بارگذاری اپلیکیشن
        """
        # می‌توانید سیگنال‌ها را اینجا import کنید
        # import auth_otp.signals
        pass