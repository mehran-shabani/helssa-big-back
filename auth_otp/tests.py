"""
تست‌های سیستم احراز هویت OTP
OTP Authentication System Tests
"""

from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock
import uuid

from .models import OTPRequest, OTPVerification, OTPRateLimit, TokenBlacklist
from .services import OTPService, AuthService

User = get_user_model()


class OTPModelTests(TestCase):
    """تست‌های مدل OTP"""
    
    def setUp(self):
        """
        مقدمه‌ای برای هر تست: شماره تلفن نمونه را قبل از اجرای هر مورد تست مقداردهی می‌کند.
        
        این متد توسط چارچوب تست (setUp) قبل از هر تست اجرا می‌شود و صفت instance `self.phone_number` را با مقدار نمونه `'09123456789'` مقداردهی می‌کند تا در تست‌های مختلف مربوط به OTP و احراز هویت به‌عنوان شمارهٔ ورودی استاندارد استفاده شود.
        """
        self.phone_number = '09123456789'
    
    def test_otp_request_creation(self):
        """
        تست ایجاد یک OTPRequest و اعتبارسنجی ویژگی‌های آن.
        
        این تست یک رکورد OTPRequest با شماره تلفن و منظور ورود ایجاد می‌کند و بررسی می‌کند که:
        - کد OTP تولید‌شده شش رقمی و فقط از ارقام تشکیل شده باشد.
        - مقدار expires_at حدوداً ۳ دقیقه پس از زمان فعلی باشد (تفاوت کمتر از ۵ ثانیه).
        
        توجه: این تست یک نمونه در دیتابیس ایجاد می‌کند (side effect).
        """
        otp_request = OTPRequest.objects.create(
            phone_number=self.phone_number,
            purpose='login'
        )
        
        # بررسی کد OTP
        self.assertEqual(len(otp_request.otp_code), 6)
        self.assertTrue(otp_request.otp_code.isdigit())
        
        # بررسی زمان انقضا (3 دقیقه)
        expected_expiry = timezone.now() + timedelta(minutes=3)
        time_diff = abs((otp_request.expires_at - expected_expiry).total_seconds())
        self.assertLess(time_diff, 5)  # تفاوت کمتر از 5 ثانیه
    
    def test_otp_is_expired_property(self):
        """تست خاصیت is_expired"""
        # OTP منقضی نشده
        otp_request = OTPRequest.objects.create(
            phone_number=self.phone_number,
            expires_at=timezone.now() + timedelta(minutes=1)
        )
        self.assertFalse(otp_request.is_expired)
        
        # OTP منقضی شده
        otp_request.expires_at = timezone.now() - timedelta(minutes=1)
        otp_request.save()
        self.assertTrue(otp_request.is_expired)
    
    def test_otp_can_verify_property(self):
        """تست خاصیت can_verify"""
        otp_request = OTPRequest.objects.create(
            phone_number=self.phone_number
        )
        
        # حالت عادی
        self.assertTrue(otp_request.can_verify)
        
        # بعد از استفاده
        otp_request.is_used = True
        self.assertFalse(otp_request.can_verify)
        
        # بعد از 3 تلاش
        otp_request.is_used = False
        otp_request.attempts = 3
        self.assertFalse(otp_request.can_verify)
    
    def test_rate_limit_windows(self):
        """تست پنجره‌های زمانی rate limit"""
        rate_limit = OTPRateLimit.objects.create(
            phone_number=self.phone_number
        )
        
        # بررسی ریست پنجره دقیقه
        rate_limit.minute_window_start = timezone.now() - timedelta(minutes=2)
        rate_limit.minute_count = 5
        rate_limit.check_and_update_windows()
        self.assertEqual(rate_limit.minute_count, 0)
        
        # بررسی ریست پنجره ساعت
        rate_limit.hour_window_start = timezone.now() - timedelta(hours=2)
        rate_limit.hour_count = 10
        rate_limit.check_and_update_windows()
        self.assertEqual(rate_limit.hour_count, 0)


