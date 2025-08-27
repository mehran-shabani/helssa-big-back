"""
سرویس مدیریت OTP با قابلیت Rate Limiting
OTP Management Service with Rate Limiting
"""

from django.utils import timezone
from django.db import transaction
from django.core.cache import cache
from datetime import timedelta
from typing import Tuple, Optional
import logging

from ..models import OTPRequest, OTPRateLimit
from .kavenegar_service import KavenegarService

logger = logging.getLogger(__name__)


class OTPService:
    """
    سرویس مدیریت کامل OTP
    """
    
    def __init__(self):
        self.kavenegar = KavenegarService()
    
    def send_otp(
        self,
        phone_number: str,
        purpose: str = 'login',
        sent_via: str = 'sms',
        ip_address: str = None,
        user_agent: str = None
    ) -> Tuple[bool, dict]:
        """
        ارسال OTP با بررسی محدودیت‌ها
        
        Args:
            phone_number: شماره موبایل
            purpose: هدف ارسال
            sent_via: روش ارسال (sms/call)
            ip_address: آدرس IP درخواست‌دهنده
            user_agent: User Agent
            
        Returns:
            Tuple[bool, dict]: (موفقیت، داده‌ها/خطا)
        """
        try:
            # فرمت کردن شماره
            phone_number = KavenegarService.format_phone_number(phone_number)
            
            # بررسی rate limit
            can_send, message = self._check_rate_limit(phone_number)
            if not can_send:
                return False, {
                    'error': 'rate_limit_exceeded',
                    'message': message,
                    'rate_limit_info': self._get_rate_limit_info(phone_number)
                }
            
            # باطل کردن OTP های قبلی
            self._invalidate_previous_otps(phone_number, purpose)
            
            # ایجاد OTP جدید
            otp_request = OTPRequest.objects.create(
                phone_number=phone_number,
                purpose=purpose,
                sent_via=sent_via,
                ip_address=ip_address,
                user_agent=user_agent or ''
            )
            
            # ارسال OTP
            if sent_via == 'sms':
                result = self.kavenegar.send_otp(
                    phone_number,
                    otp_request.otp_code
                )
            elif sent_via == 'call':
                result = self.kavenegar.send_voice_otp(
                    phone_number,
                    otp_request.otp_code
                )
            else:
                return False, {
                    'error': 'invalid_sent_via',
                    'message': 'روش ارسال نامعتبر است'
                }
            
            if result['success']:
                # ذخیره message_id
                otp_request.kavenegar_message_id = result['message_id']
                otp_request.save()
                
                # بروزرسانی rate limit
                self._update_rate_limit(phone_number)
                
                # کش کردن برای دسترسی سریع
                cache_key = f"otp_{phone_number}_{purpose}"
                cache.set(cache_key, otp_request.id, timeout=180)  # 3 دقیقه
                
                logger.info(
                    f"OTP sent successfully: {phone_number}, "
                    f"purpose: {purpose}, id: {otp_request.id}"
                )
                
                return True, {
                    'otp_id': str(otp_request.id),
                    'expires_at': otp_request.expires_at.isoformat(),
                    'expires_in': 180,  # ثانیه
                    'message': 'کد تأیید با موفقیت ارسال شد'
                }
            else:
                # خطا در ارسال
                otp_request.metadata['send_error'] = result.get('error_detail', '')
                otp_request.save()
                
                # افزایش تلاش ناموفق
                self._add_failed_attempt(phone_number)
                
                return False, {
                    'error': 'send_failed',
                    'message': result.get('error', 'خطا در ارسال کد تأیید')
                }
                
        except Exception as e:
            logger.error(f"Error in send_otp: {e}")
            return False, {
                'error': 'internal_error',
                'message': 'خطای سیستمی در ارسال کد تأیید'
            }
    
    def verify_otp(
        self,
        phone_number: str,
        otp_code: str,
        purpose: str = 'login'
    ) -> Tuple[bool, dict]:
        """
        تأیید کد OTP
        
        Args:
            phone_number: شماره موبایل
            otp_code: کد OTP
            purpose: هدف
            
        Returns:
            Tuple[bool, dict]: (موفقیت، داده‌ها/خطا)
        """
        try:
            # فرمت کردن شماره
            phone_number = KavenegarService.format_phone_number(phone_number)
            
            # جستجو در کش
            cache_key = f"otp_{phone_number}_{purpose}"
            otp_id = cache.get(cache_key)
            
            if otp_id:
                # پیدا کردن از کش
                otp_request = OTPRequest.objects.filter(
                    id=otp_id,
                    phone_number=phone_number,
                    purpose=purpose
                ).first()
            else:
                # جستجو در دیتابیس
                otp_request = OTPRequest.objects.filter(
                    phone_number=phone_number,
                    purpose=purpose,
                    is_used=False
                ).order_by('-created_at').first()
            
            if not otp_request:
                return False, {
                    'error': 'otp_not_found',
                    'message': 'کد تأیید یافت نشد یا منقضی شده است'
                }
            
            # بررسی امکان تأیید
            if not otp_request.can_verify:
                if otp_request.is_expired:
                    return False, {
                        'error': 'otp_expired',
                        'message': 'کد تأیید منقضی شده است'
                    }
                elif otp_request.is_used:
                    return False, {
                        'error': 'otp_already_used',
                        'message': 'این کد قبلاً استفاده شده است'
                    }
                elif otp_request.attempts >= 3:
                    return False, {
                        'error': 'max_attempts_exceeded',
                        'message': 'تعداد تلاش‌های مجاز به پایان رسیده است'
                    }
                else:
                    return False, {
                        'error': 'cannot_verify',
                        'message': 'امکان تأیید این کد وجود ندارد'
                    }
            
            # بررسی کد
            if otp_request.otp_code != otp_code:
                # افزایش تعداد تلاش
                otp_request.increment_attempts()
                
                remaining = 3 - otp_request.attempts
                if remaining > 0:
                    return False, {
                        'error': 'invalid_otp',
                        'message': f'کد تأیید اشتباه است. {remaining} تلاش باقی‌مانده',
                        'remaining_attempts': remaining
                    }
                else:
                    return False, {
                        'error': 'invalid_otp',
                        'message': 'کد تأیید اشتباه است و تلاش‌های مجاز تمام شد',
                        'remaining_attempts': 0
                    }
            
            # کد صحیح است
            with transaction.atomic():
                # علامت‌گذاری به عنوان استفاده شده
                otp_request.mark_as_used()
                
                # حذف از کش
                cache.delete(cache_key)
                
                # ریست rate limit برای تلاش‌های ناموفق
                self._reset_failed_attempts(phone_number)
                
                logger.info(
                    f"OTP verified successfully: {phone_number}, "
                    f"purpose: {purpose}"
                )
                
                return True, {
                    'otp_request': otp_request,
                    'message': 'کد تأیید با موفقیت تأیید شد'
                }
                
        except Exception as e:
            logger.error(f"Error in verify_otp: {e}")
            return False, {
                'error': 'internal_error',
                'message': 'خطای سیستمی در تأیید کد'
            }
    
    def resend_otp(
        self,
        phone_number: str,
        purpose: str = 'login',
        sent_via: str = 'sms',
        ip_address: str = None,
        user_agent: str = None
    ) -> Tuple[bool, dict]:
        """
        ارسال مجدد OTP
        """
        # همان send_otp با باطل کردن قبلی‌ها
        return self.send_otp(
            phone_number,
            purpose,
            sent_via,
            ip_address,
            user_agent
        )
    
    def _check_rate_limit(self, phone_number: str) -> Tuple[bool, str]:
        """بررسی محدودیت نرخ"""
        rate_limit, created = OTPRateLimit.objects.get_or_create(
            phone_number=phone_number
        )
        
        return rate_limit.can_send_otp()
    
    def _update_rate_limit(self, phone_number: str):
        """بروزرسانی شمارنده‌های rate limit"""
        rate_limit, _ = OTPRateLimit.objects.get_or_create(
            phone_number=phone_number
        )
        rate_limit.increment_counters()
    
    def _add_failed_attempt(self, phone_number: str):
        """افزودن تلاش ناموفق"""
        rate_limit, _ = OTPRateLimit.objects.get_or_create(
            phone_number=phone_number
        )
        rate_limit.add_failed_attempt()
    
    def _reset_failed_attempts(self, phone_number: str):
        """ریست تلاش‌های ناموفق"""
        try:
            rate_limit = OTPRateLimit.objects.get(phone_number=phone_number)
            rate_limit.failed_attempts = 0
            rate_limit.save()
        except OTPRateLimit.DoesNotExist:
            pass
    
    def _invalidate_previous_otps(self, phone_number: str, purpose: str):
        """باطل کردن OTP های قبلی"""
        OTPRequest.objects.filter(
            phone_number=phone_number,
            purpose=purpose,
            is_used=False
        ).update(is_used=True)
    
    def _get_rate_limit_info(self, phone_number: str) -> dict:
        """دریافت اطلاعات rate limit"""
        try:
            rate_limit = OTPRateLimit.objects.get(phone_number=phone_number)
            rate_limit.check_and_update_windows()
            
            return {
                'minute_remaining': max(0, 1 - rate_limit.minute_count),
                'hour_remaining': max(0, 5 - rate_limit.hour_count),
                'daily_remaining': max(0, 10 - rate_limit.daily_count),
                'is_blocked': rate_limit.is_blocked,
                'blocked_until': rate_limit.blocked_until.isoformat() if rate_limit.blocked_until else None
            }
        except OTPRateLimit.DoesNotExist:
            return {
                'minute_remaining': 1,
                'hour_remaining': 5,
                'daily_remaining': 10,
                'is_blocked': False,
                'blocked_until': None
            }
    
    @staticmethod
    def cleanup_expired_otps():
        """پاکسازی OTP های منقضی شده"""
        cutoff = timezone.now() - timedelta(hours=24)
        deleted_count = OTPRequest.objects.filter(
            created_at__lt=cutoff
        ).delete()[0]
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} expired OTP requests")
        
        return deleted_count