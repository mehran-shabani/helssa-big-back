"""
سریالایزرهای سیستم احراز هویت OTP
OTP Authentication System Serializers
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from .models import OTPRequest, OTPVerification, TokenBlacklist

User = get_user_model()


class PhoneNumberSerializer(serializers.Serializer):
    """
    سریالایزر برای اعتبارسنجی شماره تلفن
    """
    phone_number = serializers.CharField(
        max_length=11,
        validators=[
            RegexValidator(
                r'^09\d{9}$',
                'شماره موبایل باید با 09 شروع شود و 11 رقم باشد'
            )
        ],
        help_text='شماره موبایل به فرمت 09123456789'
    )


class OTPRequestSerializer(serializers.Serializer):
    """
    سریالایزر برای درخواست ارسال OTP
    """
    phone_number = serializers.CharField(
        max_length=11,
        validators=[
            RegexValidator(
                r'^09\d{9}$',
                'شماره موبایل باید با 09 شروع شود و 11 رقم باشد'
            )
        ]
    )
    
    purpose = serializers.ChoiceField(
        choices=['login', 'register', 'reset_password', 'verify_phone'],
        default='login',
        help_text='هدف از ارسال OTP'
    )
    
    sent_via = serializers.ChoiceField(
        choices=['sms', 'call'],
        default='sms',
        help_text='روش ارسال OTP'
    )
    
    def validate_phone_number(self, value):
        """اعتبارسنجی شماره موبایل"""
        # حذف فاصله‌ها و کاراکترهای اضافی
        value = value.strip().replace(' ', '').replace('-', '')
        
        # بررسی فرمت
        if not value.startswith('09') or len(value) != 11:
            raise serializers.ValidationError(
                'شماره موبایل باید با 09 شروع شود و 11 رقم باشد'
            )
        
        return value


class OTPVerifySerializer(serializers.Serializer):
    """
    سریالایزر برای تأیید OTP
    """
    phone_number = serializers.CharField(
        max_length=11,
        validators=[
            RegexValidator(
                r'^09\d{9}$',
                'شماره موبایل باید با 09 شروع شود و 11 رقم باشد'
            )
        ]
    )
    
    otp_code = serializers.CharField(
        max_length=6,
        min_length=6,
        help_text='کد 6 رقمی ارسال شده'
    )
    
    purpose = serializers.ChoiceField(
        choices=['login', 'register', 'reset_password', 'verify_phone'],
        default='login'
    )
    
    # اطلاعات دستگاه (اختیاری)
    device_id = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text='شناسه یکتای دستگاه'
    )
    
    device_name = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
        help_text='نام دستگاه'
    )
    
    def validate_otp_code(self, value):
        """اعتبارسنجی کد OTP"""
        # بررسی عددی بودن
        if not value.isdigit():
            raise serializers.ValidationError('کد OTP باید فقط شامل اعداد باشد')
        
        # بررسی طول
        if len(value) != 6:
            raise serializers.ValidationError('کد OTP باید 6 رقم باشد')
        
        return value


class TokenSerializer(serializers.Serializer):
    """
    سریالایزر برای توکن‌های احراز هویت
    """
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    token_type = serializers.CharField(read_only=True, default='Bearer')
    expires_in = serializers.IntegerField(
        read_only=True,
        help_text='زمان انقضا به ثانیه'
    )


class UserInfoSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای اطلاعات کاربر
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'user_type',
            'is_active',
            'created_at'
        ]
        read_only_fields = fields
    
    def get_full_name(self, obj):
        """نام کامل کاربر"""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class OTPLoginResponseSerializer(serializers.Serializer):
    """
    سریالایزر برای پاسخ ورود موفق
    """
    tokens = TokenSerializer(read_only=True)
    user = UserInfoSerializer(read_only=True)
    is_new_user = serializers.BooleanField(
        read_only=True,
        help_text='آیا کاربر جدید است'
    )
    message = serializers.CharField(read_only=True)


class RefreshTokenSerializer(serializers.Serializer):
    """
    سریالایزر برای Refresh Token
    """
    refresh = serializers.CharField(
        required=True,
        help_text='Refresh token'
    )


class TokenBlacklistSerializer(serializers.Serializer):
    """
    سریالایزر برای مسدود کردن توکن
    """
    token = serializers.CharField(
        required=True,
        help_text='توکنی که باید مسدود شود'
    )
    
    token_type = serializers.ChoiceField(
        choices=['access', 'refresh'],
        default='access',
        help_text='نوع توکن'
    )
    
    reason = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text='دلیل مسدودسازی'
    )


class OTPStatusSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای وضعیت OTP
    """
    is_expired = serializers.BooleanField(read_only=True)
    can_verify = serializers.BooleanField(read_only=True)
    remaining_attempts = serializers.SerializerMethodField()
    expires_in_seconds = serializers.SerializerMethodField()
    
    class Meta:
        model = OTPRequest
        fields = [
            'id',
            'phone_number',
            'purpose',
            'is_used',
            'is_expired',
            'can_verify',
            'attempts',
            'remaining_attempts',
            'expires_at',
            'expires_in_seconds',
            'created_at'
        ]
        read_only_fields = fields
    
    def get_remaining_attempts(self, obj):
        """تعداد تلاش‌های باقی‌مانده"""
        return max(0, 3 - obj.attempts)
    
    def get_expires_in_seconds(self, obj):
        """زمان باقی‌مانده تا انقضا"""
        from django.utils import timezone
        if obj.is_expired:
            return 0
        
        remaining = (obj.expires_at - timezone.now()).total_seconds()
        return max(0, int(remaining))


