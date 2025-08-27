"""
مدل‌های سیستم احراز هویت OTP
OTP Authentication System Models
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import RegexValidator
from datetime import timedelta
import secrets
import uuid

User = get_user_model()


class OTPRequest(models.Model):
    """
    درخواست‌های OTP ارسال شده
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    phone_number = models.CharField(
        max_length=11,
        validators=[RegexValidator(r'^09\d{9}$', 'شماره موبایل باید با 09 شروع شود و 11 رقم باشد')],
        verbose_name='شماره موبایل',
        db_index=True
    )
    
    otp_code = models.CharField(
        max_length=6,
        verbose_name='کد OTP'
    )
    
    purpose = models.CharField(
        max_length=20,
        choices=[
            ('login', 'ورود'),
            ('register', 'ثبت‌نام'),
            ('reset_password', 'بازیابی رمز عبور'),
            ('verify_phone', 'تأیید شماره تلفن'),
        ],
        default='login',
        verbose_name='هدف'
    )
    
    is_used = models.BooleanField(
        default=False,
        verbose_name='استفاده شده'
    )
    
    attempts = models.IntegerField(
        default=0,
        verbose_name='تعداد تلاش'
    )
    
    expires_at = models.DateTimeField(
        verbose_name='زمان انقضا'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='زمان ایجاد'
    )
    
    # اطلاعات ارسال
    sent_via = models.CharField(
        max_length=20,
        choices=[
            ('sms', 'پیامک'),
            ('call', 'تماس صوتی'),
        ],
        default='sms',
        verbose_name='روش ارسال'
    )
    
    kavenegar_message_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='شناسه پیام کاوه‌نگار'
    )
    
    # IP و User Agent برای امنیت
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='آدرس IP'
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent'
    )
    
    # متادیتا
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='اطلاعات اضافی'
    )
    
    class Meta:
        verbose_name = 'درخواست OTP'
        verbose_name_plural = 'درخواست‌های OTP'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone_number', 'created_at']),
            models.Index(fields=['otp_code', 'is_used']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"OTP {self.phone_number} - {self.purpose}"
    
    def save(self, *args, **kwargs):
        if not self.otp_code:
            self.otp_code = self.generate_otp_code()
        
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=3)
        
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_otp_code():
        """تولید کد OTP 6 رقمی"""
        return f"{secrets.randbelow(900000) + 100000:06d}"
    
    @property
    def is_expired(self):
        """بررسی انقضای OTP"""
        return timezone.now() > self.expires_at
    
    @property
    def can_verify(self):
        """آیا امکان تأیید وجود دارد"""
        return not self.is_used and not self.is_expired and self.attempts < 3
    
    def increment_attempts(self):
        """افزایش تعداد تلاش"""
        self.attempts += 1
        self.save(update_fields=['attempts'])
    
    def mark_as_used(self):
        """علامت‌گذاری به عنوان استفاده شده"""
        self.is_used = True
        self.save(update_fields=['is_used'])