class OTPServiceTests(TestCase):
    """تست‌های سرویس OTP"""
    
    def setUp(self):
        self.phone_number = '09123456789'
        self.otp_service = OTPService()
    
    @patch('auth_otp.services.kavenegar_service.KavenegarAPI')
    def test_send_otp_success(self, mock_kavenegar):
        """تست ارسال موفق OTP"""
        # Mock Kavenegar response
        mock_api_instance = MagicMock()
        mock_api_instance.verify_lookup.return_value = {
            'messageid': '123456',
            'status': 200,
            'statustext': 'Success'
        }
        mock_kavenegar.return_value = mock_api_instance
        
        success, result = self.otp_service.send_otp(
            phone_number=self.phone_number,
            purpose='login'
        )
        
        self.assertTrue(success)
        self.assertIn('otp_id', result)
        self.assertIn('expires_at', result)
        
        # بررسی ایجاد رکورد در دیتابیس
        otp_request = OTPRequest.objects.get(id=result['otp_id'])
        self.assertEqual(otp_request.phone_number, self.phone_number)
        self.assertEqual(otp_request.kavenegar_message_id, '123456')
    
    def test_send_otp_rate_limit(self):
        """تست محدودیت نرخ ارسال OTP"""
        # ایجاد rate limit که حد مجاز را رد کرده
        rate_limit = OTPRateLimit.objects.create(
            phone_number=self.phone_number,
            minute_count=2,
            minute_window_start=timezone.now()
        )
        
        success, result = self.otp_service.send_otp(
            phone_number=self.phone_number,
            purpose='login'
        )
        
        self.assertFalse(success)
        self.assertEqual(result['error'], 'rate_limit_exceeded')
    
    def test_verify_otp_success(self):
        """تست تأیید موفق OTP"""
        # ایجاد OTP
        otp_request = OTPRequest.objects.create(
            phone_number=self.phone_number,
            otp_code='123456',
            purpose='login'
        )
        
        success, result = self.otp_service.verify_otp(
            phone_number=self.phone_number,
            otp_code='123456',
            purpose='login'
        )
        
        self.assertTrue(success)
        self.assertEqual(result['otp_request'], otp_request)
        
        # بررسی علامت‌گذاری به عنوان استفاده شده
        otp_request.refresh_from_db()
        self.assertTrue(otp_request.is_used)
    
    def test_verify_otp_wrong_code(self):
        """تست تأیید OTP با کد اشتباه"""
        otp_request = OTPRequest.objects.create(
            phone_number=self.phone_number,
            otp_code='123456',
            purpose='login'
        )
        
        success, result = self.otp_service.verify_otp(
            phone_number=self.phone_number,
            otp_code='654321',
            purpose='login'
        )
        
        self.assertFalse(success)
        self.assertEqual(result['error'], 'invalid_otp')
        
        # بررسی افزایش تعداد تلاش
        otp_request.refresh_from_db()
        self.assertEqual(otp_request.attempts, 1)