class RateLimitStatusSerializer(serializers.Serializer):
    """
    سریالایزر برای وضعیت محدودیت نرخ
    """
    can_send = serializers.BooleanField(
        read_only=True,
        help_text='آیا امکان ارسال وجود دارد'
    )
    
    message = serializers.CharField(
        read_only=True,
        help_text='پیام وضعیت'
    )
    
    minute_limit = serializers.IntegerField(
        read_only=True,
        default=1,
        help_text='محدودیت در دقیقه'
    )
    
    minute_remaining = serializers.IntegerField(
        read_only=True,
        help_text='تعداد باقی‌مانده در دقیقه'
    )
    
    hour_limit = serializers.IntegerField(
        read_only=True,
        default=5,
        help_text='محدودیت در ساعت'
    )
    
    hour_remaining = serializers.IntegerField(
        read_only=True,
        help_text='تعداد باقی‌مانده در ساعت'
    )
    
    is_blocked = serializers.BooleanField(
        read_only=True,
        help_text='آیا شماره مسدود است'
    )
    
    blocked_until = serializers.DateTimeField(
        read_only=True,
        allow_null=True,
        help_text='زمان رفع مسدودیت'
    )


class RegisterSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای ثبت‌نام کاربر جدید
    """
    phone_number = serializers.CharField(
        max_length=11,
        validators=[
            RegexValidator(
                r'^09\d{9}$',
                'شماره موبایل باید با 09 شروع شود و 11 رقم باشد'
            )
        ]
    )
    
    user_type = serializers.ChoiceField(
        choices=['patient', 'doctor'],
        default='patient',
        help_text='نوع کاربر'
    )
    
    first_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True
    )
    
    last_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True
    )
    
    email = serializers.EmailField(
        required=False,
        allow_blank=True
    )
    
    class Meta:
        model = User
        fields = [
            'phone_number',
            'user_type',
            'first_name',
            'last_name',
            'email'
        ]
    
    def validate_phone_number(self, value):
        """بررسی یکتا بودن شماره موبایل"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'این شماره موبایل قبلاً ثبت شده است'
            )
        return value
    
    def create(self, validated_data):
        """ایجاد کاربر جدید"""
        phone_number = validated_data.pop('phone_number')
        
        user = User.objects.create_user(
            username=phone_number,
            **validated_data
        )
        
        return user


class LogoutSerializer(serializers.Serializer):
    """
    سریالایزر برای خروج از سیستم
    """
    refresh = serializers.CharField(
        required=True,
        help_text='Refresh token برای باطل کردن'
    )
    
    logout_all_devices = serializers.BooleanField(
        default=False,
        help_text='خروج از تمام دستگاه‌ها'
    )