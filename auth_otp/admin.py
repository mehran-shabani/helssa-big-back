"""
ادمین پنل برای سیستم احراز هویت OTP
Admin Panel for OTP Authentication System
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import OTPRequest, OTPVerification, OTPRateLimit, TokenBlacklist


@admin.register(OTPRequest)
class OTPRequestAdmin(admin.ModelAdmin):
    """
    مدیریت درخواست‌های OTP
    """
    list_display = [
        'phone_number',
        'purpose',
        'otp_code_display',
        'is_used',
        'is_expired_display',
        'attempts',
        'sent_via',
        'created_at',
        'expires_at'
    ]
    
    list_filter = [
        'purpose',
        'is_used',
        'sent_via',
        'created_at'
    ]
    
    search_fields = [
        'phone_number',
        'otp_code',
        'kavenegar_message_id'
    ]
    
    readonly_fields = [
        'id',
        'otp_code',
        'expires_at',
        'created_at',
        'ip_address',
        'user_agent',
        'kavenegar_message_id',
        'metadata'
    ]
    
    ordering = ['-created_at']
    
    def otp_code_display(self, obj):
        """
        یک نمایش امن و مناسب برای ستون کد OTP در پنل ادمین بازمی‌گرداند.
        
        این تابع برای نمایش کد OTP در لیست ادمین استفاده می‌شود و بسته به وضعیت درخواست یکی از حالات زیر را برمی‌گرداند:
        - اگر OTP قبلاً استفاده شده باشد: برچسب خاکستری «استفاده شده».
        - اگر OTP منقضی شده باشد: برچسب قرمز «منقضی شده».
        - در غیر این صورت: نمایش ماسک‌شده از کد که فقط چهار رقم آخر را نشان می‌دهد (برای حفظ امنیت)، با پیشوند `**`.
        
        Parameters:
            obj (OTPRequest): نمونه مدل OTPRequest که شامل فیلدهای `is_used`, `is_expired` و `otp_code` است.
        
        Returns:
            str: رشته‌ای امن برای قرارگیری در لیست ادمین (HTML-safe). نمایشی از وضعیت یا نسخهٔ ماسک‌شدهٔ کد OTP.
        """
        if obj.is_used:
            return format_html('<span style="color: gray;">استفاده شده</span>')
        elif obj.is_expired:
            return format_html('<span style="color: red;">منقضی شده</span>')
        else:
            # نمایش جزئی کد برای امنیت
            return f"**{obj.otp_code[-4:]}"
    otp_code_display.short_description = 'کد OTP'
    
    def is_expired_display(self, obj):
        """
        یک نمایش‌دهنده وضعیت انقضا برای استفاده در Django admin که بر اساس مقدار `is_expired` علامت مناسب را برمی‌گرداند.
        
        تابع ورودی یک نمونه مدل را می‌پذیرد که ویژگی بولی `is_expired` دارد و با توجه به آن:
        - اگر منقضی شده باشد یک علامت ضرب (✗) با رنگ قرمز بازمی‌گرداند.
        - اگر منقضی نشده باشد یک علامت تیک (✓) با رنگ سبز بازمی‌گرداند.
        
        مقدار بازگشتی با استفاده از `format_html` ایمن‌سازی شده و مناسب قرارگیری در `list_display` پنل ادمین است.
        
        برمی‌گرداند:
            str: رشته HTML ایمن شامل یک نماد وضعیت رنگی (قرمز برای منقضی، سبز برای فعال).
        """
        if obj.is_expired:
            return format_html('<span style="color: red;">✗</span>')
        else:
            return format_html('<span style="color: green;">✓</span>')
    is_expired_display.short_description = 'منقضی شده'


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    """
    مدیریت تأییدیه‌های OTP
    """
    list_display = [
        'get_phone_number',
        'user',
        'device_name',
        'is_active',
        'verified_at'
    ]
    
    list_filter = [
        'is_active',
        'verified_at'
    ]
    
    search_fields = [
        'user__username',
        'user__first_name',
        'user__last_name',
        'device_id',
        'device_name'
    ]
    
    readonly_fields = [
        'id',
        'otp_request',
        'user',
        'verified_at',
        'access_token',
        'refresh_token',
        'device_id',
        'device_name',
        'session_key'
    ]
    
    ordering = ['-verified_at']
    
    def get_phone_number(self, obj):
        """
        بازمی‌گرداند شماره موبایل مرتبط با رکورد OTPVerification از طریق رابطه مربوطه.
        
        جزئیات:
        - مقدار بازگشتی: رشته‌ای که از `obj.otp_request.phone_number` استخراج می‌شود.
        - این متد فرض می‌کند که رابطه `otp_request` و فیلد `phone_number` روی شیء موجود است و صرفاً مقدار مرتبط را بازمی‌گرداند.
        """
        return obj.otp_request.phone_number
    get_phone_number.short_description = 'شماره موبایل'
    
    actions = ['deactivate_sessions']
    
    def deactivate_sessions(self, request, queryset):
        """
        غیرفعال‌سازی جلسه‌های انتخاب‌شده در ادمین.
        
        این اکشن روی queryset اعمال می‌شود (انتظار می‌رود متعلق به مدل OTPVerification باشد) و هر رکوردی که فیلد `is_active` آن True باشد را به False تغییر می‌دهد. پس از اعمال تغییرات، تعداد نشست‌های غیرفعال‌شده را به کاربر ادمین با استفاده از پیام ادمین نشان می‌دهد.
        
        Parameters:
            queryset (QuerySet): مجموعه رکوردهایی که قرار است پردازش شوند (معمولاً queryset از OTPVerification).
        """
        count = queryset.filter(is_active=True).update(is_active=False)
        self.message_user(request, f'{count} نشست غیرفعال شد.')
    deactivate_sessions.short_description = 'غیرفعال کردن نشست‌ها'


@admin.register(OTPRateLimit)
class OTPRateLimitAdmin(admin.ModelAdmin):
    """
    مدیریت محدودیت‌های نرخ OTP
    """
    list_display = [
        'phone_number',
        'minute_count',
        'hour_count',
        'daily_count',
        'is_blocked',
        'blocked_until',
        'failed_attempts',
        'last_request'
    ]
    
    list_filter = [
        'is_blocked',
        'last_request'
    ]
    
    search_fields = [
        'phone_number'
    ]
    
    readonly_fields = [
        'minute_window_start',
        'hour_window_start',
        'daily_window_start',
        'last_request'
    ]
    
    ordering = ['-last_request']
    
    actions = ['unblock_numbers', 'reset_counters']
    
    def unblock_numbers(self, request, queryset):
        """
        رفع مسدودیت برای رکوردهای انتخاب‌شده در مدل محدودیت نرخ (OTPRateLimit).
        
        این متد برای اکشن ادمین استفاده می‌شود؛ تمام رکوردهای درون `queryset` که فعلاً در حالت مسدود (is_blocked=True) هستند را آن‌مسدود می‌کند، مقدار فیلد `blocked_until` را پاک کرده و شمارنده‌ی `failed_attempts` را به صفر بازمی‌گرداند. پس از انجام به‌روزرسانی، پیغامی حاوی تعداد رکوردهای آن‌مسدودشده به کاربر نمایش داده می‌شود.
        
        Parameters:
            request: شیٔ HttpRequest مربوط به درخواست ادمین (برای نمایش پیام نتیجه).
            queryset: QuerySet از نمونه‌های OTPRateLimit که قرار است پردازش شوند؛ تنها رکوردهایی که دارای `is_blocked=True` هستند تغییر می‌یابند.
        
        Returns:
            None
        """
        count = queryset.filter(is_blocked=True).update(
            is_blocked=False,
            blocked_until=None,
            failed_attempts=0
        )
        self.message_user(request, f'{count} شماره از مسدودیت خارج شد.')
    unblock_numbers.short_description = 'رفع مسدودیت'
    
    def reset_counters(self, request, queryset):
        """
        ریست کردن شمارنده‌های نرخ محدودسازی برای رکوردهای انتخاب‌شده در پنل ادمین.
        
        این اکشن برای رکوردهای انتخاب‌شده فیلدهای `minute_count`، `hour_count` و `daily_count` را به صفر تنظیم می‌کند و زمان‌های شروع پنجره‌های مربوطه
        (`minute_window_start`, `hour_window_start`, `daily_window_start`) را به زمان جاری (timezone.now()) به‌روزرسانی می‌کند. پس از اجرا، پیغامی به کاربر ادمین
        نمایش داده می‌شود که تعداد رکوردهای به‌روزرسانی‌شده را نشان می‌دهد.
        """
        now = timezone.now()
        count = queryset.update(
            minute_count=0,
            hour_count=0,
            daily_count=0,
            minute_window_start=now,
            hour_window_start=now,
            daily_window_start=now
        )
        self.message_user(request, f'شمارنده‌های {count} شماره ریست شد.')
    reset_counters.short_description = 'ریست شمارنده‌ها'


@admin.register(TokenBlacklist)
class TokenBlacklistAdmin(admin.ModelAdmin):
    """
    مدیریت توکن‌های مسدود شده
    """
    list_display = [
        'get_token_preview',
        'token_type',
        'user',
        'reason',
        'blacklisted_at',
        'expires_at',
        'is_expired_display'
    ]
    
    list_filter = [
        'token_type',
        'blacklisted_at',
        'expires_at'
    ]
    
    search_fields = [
        'user__username',
        'reason'
    ]
    
    readonly_fields = [
        'token',
        'token_type',
        'user',
        'blacklisted_at',
        'reason',
        'expires_at'
    ]
    
    ordering = ['-blacklisted_at']
    
    def get_token_preview(self, obj):
        """
        بازگرداندن پیش‌نمایش کوتاه‌شده‌ای از مقدار توکن برای نمایش امن در پنل ادمین.
        
        این متد یک نسخهٔ کوتاه‌شده از فیلد `token` شیء داده‌شده برمی‌گرداند تا از نمایش کامل توکن (که اطلاعات حساسی است) جلوگیری شود — حداکثر ۲۰ کاراکتر اول به‌همراه `...`.
        
        Parameters:
            obj (TokenBlacklist): نمونهٔ مدل حاوی فیلد `token` که پیش‌نمایش از آن تولید می‌شود.
        
        Returns:
            str: رشته‌ای که حاوی ۲۰ کاراکتر اول توکن به‌همراه `...` است.
        """
        return f"{obj.token[:20]}..."
    get_token_preview.short_description = 'توکن'
    
    def is_expired_display(self, obj):
        """
        نمایش وضعیت انقضأ یک رکورد به‌صورت HTML امن.
        
        این متد بررسی می‌کند که زمان کنونی (با استفاده از timezone.now()) از مقدار expires_at شیء مورد نظر گذشته است یا نه و بر اساس آن یک تگ HTML امن بازمی‌گرداند: اگر منقضی شده باشد رشته‌ای با متن «منقضی» (به رنگ خاکستری) و در غیر این صورت «فعال» (به رنگ سبز). مقدار بازگشتی توسط قالب ادمین به‌عنوان HTML رندر می‌شود.
        
        Parameters:
            obj: شیء مدل حاوی فیلد datetime به نام `expires_at` (مثلاً نمونه TokenBlacklist). تنها در صورتی کاربردی است که `obj.expires_at` مقدار تاریخ/زمان قابل مقایسه داشته باشد.
        
        Returns:
            django.utils.safestring.SafeString: HTML امن حاوی وضعیت ("منقضی" یا "فعال").
        """
        if timezone.now() > obj.expires_at:
            return format_html('<span style="color: gray;">منقضی</span>')
        else:
            return format_html('<span style="color: green;">فعال</span>')
    is_expired_display.short_description = 'وضعیت'
    
    def has_add_permission(self, request):
        """
        بررسی و غیرفعال‌سازی امکان افزودن شیء جدید از رابط مدیریت Django.
        
        این متد همیشه False برمی‌گرداند تا دکمه و فرم افزودن (Add) در رابط ادمین برای مدل مربوطه غیرقابل‌دسترس شود و درخواست‌های افزودن از طریق پنل ادمین مسدود شوند. این کنترل تنها دسترسی از طریق رابط ادمین را غیرفعال می‌کند و ایجاد برنامه‌نویسی یا از طریق API را تغییر نمی‌دهد.
        """
        return False