class AuthServiceTests(TestCase):
    """تست‌های سرویس احراز هویت"""
    
    def test_create_user_if_not_exists(self):
        """تست ایجاد کاربر جدید"""
        phone_number = '09123456789'
        
        # کاربر جدید
        user, is_new = AuthService.create_user_if_not_exists(
            phone_number=phone_number,
            user_type='patient'
        )
        
        self.assertTrue(is_new)
        self.assertEqual(user.username, phone_number)
        self.assertEqual(user.user_type, 'patient')
        
        # کاربر موجود
        user2, is_new2 = AuthService.create_user_if_not_exists(
            phone_number=phone_number,
            user_type='patient'
        )
        
        self.assertFalse(is_new2)
        self.assertEqual(user.id, user2.id)
    
    def test_generate_tokens(self):
        """
        اعتبارسنجی تولید مجموعه توکن‌های احراز هویت (JWT) برای یک کاربر جدید.
        
        این تست بررسی می‌کند که AuthService.generate_tokens برای یک کاربر جدید دیکشنری‌ای شامل کلیدهای زیر بازمی‌گرداند:
        - 'access': توکن دسترسی (access token)
        - 'refresh': توکن تجدید (refresh token)
        - 'token_type': نوع توکن که باید مقدار 'Bearer' باشد
        - 'expires_in': مدت زمان عمر توکن (به‌طور ضمنی بررسی وجود کلید، نه مقدار دقیق)
        
        تست هیچ مقدار خاصی برای توکن‌ها را بررسی نمی‌کند، فقط حضور کلیدهای مورد انتظار و مقدار صحیح 'token_type' را تضمین می‌کند.
        """
        user = User.objects.create_user(
            username='09123456789',
            user_type='patient'
        )
        
        tokens = AuthService.generate_tokens(user)
        
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
        self.assertIn('token_type', tokens)
        self.assertEqual(tokens['token_type'], 'Bearer')
        self.assertIn('expires_in', tokens)
    
    def test_blacklist_token(self):
        """تست مسدود کردن توکن"""
        user = User.objects.create_user(
            username='09123456789',
            user_type='patient'
        )
        
        token = 'test-token-123'
        success = AuthService.blacklist_token(
            token=token,
            token_type='access',
            user=user,
            reason='Test blacklist'
        )
        
        self.assertTrue(success)
        self.assertTrue(TokenBlacklist.is_blacklisted(token))


