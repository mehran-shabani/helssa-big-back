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
        """
        نمایش متنی کوتاه برای نمونهٔ OTPRequest.
        
        این متد یک رشتهٔ خوانا تولید می‌کند که شمارهٔ تلفن و هدف OTP را به‌صورت `OTP {phone_number} - {purpose}` بازمی‌گرداند؛ برای نمایش در پنل ادمین، لاگ‌ها و شی‌ٔ مدل در شل استفاده می‌شود.
        
        Returns:
            str: نمایش متنی نمونهٔ OTPRequest
        """
        return f"OTP {self.phone_number} - {self.purpose}"
    
    def save(self, *args, **kwargs):
        """
        یک ذخیره‌ساز سفارشی برای مدل OTPRequest.
        
        اگر فیلد `otp_code` خالی باشد، یک کد شش‌رقمی جدید تولید و به آن اختصاص می‌دهد. اگر فیلد `expires_at` مقداردهی نشده باشد، زمان انقضا را سه دقیقه پس از زمان جاری قرار می‌دهد. نهایتاً رکورد را با فراخوانی `super().save(*args, **kwargs)` در پایگاه‌داده ثبت/به‌روزرسانی می‌کند.
        
        تأثیرات جانبی:
        - ممکن است مقدارهای `otp_code` و `expires_at` را قبل از ذخیره تغییر دهد.
        - هیچ مقداری بازگشتی ندارد؛ نتیجهٔ عملکرد در پایگاه‌داده منعکس می‌شود.
        """
        if not self.otp_code:
            self.otp_code = self.generate_otp_code()
        
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=3)
        
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_otp_code():
        """
        تولید یک کد OTP شش‌رقمی امن و تصادفی.
        
        این تابع با استفاده از ماژول cryptographically secure `secrets` یک عدد صحیح در بازهٔ 100000 تا 999999 تولید می‌کند و آن را به صورت رشته‌ای شش‌رقمی بازمی‌گرداند. بدین ترتیب همیشه یک کد شامل شش رقم (بدون صفر پیشرو) را تضمین می‌کند و برای استفاده در مکانیزم‌های احراز هویت موقت مناسب است.
        
        Returns:
            str: یک رشته حاوی ۶ رقم (مثلاً `"482905"`).
        """
        return f"{secrets.randbelow(900000) + 100000:06d}"
    
    @property
    def is_expired(self):
        """
        بررسی می‌کند که آیا کد OTP منقضی شده است.
        
        تابع زمان کنونی را با expires_at مقایسه می‌کند و در صورتی که زمان فعلی (timezone.now()) بعد از expires_at باشد مقدار True بازمی‌گرداند، در غیر این صورت False.
        Returns:
        	bool: True اگر OTP منقضی شده باشد، False در غیر این صورت.
        """
        return timezone.now() > self.expires_at
    
    @property
    def can_verify(self):
        """
        بررسی می‌کند که آیا این OTP قابل‌استفاده برای تأیید است.
        
        تابع True برمی‌گرداند اگر:
        - کد هنوز مصرف نشده باشد (is_used=False)،
        - کد منقضی نشده باشد (is_expired() False)،
        - تعداد تلاش‌های فعلی کمتر از ۳ باشد (attempts < 3).
        
        Returns:
        	bool: وضعیت قابل‌تأیید بودن (True اگر قابل‌تأیید باشد، در غیر این صورت False).
        """
        return not self.is_used and not self.is_expired and self.attempts < 3
    
    def increment_attempts(self):
        """
        افزایش شمارندهٔ تلاش‌های تأیید برای این درخواست OTP و ذخیرهٔ تغییر در دیتابیس.
        
        با فراخوانی این متد مقدار فیلد `attempts` را یک واحد افزایش می‌دهد و فقط همان فیلد را با استفاده از `save(update_fields=['attempts'])` در پایگاه‌داده ذخیره می‌کند. این متد مقداری بازنمی‌گرداند و برای ثبت تعداد تلاش‌های ناموفق یا محدودسازی تعداد تلاش‌ها استفاده می‌شود.
        """
        self.attempts += 1
        self.save(update_fields=['attempts'])
    
    def mark_as_used(self):
        """
        علامت‌گذاری درخواست OTP به‌عنوان استفاده‌شده و ذخیرهٔ تغییر در دیتابیس.
        
        این متد فِلِد is_used را به True تنظیم کرده و تنها همین فِلِد را با save(update_fields=['is_used']) پایگاه‌داده‌ای به‌روز می‌کند تا تغییر سریع و اتمیک اعمال شود. فراخوانی مجدد ایمن است (idempotent) و برای ثبت اینکه کد OTP دیگر قابل‌استفاده نیست باید پس از تأیید موفق استفاده شود.
        """
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
        """
        نمایش متنی رکورد تأیید OTP شامل شمارهٔ تلفن و زمان تأیید.
        
        این متد یک رشته برمی‌گرداند که شمارهٔ تلفن مرتبط با درخواست OTP و زمان ثبت تأیید (verified_at) را نمایش می‌دهد. برای نمایش در ادمن، لاگ‌ها یا دیباگ مناسب است.
        
        Returns:
        	str: رشته‌ای به فرمت `"Verification {phone_number} - {verified_at}"`.
        """
        return f"Verification {self.otp_request.phone_number} - {self.verified_at}"
    
    def deactivate(self):
        """
        وضعیت تأییدیه را غیر‌فعال می‌کند و تغییر را در پایگاه‌داده ثبت می‌کند.
        
        این متد فیلد `is_active` را به `False` تغییر می‌دهد و فقط همین فیلد را با فراخوانی `save(update_fields=['is_active'])` ذخیره می‌کند. توجه: این متد توکن‌ها یا سایر منابع مرتبط را منقضی یا بازپس‌گیری نمی‌کند؛ در صورت نیاز باید عملیات‌های اضافی (مثلاً افزودن توکن‌ها به لیست سیاه) جداگانه انجام شوند.
        """
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
        """
        یک نمایش رشته‌ای خوانا برای شیء محدودیت نرخ که شماره تلفن مربوطه را نشان می‌دهد.
        
        Returns:
            str: رشته‌ای حاوی برچسب "Rate Limit" و شماره تلفن مرتبط (مثال: "Rate Limit 09123456789").
        """
        return f"Rate Limit {self.phone_number}"
    
    def reset_minute_window(self):
        """
        پیمانهٔ شمارش یک‌دقیقه‌ای را بازنشانی می‌کند.
        
        این متد مقدار minute_count را به صفر برمی‌گرداند و زمان شروع پنجرهٔ دقیقه (minute_window_start) را به زمان کنونی حساس به منطقهٔ زمانی تعیین می‌کند. تغییرات فقط روی نمونهٔ فعلی در حافظه اعمال می‌شود و برای ذخیرهٔ دائمی در پایگاه‌داده باید پس از فراخوانی متد save() فراخوانی شود. این متد وضعیت بلاک (is_blocked یا blocked_until) یا شمارنده‌های ساعتی/روزانه را تغییر نمی‌دهد.
        """
        self.minute_count = 0
        self.minute_window_start = timezone.now()
    
    def reset_hour_window(self):
        """
        پنجره‌ی شمارش ساعتی محدودیت ارسال را بازنشانی می‌کند.
        
        این متد شمارنده‌ی `hour_count` را صفر می‌کند و زمان شروع پنجره‌ی ساعتی (`hour_window_start`) را به زمان جاری (timezone-aware) قرار می‌دهد. توجه: این تابع تنها مقادیر فیلدها را در نمونهٔ مدل به‌روزرسانی می‌کند و خودکار عملیات ذخیره (save) روی پایگاه‌داده انجام نمی‌دهد — در صورت نیاز باید پس از فراخوانی `save()` صدا زده شود.
        """
        self.hour_count = 0
        self.hour_window_start = timezone.now()
    
    def reset_daily_window(self):
        """
        روزانه شدن پنجره‌ی شمارنده‌ی ارسال OTP را بازنشانی می‌کند.
        
        این متد مقدار شمارنده‌ی روزانه (daily_count) را به صفر تنظیم و زمان شروع پنجره‌ی روزانه (daily_window_start) را به زمان جاری سرور (timezone.now()) به‌روزرسانی می‌کند. از این متد برای آغاز یک بازه‌ی روزانهٔ جدید و محاسبهٔ محدودیت‌های روزانه پس از گذشت بازهٔ قبلی استفاده می‌شود.
        """
        self.daily_count = 0
        self.daily_window_start = timezone.now()
    
    def check_and_update_windows(self):
        """
        پنجره‌های شمارش محدودیت را بررسی و در صورت عبور از بازه‌های زمانی مرتبط بازنشانی می‌کند؛ همچنین وضعیت مسدودیت را بر اساس زمان پایان مسدودی به‌روز می‌کند.
        
        این متد رفتارهای جانبی زیر را انجام می‌دهد:
        - اگر از شروع پنجرهٔ دقیقه بیش از ۱ دقیقه گذشته باشد، شمارندهٔ دقیقه را بازنشانی می‌کند (reset_minute_window).
        - اگر از شروع پنجرهٔ ساعت بیش از ۱ ساعت گذشته باشد، شمارندهٔ ساعت را بازنشانی می‌کند (reset_hour_window).
        - اگر از شروع پنجرهٔ روز بیش از ۲۴ ساعت گذشته باشد، شمارندهٔ روز را بازنشانی می‌کند (reset_daily_window).
        - اگر شیء در حالت مسدودی است و زمان فعلی از blocked_until گذشته باشد، مسدودی را رفع کرده، blocked_until را پاک می‌کند و failed_attempts را به صفر بازنشانی می‌کند.
        
        هیچ مقداری بازگشتی ندارد؛ متد وضعیت شیء را مستقیماً تغییر و (در صورت لزوم) فیلدهای مرتبط را آمادهٔ ثبت می‌نماید.
        """
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
        """
        بررسی می‌کند که آیا برای شماره تلفن مربوط به این شیء می‌توان یک OTP جدید ارسال کرد.
        
        این متد ابتدا وضعیت پنجره‌های زمانی را با فراخوانی check_and_update_windows به‌روزرسانی می‌کند (که در صورت گذشتن بازه‌ها شمارنده‌ها را ریست و در صورت پایان مدت مسدودیت، وضعیت بلاک را حذف می‌کند). سپس قواعد نرخ‌دهی را ارزیابی می‌کند و یک تاپل (bool, str) برمی‌گرداند:
        - اگر نمونه در حالت مسدود باشد -> (False, پیامِ حاوی زمان پایان مسدودیت)
        - اگر حد دقیقه‌ای (حداکثر 1 در دقیقه) رد شده باشد -> (False, پیام مناسب)
        - اگر حد ساعتی (حداکثر 5 در ساعت) رد شده باشد -> (False, پیام مناسب)
        - اگر حد روزانه (حداکثر 10 در روز) رد شده باشد -> (False, پیام مناسب)
        - در غیر این‌صورت -> (True, "OK")
        
        مقدار بازگشتی:
            tuple:
                - اولین عضو (bool): آیا ارسال مجاز است.
                - دومین عضو (str): توضیح وضعیت یا پیام خطا به زبان فارسی.
        """
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
        """
        افزایش هم‌زمان شمارنده‌های دقیقه‌ای، ساعتی و روزانه و ذخیرهٔ تغییرات در پایگاه‌داده.
        
        این متد هر سه فیلد شمارنده (minute_count، hour_count، daily_count) را یک واحد افزایش می‌دهد و تغییرات را با فراخوانی save() در مدل ذخیره می‌کند. برای به‌روزرسانی سریع شمارش درخواست‌ها پس از ارسال موفق یا ثبت درخواست جدید OTP استفاده شود. (هیچ مقداری بازگردانده نمی‌شود؛ اثر جانبی: نوشتن به پایگاه‌داده)
        """
        self.minute_count += 1
        self.hour_count += 1
        self.daily_count += 1
        self.save()
    
    def add_failed_attempt(self):
        """
        افزایش شمارش تلاش ناموفق برای شماره تلفن و اعمال مسدودسازی در صورت تجاوز از آستانه.
        
        این متد مقدار فیلد `failed_attempts` را یک واحد افزایش می‌دهد، و اگر مقدار پس از افزایش برابر یا بیشتر از ۱۰ شود:
        - فیلد `is_blocked` را روی True قرار می‌دهد.
        - فیلد `blocked_until` را به زمان کنونی بعلاوه ۲۴ ساعت تنظیم می‌کند.
        
        در پایان تغییرات را با فراخوانی `save()` روی نمونه ذخیره می‌کند. این متد چیزی بازنمی‌گرداند و اثر جانبی آن به‌روزرسانی و ذخیرهٔ وضعیت مدل است.
        """
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
        """
        نمایش کوتاهی از رکورد توکن بلاک‌شده.
        
        رشته‌ای بازمی‌گرداند که نوع توکن (مثلاً `access` یا `refresh`) و نمایش قابل‌خواندنِ کاربر مرتبط را ترکیب می‌کند؛ مناسب برای نمایش در رابط‌های مدیریتی یا لاگ‌های انسانی.
        """
        return f"Blacklisted {self.token_type} - {self.user}"
    
    @classmethod
    def is_blacklisted(cls, token):
        """
        بررسی می‌کند که یک توکن مشخص در جدول بلک‌لیست وجود دارد و هنوز تاریخ انقضای آن نگذشته است.
        
        Parameters:
            token (str): مقدار توکن مورد بررسی.
        
        Returns:
            bool: True اگر رکورد بلک‌لیست با آن توکن وجود داشته باشد و expires_at آن بزرگتر از زمان فعلی باشد، در غیر این صورت False.
        """
        return cls.objects.filter(
            token=token,
            expires_at__gt=timezone.now()
        ).exists()