class OTPVerification(models.Model):
    """
    تأییدیه‌های OTP موفق
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    otp_request = models.OneToOneField(
        OTPRequest,
        on_delete=models.CASCADE,
        related_name='verification',
        verbose_name='درخواست OTP'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='otp_verifications',
        verbose_name='کاربر'
    )
    
    verified_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='زمان تأیید'
    )
    
    # توکن‌های صادر شده
    access_token = models.TextField(
        verbose_name='Access Token'
    )
    
    refresh_token = models.TextField(
        verbose_name='Refresh Token'
    )
    
    # اطلاعات دستگاه
    device_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='شناسه دستگاه'
    )
    
    device_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='نام دستگاه'
    )
    
    # Session tracking
    session_key = models.CharField(
        max_length=40,
        blank=True,
        verbose_name='کلید نشست'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
    )
    
    class Meta:
        verbose_name = 'تأییدیه OTP'
        verbose_name_plural = 'تأییدیه‌های OTP'
        ordering = ['-verified_at']
    
    def __str__(self):
        return f"Verification {self.otp_request.phone_number} - {self.verified_at}"
    
    def deactivate(self):
        """غیرفعال کردن تأییدیه"""
        self.is_active = False
        self.save(update_fields=['is_active'])


class OTPRateLimit(models.Model):
    """
    محدودیت‌های نرخ ارسال OTP
    """
    phone_number = models.CharField(
        max_length=11,
        unique=True,
        validators=[RegexValidator(r'^09\d{9}$')],
        verbose_name='شماره موبایل'
    )
    
    # شمارنده‌ها
    minute_count = models.IntegerField(
        default=0,
        verbose_name='تعداد در دقیقه'
    )
    
    hour_count = models.IntegerField(
        default=0,
        verbose_name='تعداد در ساعت'
    )
    
    daily_count = models.IntegerField(
        default=0,
        verbose_name='تعداد روزانه'
    )
    
    # زمان‌های آخرین بروزرسانی
    minute_window_start = models.DateTimeField(
        default=timezone.now,
        verbose_name='شروع پنجره دقیقه'
    )
    
    hour_window_start = models.DateTimeField(
        default=timezone.now,
        verbose_name='شروع پنجره ساعت'
    )
    
    daily_window_start = models.DateTimeField(
        default=timezone.now,
        verbose_name='شروع پنجره روز'
    )
    
    # مسدودسازی
    is_blocked = models.BooleanField(
        default=False,
        verbose_name='مسدود شده'
    )
    
    blocked_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='مسدود تا'
    )
    
    failed_attempts = models.IntegerField(
        default=0,
        verbose_name='تلاش‌های ناموفق'
    )
    
    last_request = models.DateTimeField(
        auto_now=True,
        verbose_name='آخرین درخواست'
    )
    
    class Meta:
        verbose_name = 'محدودیت نرخ OTP'
        verbose_name_plural = 'محدودیت‌های نرخ OTP'
        indexes = [
            models.Index(fields=['phone_number', 'is_blocked']),
        ]
    
    def __str__(self):
        return f"Rate Limit {self.phone_number}"
    
    def reset_minute_window(self):
        """ریست پنجره دقیقه"""
        self.minute_count = 0
        self.minute_window_start = timezone.now()
    
    def reset_hour_window(self):
        """ریست پنجره ساعت"""
        self.hour_count = 0
        self.hour_window_start = timezone.now()
    
    def reset_daily_window(self):
        """ریست پنجره روز"""
        self.daily_count = 0
        self.daily_window_start = timezone.now()
    
    def check_and_update_windows(self):
        """بررسی و بروزرسانی پنجره‌های زمانی"""
        now = timezone.now()
        
        # بررسی پنجره دقیقه
        if now - self.minute_window_start > timedelta(minutes=1):
            self.reset_minute_window()
        
        # بررسی پنجره ساعت
        if now - self.hour_window_start > timedelta(hours=1):
            self.reset_hour_window()
        
        # بررسی پنجره روز
        if now - self.daily_window_start > timedelta(days=1):
            self.reset_daily_window()
        
        # بررسی مسدودیت
        if self.is_blocked and self.blocked_until and now > self.blocked_until:
            self.is_blocked = False
            self.blocked_until = None
            self.failed_attempts = 0
    
    def can_send_otp(self):
        """آیا امکان ارسال OTP وجود دارد"""
        self.check_and_update_windows()
        
        if self.is_blocked:
            return False, f"شماره شما تا {self.blocked_until} مسدود است"
        
        if self.minute_count >= 1:
            return False, "حداکثر 1 درخواست در دقیقه مجاز است"
        
        if self.hour_count >= 5:
            return False, "حداکثر 5 درخواست در ساعت مجاز است"
        
        if self.daily_count >= 10:
            return False, "حداکثر 10 درخواست در روز مجاز است"
        
        return True, "OK"
    
    def increment_counters(self):
        """افزایش شمارنده‌ها"""
        self.minute_count += 1
        self.hour_count += 1
        self.daily_count += 1
        self.save()
    
    def add_failed_attempt(self):
        """افزودن تلاش ناموفق"""
        self.failed_attempts += 1
        
        if self.failed_attempts >= 10:
            self.is_blocked = True
            self.blocked_until = timezone.now() + timedelta(hours=24)
        
        self.save()


class TokenBlacklist(models.Model):
    """
    لیست سیاه توکن‌ها
    """
    token = models.TextField(
        unique=True,
        verbose_name='توکن'
    )
    
    token_type = models.CharField(
        max_length=20,
        choices=[
            ('access', 'Access Token'),
            ('refresh', 'Refresh Token'),
        ],
        verbose_name='نوع توکن'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blacklisted_tokens',
        verbose_name='کاربر'
    )
    
    blacklisted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='زمان مسدودی'
    )
    
    reason = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='دلیل'
    )
    
    expires_at = models.DateTimeField(
        verbose_name='زمان انقضا'
    )
    
    class Meta:
        verbose_name = 'توکن مسدود'
        verbose_name_plural = 'توکن‌های مسدود'
        ordering = ['-blacklisted_at']
        indexes = [
            models.Index(fields=['token', 'expires_at']),
        ]
    
    def __str__(self):
        return f"Blacklisted {self.token_type} - {self.user}"
    
    @classmethod
    def is_blacklisted(cls, token):
        """بررسی مسدود بودن توکن"""
        return cls.objects.filter(
            token=token,
            expires_at__gt=timezone.now()
        ).exists()