class OTPAPITests(APITestCase):
    """تست‌های API احراز هویت OTP"""
    
    def setUp(self):
        """
        مقدمه‌ای برای هر تست: شماره تلفن نمونه را قبل از اجرای هر مورد تست مقداردهی می‌کند.
        
        این متد توسط چارچوب تست (setUp) قبل از هر تست اجرا می‌شود و صفت instance `self.phone_number` را با مقدار نمونه `'09123456789'` مقداردهی می‌کند تا در تست‌های مختلف مربوط به OTP و احراز هویت به‌عنوان شمارهٔ ورودی استاندارد استفاده شود.
        """
        self.phone_number = '09123456789'
    
    @patch('auth_otp.services.kavenegar_service.KavenegarAPI')
    def test_send_otp_api(self, mock_kavenegar):
        """
        آزمون endpoint ارسال OTP از طریق API.
        
        این تست فراخوانی POST به مسیر 'auth_otp:otp_send' را با شماره تلفن و منظور (purpose) شبیه‌سازی می‌کند و موارد زیر را راستی‌آزمایی می‌کند:
        - پاسخ HTTP با کد 201 (Created) بازگردانده شود.
        - فیلد success در بدنه پاسخ True باشد.
        - شناسهٔ تولید شده OTP ('otp_id') در داده‌های پاسخ وجود داشته باشد.
        
        برای جداسازی از سرویس خارجی ارسال پیامک، اتصال به Kavenegar با یک ماک (mock_kavenegar) فراهم و رفتار آن با پاسخ موفق شبیه‌سازی می‌شود تا فراخوانی سرویس پیامک در جریان تست کنترل شود.
        """
        # Mock Kavenegar
        mock_api_instance = MagicMock()
        mock_api_instance.verify_lookup.return_value = {
            'messageid': '123456',
            'status': 200,
            'statustext': 'Success'
        }
        mock_kavenegar.return_value = mock_api_instance
        
        url = reverse('auth_otp:otp_send')
        data = {
            'phone_number': self.phone_number,
            'purpose': 'login'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('otp_id', response.data['data'])
    
    def test_send_otp_invalid_phone(self):
        """تست API ارسال OTP با شماره نامعتبر"""
        url = reverse('auth_otp:otp_send')
        data = {
            'phone_number': '123456',  # شماره نامعتبر
            'purpose': 'login'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error'], 'validation_error')
    
    def test_verify_otp_api(self):
        """تست API تأیید OTP"""
        # ایجاد OTP
        otp_request = OTPRequest.objects.create(
            phone_number=self.phone_number,
            otp_code='123456',
            purpose='login'
        )
        
        url = reverse('auth_otp:otp_verify')
        data = {
            'phone_number': self.phone_number,
            'otp_code': '123456',
            'purpose': 'login'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('tokens', response.data['data'])
        self.assertIn('user', response.data['data'])
        self.assertTrue(response.data['data']['is_new_user'])
    
    def test_refresh_token_api(self):
        """تست API تازه‌سازی توکن"""
        # ایجاد کاربر و توکن
        user = User.objects.create_user(
            username=self.phone_number,
            user_type='patient'
        )
        tokens = AuthService.generate_tokens(user)
        
        url = reverse('auth_otp:token_refresh')
        data = {
            'refresh': tokens['refresh']
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data['data'])
    
    def test_logout_api(self):
        """
        تأیید می‌کند که endpoint خروج (logout) توکن رفرش را بلک‌لیست می‌کند و درخواست با توکن دسترسی معتبر پذیرفته می‌شود.
        
        در این تست:
        - یک کاربر جدید ساخته می‌شود و برای او توکن‌های دسترسی و رفرش تولید می‌گردد.
        - هدر Authorization با توکن access تنظیم شده و یک درخواست POST به endpoint خروج ارسال می‌شود.
        - انتظار می‌رود پاسخ HTTP 200 و فیلد `success` برابر True باشد.
        - در نهایت بررسی می‌شود که توکن رفرش ارسال‌شده در بلک‌لیست قرار گرفته باشد (TokenBlacklist.is_blacklisted بازگشت True).
        """
        # ایجاد کاربر و ورود
        user = User.objects.create_user(
            username=self.phone_number,
            user_type='patient'
        )
        tokens = AuthService.generate_tokens(user)
        
        # تنظیم توکن برای درخواست
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('auth_otp:logout')
        data = {
            'refresh': tokens['refresh']
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # بررسی مسدود شدن توکن
        self.assertTrue(TokenBlacklist.is_blacklisted(tokens['refresh']))


class CleanupTasksTests(TransactionTestCase):
    """تست‌های تسک‌های پاکسازی"""
    
    def test_cleanup_expired_otps(self):
        """تست پاکسازی OTP های منقضی"""
        # ایجاد OTP های قدیمی
        old_otp1 = OTPRequest.objects.create(
            phone_number='09123456789',
            created_at=timezone.now() - timedelta(days=2)
        )
        old_otp2 = OTPRequest.objects.create(
            phone_number='09123456788',
            created_at=timezone.now() - timedelta(days=2)
        )
        
        # ایجاد OTP جدید
        new_otp = OTPRequest.objects.create(
            phone_number='09123456787'
        )
        
        # پاکسازی
        deleted_count = OTPService.cleanup_expired_otps()
        
        self.assertEqual(deleted_count, 2)
        self.assertFalse(OTPRequest.objects.filter(id=old_otp1.id).exists())
        self.assertFalse(OTPRequest.objects.filter(id=old_otp2.id).exists())
        self.assertTrue(OTPRequest.objects.filter(id=new_otp.id).exists())
    
    def test_cleanup_expired_blacklist(self):
        """تست پاکسازی توکن‌های منقضی از blacklist"""
        user = User.objects.create_user(
            username='09123456789',
            user_type='patient'
        )
        
        # توکن منقضی
        expired_token = TokenBlacklist.objects.create(
            token='expired-token',
            token_type='access',
            user=user,
            expires_at=timezone.now() - timedelta(days=1)
        )
        
        # توکن معتبر
        valid_token = TokenBlacklist.objects.create(
            token='valid-token',
            token_type='refresh',
            user=user,
            expires_at=timezone.now() + timedelta(days=1)
        )
        
        # پاکسازی
        deleted_count = AuthService.cleanup_expired_blacklist()
        
        self.assertEqual(deleted_count, 1)
        self.assertFalse(TokenBlacklist.objects.filter(id=expired_token.id).exists())
        self.assertTrue(TokenBlacklist.objects.filter(id=valid_token.id).exists())