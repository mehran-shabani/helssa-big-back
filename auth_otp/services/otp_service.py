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
        """
        یک سازنده برای OTPService که نمونه‌ای از KavenegarService را در self.kavenegar مقداردهی می‌کند.
        
        این سرویس برای قالب‌بندی شماره تلفن و ارسال OTP (SMS یا voice) استفاده می‌شود و در سراسر متدهای کلاس جهت ارتباط با سرویس ارسال پیام به کار می‌رود.
        """
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
        ارسال یک کد OTP به شماره موبایل با رعایت محدودیت‌های نرخ و مدیریت چرخه عمر کد.
        
        این تابع یک OTP جدید ایجاد و (باطل‌کنندهٔ کدهای قبلی برای همان شماره/هدف) آن را از طریق SMS یا تماس صوتی ارسال می‌کند، محدودیت‌های ارسال را بررسی و به‌روز می‌کند، شناسه پیام سرویس ارسال‌کننده را ذخیره می‌کند و شناسهٔ درخواست را در کش برای دسترسی سریع نگه می‌دارد.
        
        رفتار و عوارض جانبی مهم:
        - شماره موبایل را فرمت می‌کند.
        - حالت‌های نرخ (rate limit) را بررسی می‌کند و در صورت تجاوز از محدودیت ارسال را متوقف کرده و اطلاعات محدودیت را بازمی‌گرداند.
        - OTPهای قبلی برای همان phone_number و purpose را باطل می‌کند.
        - یک رکورد OTPRequest جدید ایجاد می‌کند و در صورت موفقیت ارسال، message_id دریافتی را در آن ذخیره می‌کند.
        - در صورت ارسال موفق، شمارنده‌های نرخ به‌روزرسانی و شناسهٔ OTP در کش (کلید "otp_{phone_number}_{purpose}") با زمان‌انقضاء ۳ دقیقه قرار می‌گیرد.
        - در صورت شکست ارسال، خطای ارسال در metadata رکورد ذخیره و شمارش تلاش‌های ناموفق افزایش می‌یابد.
        - تمامی خطاهای داخلی را به‌صورت کلی هندل کرده و پیام استانداردی با error = 'internal_error' بازمی‌گرداند.
        
        پارامترها:
        - phone_number: شماره موبایل مقصد (رشته) — قبل از استفاده فرمت می‌شود.
        - purpose: هدف استفاده از OTP (پیش‌فرض 'login') — برای تمایز چند جریان OTP.
        - sent_via: روش ارسال؛ مقدارهای مجاز 'sms' یا 'call' (پیش‌فرض 'sms'). مقدار نامعتبر باعث بازگشت خطا می‌شود.
        - ip_address و user_agent: اختیاری، برای ثبت در رکورد OTPRequest (برای تحلیل/لاگ).
        
        مقدار بازگشتی:
        - Tuple[bool, dict]: اگر ارسال موفق باشد، (True, { 'otp_id', 'expires_at', 'expires_in', 'message' }) بازمی‌گردد. در موارد خطا، (False, { 'error': <کد_خطا>, 'message': <پیام_قابل_نمایش>, ... }) با اطلاعات تکمیلی مانند rate_limit_info یا پیام خطای سرویس ارسال‌کننده برگردانده می‌شود.
        
        کدهای خطای قابل انتظار (نمونه):
        - 'rate_limit_exceeded' — ارسال به‌دلیل محدودیت‌های نرخ مسدود شده است.
        - 'invalid_sent_via' — روش ارسال نامعتبر است.
        - 'send_failed' — شکست در ارسال توسط سرویس پیام‌رسان.
        - 'internal_error' — خطای داخلی/غیرمنتظره.
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
        تأیید یک کد OTP برای شماره موبایل مشخص و هدف داده‌شده.
        
        این تابع کد ورودی را با آخرین درخواست OTP معتبر برای phone_number و purpose مطابقت می‌دهد و وضعیت را برمی‌گرداند. رفتارهای جانبی مهم:
        - در صورت تطابق موفق: درخواست OTP درون یک تراکنش علامت‌گذاری می‌شود (mark_as_used)، ورودی کش مربوطه حذف می‌شود و شمارنده تلاش‌های ناموفق ریست می‌گردد.
        - در صورت تطابق ناموفق: تعداد تلاش‌های آن درخواست افزایش می‌یابد.
        - در صورت خطا در اجرا، یک پاسخ خطای داخلی بازگردانده می‌شود.
        
        پارامترها:
            phone_number (str): شماره موبایل ورودی (قبل از مقایسه قالب‌بندی می‌شود).
            otp_code (str): کد OTP که باید بررسی شود.
            purpose (str): هدف یا زمینه استفاده از OTP (پیش‌فرض: 'login').
        
        مقدار بازگشتی:
            Tuple[bool, dict]: 
                - اگر موفق باشد: (True, {'otp_request': <OTPRequest>, 'message': '...'}) بازمی‌گرداند.
                - اگر ناموفق باشد: (False, payload) که payload شامل کلیدهای خطا است. کدهای خطای ممکن:
                    - 'otp_not_found': درخواست معتبری پیدا نشد.
                    - 'otp_expired': کد منقضی شده است.
                    - 'otp_already_used': کد قبلاً استفاده شده است.
                    - 'max_attempts_exceeded': بیشینه تلاش‌ها مصرف شده است.
                    - 'cannot_verify': به‌دلایلی قابل تأیید نیست.
                    - 'invalid_otp': کد نادرست است؛ در این صورت ممکن است فیلد 'remaining_attempts' باقیمانده تلاش‌ها را ارائه دهد.
                    - 'internal_error': خطای سیستمی هنگام پردازش.
        
        توجهات پیاده‌سازی:
        - تابع ابتدا شماره را قالب‌بندی می‌کند و تلاش می‌کند درخواست مرتبط را از کش بازیابی کند؛ در غیر این صورت جدیدترین OTP غیر استفاده‌شده از پایگاه داده خوانده می‌شود.
        - عملیات علامت‌گذاری به‌عنوان استفاده‌شده در یک تراکنش انجام می‌شود تا از شرایط رقابتی جلوگیری شود.
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
        ارسال مجدد کد یک‌بارمصرف (OTP) با همان رفتار تابع send_otp.
        
        این متد فقط به send_otp واگذار می‌شود و یک OTP جدید می‌سازد در حالی که OTP‌های قبلی برای همان شماره و منظور (purpose) باطل می‌شوند. رفتار کامل شامل قالب‌بندی شماره، بررسی محدودیت نرخ، ایجاد رکورد جدید OTPRequest، ارسال از طریق `sms` یا `voice`، به‌روزرسانی شمارنده‌های نرخ و کش کردن شناسه OTP برای مدت کوتاه است.
        
        Parameters:
            phone_number (str): شماره تلفن مقصد (هر قالبی قبول می‌شود؛ درون تابع قالب‌بندی می‌شود).
            purpose (str): منظور استفاده از OTP (پیش‌فرض `'login'`). برای تفکیک OTP‌ها بین مقاصد مختلف استفاده می‌شود.
            sent_via (str): روش ارسال؛ `'sms'` یا `'voice'` (پیش‌فرض `'sms'`).
            ip_address (str | None): آدرس IP درخواست‌دهنده (اختیاری، برای لاگ/ثبت).
            user_agent (str | None): رشته User-Agent درخواست‌دهنده (اختیاری، برای لاگ/ثبت).
        
        Returns:
            Tuple[bool, dict]: زوج (success, payload). در صورت موفقیت `success=True` و payload شامل اطلاعاتی مانند `otp_id`، `expires_at` و پیام موفقیت است. در صورت خطا `success=False` و payload شامل کلید `error` و توضیحات مرتبط خواهد بود.
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
        """
        بررسی می‌کند آیا برای شماره تلفن مورد نظر ارسال OTP مجاز است؛ در صورت نیاز رکورد محدودسازی جدید ایجاد می‌شود.
        
        پارامترها:
            phone_number (str): شماره تلفن فرمت‌شده که محدودیت ارسال برای آن بررسی می‌شود.
        
        بازگشت:
            tuple[bool, str]: اولین عضو نشان‌دهندهٔ قابلیت ارسال (True = مجاز، False = مسدود/محدود)، عضو دوم پیغام یا جزئیات وضعیت محدودیت (مثلاً دلیل مسدودیت یا اطلاعات پنجره‌های زمانی).
        """
        rate_limit, created = OTPRateLimit.objects.get_or_create(
            phone_number=phone_number
        )
        
        return rate_limit.can_send_otp()
    
    def _update_rate_limit(self, phone_number: str):
        """
        شمارنده‌های محدودیت نرخ ارسال برای یک شماره را ایجاد یا به‌روز می‌کند.
        
        اگر رکورد محدودیت برای phone_number وجود نداشته باشد، یک ردیف جدید ایجاد می‌کند و سپس شمارنده‌های مربوطه
        (دقیقه‌ای/ساعتی/روزانه) را با فراخوانی متد increment_counters روی مدل OTPRateLimit افزایش می‌دهد.
        این عملیات می‌تواند وضعیت مسدودی را تغییر دهد (مثلاً پس از رسیدن به حد مجاز).
        
        Parameters:
            phone_number (str): شماره تلفن هدف (باید در فرمت استفاده‌شده در مدل ذخیره شود).
        """
        rate_limit, _ = OTPRateLimit.objects.get_or_create(
            phone_number=phone_number
        )
        rate_limit.increment_counters()
    
    def _add_failed_attempt(self, phone_number: str):
        """
        افزایش شمارش تلاش‌های ناموفق برای یک شماره تلفن و ایجاد رکورد محدودسازی در صورت نیاز.
        
        دسکریپشن:
        این تابع رکورد OTPRateLimit مربوط به phone_number را بازیابی می‌کند (در صورت نبود، آن را ایجاد می‌کند) و سپس شمارنده تلاش‌های ناموفق را با فراخوانی rate_limit.add_failed_attempt() افزایش می‌دهد. این عملیات وضعیت نرخ‌محدودسازی را در پایگاه‌داده به‌روزرسانی می‌کند و ممکن است به بلوکه شدن موقت ارسال/تأیید OTP برای آن شماره منجر شود.
        
        Parameters:
            phone_number (str): شماره تلفن هدف (بصورت فرمت‌شده) که تلاش ناموفق مربوط به آن ثبت می‌شود.
        
        Returns:
            None
        """
        rate_limit, _ = OTPRateLimit.objects.get_or_create(
            phone_number=phone_number
        )
        rate_limit.add_failed_attempt()
    
    def _reset_failed_attempts(self, phone_number: str):
        """
        ریست‌کننده شمارش تلاش‌های ناموفق برای شماره تلفن مشخص.
        
        این تابع مقدار فیلد `failed_attempts` در رکورد `OTPRateLimit` مربوط به `phone_number` را به صفر برمی‌گرداند و تغییر را ذخیره می‌کند. اگر هیچ رکوردی برای آن شماره وجود نداشته باشد، تابع بدون خطا و بدون اثر جانبی اجرا می‌شود (صرفاً عبور می‌کند).
        
        Parameters:
            phone_number (str): شماره تلفنی که شمارش تلاش‌های ناموفق آن باید ریست شود.
        """
        try:
            rate_limit = OTPRateLimit.objects.get(phone_number=phone_number)
            rate_limit.failed_attempts = 0
            rate_limit.save()
        except OTPRateLimit.DoesNotExist:
            pass
    
    def _invalidate_previous_otps(self, phone_number: str, purpose: str):
        """
        سابقهٔ OTPهای معلق برای یک شماره و هدف مشخص را باطل می‌کند (آن‌ها را به‌صورت استفاده‌شده علامت می‌زند).
        
        این متد تمامی رکوردهای OTPRequest که برای phone_number و purpose داده‌شده وجود دارند و هنوز استفاده‌نشده (is_used=False) هستند را در دیتابیس به‌روزرسانی کرده و فیلد is_used را برابر True قرار می‌دهد تا از استفادهٔ مجدد آن‌ها جلوگیری شود.
        
        Parameters:
            phone_number (str): شماره تلفن قالب‌بندی‌شده که OTPها به آن مربوط هستند.
            purpose (str): هدف یا کانتکست OTP (مثلاً 'login' یا 'password_reset') که برای تفکیک کدها استفاده می‌شود.
        """
        OTPRequest.objects.filter(
            phone_number=phone_number,
            purpose=purpose,
            is_used=False
        ).update(is_used=True)
    
    def _get_rate_limit_info(self, phone_number: str) -> dict:
        """
        بازگرداندن اطلاعات وضعیت محدودسازی ارسال (rate limit) برای یک شماره تلفن.
        
        این متد وضعیت فعلی پنجره‌های نرخ (دقیقه‌ای، ساعتی، روزانه) را برای شمارهٔ داده‌شده خوانده و با فراخوانی `check_and_update_windows()` مقدار شمارنده‌ها را به‌روز می‌کند، سپس یک دیکت شامل تعداد ارسال‌های باقیمانده در هر پنجره و وضعیت مسدودی برمی‌گرداند.
        
        Parameters:
            phone_number (str): شماره تلفن فرمت‌شده‌ای که باید وضعیت rate limit آن بررسی شود.
        
        Returns:
            dict: دیکشنری با کلیدهای زیر:
                - minute_remaining (int): تعداد ارسال‌های باقیمانده در پنجرهٔ یک دقیقه (همیشه >= 0).
                - hour_remaining (int): تعداد ارسال‌های باقیمانده در پنجرهٔ یک ساعت (همیشه >= 0).
                - daily_remaining (int): تعداد ارسال‌های باقیمانده در پنجرهٔ یک روز (همیشه >= 0).
                - is_blocked (bool): نشان‌دهندهٔ اینکه شماره در حال حاضر مسدود است یا خیر.
                - blocked_until (str|None): زمان پایان مسدودی به صورت ISO-8601 یا None در صورت عدم مسدودی.
        
        Notes:
            - متد ممکن است رکورد OTPRateLimit را به‌روزرسانی کند (از طریق `check_and_update_windows()`)، بنابراین این فراخوانی اثر جانبی روی داده‌ها دارد.
            - اگر رکورد rate limit برای شماره وجود نداشته باشد، مقادیر پیش‌فرض (یک ارسال برای دقیقه، پنج برای ساعت، ده برای روز) بازگردانده می‌شود.
        """
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
        """
        پاکسازی درخواست‌های OTP که بیش از ۲۴ ساعت از ایجادشان گذشته‌اند و بازگرداندن تعداد حذف‌شده.
        
        این تابع رکوردهای مدل OTPRequest را که فیلد created_at آن‌ها کمتر از زمان کنونی منهای ۲۴ ساعت است حذف می‌کند. در صورت حذف شدن هر رکوردی، تعداد حذف‌شده (int) برگردانده می‌شود و همچنین در صورت حذف‌ شدن لاگ اطلاع‌رسانی صادر می‌شود.
        """
        cutoff = timezone.now() - timedelta(hours=24)
        deleted_count = OTPRequest.objects.filter(
            created_at__lt=cutoff
        ).delete()[0]
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} expired OTP requests")
        
        return deleted_count