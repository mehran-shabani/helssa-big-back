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
        """نمایش محافظت شده کد OTP"""
        if obj.is_used:
            return format_html('<span style="color: gray;">استفاده شده</span>')
        elif obj.is_expired:
            return format_html('<span style="color: red;">منقضی شده</span>')
        else:
            # نمایش جزئی کد برای امنیت
            return f"**{obj.otp_code[-4:]}"
    otp_code_display.short_description = 'کد OTP'
    
    def is_expired_display(self, obj):
        """نمایش وضعیت انقضا"""
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
        """دریافت شماره تلفن از OTP request"""
        return obj.otp_request.phone_number
    get_phone_number.short_description = 'شماره موبایل'
    
    actions = ['deactivate_sessions']
    
    def deactivate_sessions(self, request, queryset):
        """غیرفعال کردن نشست‌های انتخاب شده"""
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
        """رفع مسدودیت شماره‌های انتخاب شده"""
        count = queryset.filter(is_blocked=True).update(
            is_blocked=False,
            blocked_until=None,
            failed_attempts=0
        )
        self.message_user(request, f'{count} شماره از مسدودیت خارج شد.')
    unblock_numbers.short_description = 'رفع مسدودیت'
    
    def reset_counters(self, request, queryset):
        """ریست کردن شمارنده‌ها"""
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
        """نمایش محدود توکن برای امنیت"""
        return f"{obj.token[:20]}..."
    get_token_preview.short_description = 'توکن'
    
    def is_expired_display(self, obj):
        """نمایش وضعیت انقضا"""
        if timezone.now() > obj.expires_at:
            return format_html('<span style="color: gray;">منقضی</span>')
        else:
            return format_html('<span style="color: green;">فعال</span>')
    is_expired_display.short_description = 'وضعیت'
    
    def has_add_permission(self, request):
        """غیرفعال کردن افزودن دستی"""
        return False