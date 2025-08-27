"""
سرویس مدیریت توکن‌ها و احراز هویت
Token Management and Authentication Service
"""

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from typing import Tuple, Optional, Dict
import jwt
import uuid
import logging

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from ..models import OTPVerification, TokenBlacklist

logger = logging.getLogger(__name__)
User = get_user_model()


class AuthService:
    """
    سرویس مدیریت احراز هویت و توکن‌ها
    """
    
    @staticmethod
    def create_user_if_not_exists(phone_number: str, user_type: str = 'patient') -> Tuple[User, bool]:
        """
        یک کاربر را با username برابر phone_number بازیابی می‌کند یا در صورت نبود، یک کاربر فعال جدید می‌سازد.
        
        شرح:
        - تلاش می‌کند کاربری را با username برابر شمارهٔ موبایل پیدا کند؛ در صورت وجود، همان کاربر بازگردانده می‌شود.
        - اگر کاربر پیدا نشود، یک کاربر جدید با username=phone_number، user_type مشخص و is_active=True ایجاد می‌کند و آن را بازمی‌گرداند.
        - در صورت ایجاد کاربر جدید، یک پیام اطلاعاتی در لاگ ثبت می‌شود.
        
        پارامترها:
            phone_number (str): شماره موبایل که به‌عنوان username استفاده می‌شود.
            user_type (str): نوع کاربر جدید در صورت ایجاد (پیش‌فرض 'patient').
        
        بازگشتی:
            Tuple[User, bool]: تاپل شامل شیء User و یک بولن که نشان می‌دهد آیا کاربر جدید ایجاد شده (True) یا کاربر موجود بازگردانده شده (False).
        """
        try:
            user = User.objects.get(username=phone_number)
            is_new = False
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=phone_number,
                user_type=user_type,
                is_active=True
            )
            is_new = True
            logger.info(f"New user created: {phone_number}, type: {user_type}")
        
        return user, is_new
    
    @staticmethod
    def generate_tokens(user: User) -> Dict[str, any]:
        """
        تولید توکن‌های JWT (دسترسی و رفرش) برای یک کاربر و بازگرداندن متادیتای مرتبط.
        
        توضیحات:
            این تابع یک RefreshToken برای کاربر می‌سازد، دو claim اضافی `user_type` و `phone_number`
            را به توکن رفرش اضافه می‌کند و سپس یک توکن دسترسی (access) و رفرش (refresh) به‌صورت رشته‌ای
            بازمی‌گرداند. همچنین زمان عمر توکن دسترسی به ثانیه و زمان پایان اعتبار هر دو توکن به‌صورت
            ISO-8601 ارائه می‌شود.
        
        پارامترها:
            user: نمونهٔ مدل User که برای آن توکن‌ها تولید می‌شود. فیلد `user_type` و `username`
                  (شماره تلفن) از این شیء برای افزودن claimها استفاده می‌شود.
        
        بازگشتی:
            dict شامل کلیدهای زیر:
              - access (str): توکن دسترسی به‌صورت رشته.
              - refresh (str): توکن رفرش به‌صورت رشته.
              - token_type (str): نوع توکن (مثلاً 'Bearer').
              - expires_in (int): مدت زمان اعتبار توکن دسترسی بر حسب ثانیه.
              - access_expires_at (str): زمان پایان اعتبار توکن دسترسی به‌صورت رشته ISO-8601.
              - refresh_expires_at (str): زمان پایان اعتبار توکن رفرش به‌صورت رشته ISO-8601.
        """
        refresh = RefreshToken.for_user(user)
        
        # افزودن claims اضافی
        refresh['user_type'] = user.user_type
        refresh['phone_number'] = user.username
        
        # محاسبه زمان انقضا
        access_lifetime = getattr(
            settings,
            'SIMPLE_JWT',
            {}
        ).get('ACCESS_TOKEN_LIFETIME', timedelta(minutes=5))
        
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'token_type': 'Bearer',
            'expires_in': int(access_lifetime.total_seconds()),
            'access_expires_at': (timezone.now() + access_lifetime).isoformat(),
            'refresh_expires_at': (
                timezone.now() + 
                getattr(settings, 'SIMPLE_JWT', {}).get(
                    'REFRESH_TOKEN_LIFETIME',
                    timedelta(days=7)
                )
            ).isoformat()
        }
    
    @staticmethod
    def create_verification_record(
        otp_request,
        user: User,
        tokens: Dict[str, str],
        device_id: str = None,
        device_name: str = None,
        session_key: str = None
    ) -> OTPVerification:
        """
        ایجاد و ثبت یک رکورد OTPVerification برای جلسه ورود کاربر و بازگرداندن نمونه ایجاد‌شده.
        
        یک رکورد OTPVerification جدید می‌سازد که به درخواست OTP و کاربر پیوند می‌خورد و توکن‌های دسترسی و تازه‌سازی را ذخیره می‌کند. اگر device_id داده نشده باشد یک UUID جدید تولید می‌شود، device_name در صورت نبودن برابر با `'Unknown Device'` قرار می‌گیرد و session_key به‌صورت پیش‌فرض رشته خالی خواهد بود.
        
        Parameters:
            otp_request: شیء مربوط به درخواست OTP (حاوی اطلاعاتی مثل ip_address و user_agent) که با رکورد تأیید مرتبط خواهد شد.
            user: شیء کاربر مرتبط با این جلسه.
            tokens: دیکشنری شامل حداقل کلیدهای `'access'` و `'refresh'` با مقادیر توکن‌های متناظر.
            device_id: (اختیاری) شناسه دستگاه؛ در صورت عدم مقداردهی، مقدار تصادفی UUID تولید می‌شود.
            device_name: (اختیاری) نام دستگاه؛ در صورت عدم مقداردهی، `'Unknown Device'` استفاده می‌شود.
            session_key: (اختیاری) کلید نشست/سشن که به رکورد اضافه می‌شود؛ پیش‌فرض رشته خالی است.
        
        Returns:
            OTPVerification: نمونه‌ی رکورد تأییدیه ذخیره‌شده در دیتابیس.
        """
        verification = OTPVerification.objects.create(
            otp_request=otp_request,
            user=user,
            access_token=tokens['access'],
            refresh_token=tokens['refresh'],
            device_id=device_id or str(uuid.uuid4()),
            device_name=device_name or 'Unknown Device',
            session_key=session_key or ''
        )
        
        logger.info(
            f"Verification record created for user: {user.username}, "
            f"device: {device_name}"
        )
        
        return verification
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> Tuple[bool, Dict[str, any]]:
        """
        تازه‌سازی توکن دسترسی (Access Token) با استفاده از یک Refresh Token.
        
        این تابع یک Refresh Token را اعتبارسنجی می‌کند، اطمینان می‌دهد که توکن در فهرست سیاه نیست و کاربر مربوطه وجود دارد و فعال است، سپس یک Access Token جدید می‌سازد. بسته به تنظیمات SIMPLE_JWT می‌تواند عمل «چرخش» (rotation) را انجام دهد: توکن رفرش قدیمی را (در صورت فعال بودن BLACKLIST_AFTER_ROTATION) در لیست سیاه قرار می‌دهد و یک Refresh Token جدید برای کاربر صادر می‌کند. در صورت موفقیت، مقدار بازگشتی شامل توکن‌های مربوطه و زمان انقضای Access به ثانیه است؛ در غیر این‌صورت یک دیکشنری خطا با کد و پیام مناسب بازگردانده می‌شود.
        
        پارامترها:
            refresh_token (str): رشته‌ی Refresh Token که باید برای صدور Access جدید استفاده شود.
        
        مقدار بازگشتی:
            Tuple[bool, Dict[str, any]]: 
                - در صورت موفقیت: (True, payload) که payload شامل کلیدهای زیر است:
                    - 'access' (str): Access Token جدید
                    - 'refresh' (str, اختیاری): Refresh Token جدید (در صورت فعال بودن چرخش)
                    - 'token_type' (str): معمولاً 'Bearer'
                    - 'expires_in' (int): زمان باقی‌مانده‌ی اعتبار Access به ثانیه
                - در صورت خطا: (False, error_dict) که error_dict حداقل شامل:
                    - 'error' (str): کد خطا مانند 'token_blacklisted', 'user_inactive', 'user_not_found', 'invalid_token', 'internal_error'
                    - 'message' (str): توضیح کوتاه به فارسی
        
        حالات خطا مهم:
            - اگر توکن در لیست سیاه باشد، خطای 'token_blacklisted' بازگردانده می‌شود.
            - اگر کاربر مرتبط وجود نداشته یا غیرفعال باشد، خطاهای 'user_not_found' یا 'user_inactive' بازگردانده می‌شوند.
            - در صورت نامعتبر بودن توکن، 'invalid_token' بازگردانده می‌شود.
            - خطاهای داخلی سیستم با 'internal_error' گزارش می‌شوند.
        """
        try:
            # بررسی blacklist
            if TokenBlacklist.is_blacklisted(refresh_token):
                return False, {
                    'error': 'token_blacklisted',
                    'message': 'این توکن مسدود شده است'
                }
            
            # تولید توکن جدید
            refresh = RefreshToken(refresh_token)
            
            # بررسی اعتبار کاربر
            user_id = refresh.payload.get('user_id')
            try:
                user = User.objects.get(id=user_id)
                if not user.is_active:
                    return False, {
                        'error': 'user_inactive',
                        'message': 'حساب کاربری غیرفعال است'
                    }
            except User.DoesNotExist:
                return False, {
                    'error': 'user_not_found',
                    'message': 'کاربر یافت نشد'
                }
            
            # تولید access token جدید
            new_access = refresh.access_token
            
            # Rotate refresh token if configured
            if getattr(settings, 'SIMPLE_JWT', {}).get('ROTATE_REFRESH_TOKENS', True):
                # مسدود کردن refresh token قدیمی
                if getattr(settings, 'SIMPLE_JWT', {}).get('BLACKLIST_AFTER_ROTATION', True):
                    AuthService.blacklist_token(
                        refresh_token,
                        'refresh',
                        user,
                        'Token rotation'
                    )
                
                # تولید refresh token جدید
                new_refresh = RefreshToken.for_user(user)
                new_refresh['user_type'] = user.user_type
                new_refresh['phone_number'] = user.username
                
                return True, {
                    'access': str(new_access),
                    'refresh': str(new_refresh),
                    'token_type': 'Bearer',
                    'expires_in': int(
                        getattr(settings, 'SIMPLE_JWT', {}).get(
                            'ACCESS_TOKEN_LIFETIME',
                            timedelta(minutes=5)
                        ).total_seconds()
                    )
                }
            else:
                return True, {
                    'access': str(new_access),
                    'token_type': 'Bearer',
                    'expires_in': int(
                        getattr(settings, 'SIMPLE_JWT', {}).get(
                            'ACCESS_TOKEN_LIFETIME',
                            timedelta(minutes=5)
                        ).total_seconds()
                    )
                }
                
        except TokenError as e:
            logger.error(f"Token refresh error: {e}")
            return False, {
                'error': 'invalid_token',
                'message': 'توکن نامعتبر است'
            }
        except Exception as e:
            logger.error(f"Unexpected error in refresh_access_token: {e}")
            return False, {
                'error': 'internal_error',
                'message': 'خطای سیستمی'
            }
    
    @staticmethod
    def blacklist_token(
        token: str,
        token_type: str,
        user: User,
        reason: str = ''
    ) -> bool:
        """
        توکن مشخص را در جدول TokenBlacklist ذخیره و مسدود می‌کند.
        
        این تابع یک رکورد TokenBlacklist با فیلدهای token، token_type، user، reason و expires_at ایجاد می‌کند.
        مقدار expires_at بر اساس نوع توکن از پیکربندی settings.SIMPLE_JWT گرفته می‌شود:
        - برای token_type == 'access' از ACCESS_TOKEN_LIFETIME (پیش‌فرض ۵ دقیقه) استفاده می‌شود.
        - در غیر این صورت از REFRESH_TOKEN_LIFETIME (پیش‌فرض ۷ روز) استفاده می‌شود.
        
        پارامترها:
            token (str): مقدار رشته‌ای توکن که باید مسدود شود.
            token_type (str): نوع توکن؛ مقدارهای مورد انتظار: 'access' یا 'refresh' (هر مقدار دیگر به‌عنوان refresh در نظر گرفته می‌شود).
            user (User): نمونه کاربر متعلق به توکن (برای ثبت در رکورد blacklist).
            reason (str, optional): دلیل مسدودسازی برای نگهداری لاگ/پژوهش.
        
        بازگشت:
            bool: در صورت ایجاد موفق رکورد True و در صورت بروز خطا (مثلاً خطای پایگاه‌داده) False بازمی‌گرداند.
        """
        try:
            # محاسبه زمان انقضا
            if token_type == 'access':
                expires_at = timezone.now() + getattr(
                    settings, 'SIMPLE_JWT', {}
                ).get('ACCESS_TOKEN_LIFETIME', timedelta(minutes=5))
            else:  # refresh
                expires_at = timezone.now() + getattr(
                    settings, 'SIMPLE_JWT', {}
                ).get('REFRESH_TOKEN_LIFETIME', timedelta(days=7))
            
            TokenBlacklist.objects.create(
                token=token,
                token_type=token_type,
                user=user,
                reason=reason,
                expires_at=expires_at
            )
            
            logger.info(
                f"Token blacklisted: type={token_type}, "
                f"user={user.username}, reason={reason}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error blacklisting token: {e}")
            return False
    
    @staticmethod
    def logout(user: User, refresh_token: str = None, logout_all: bool = False) -> bool:
        """
        خروج کاربر از سیستم؛ هم‌زمان از یک دستگاه یا تمام دستگاه‌ها را مدیریت می‌کند.
        
        این متد توکن‌های مرتبط با جلسه‌های فعال کاربر را بلک‌لیست کرده و رکوردهای OTPVerification مربوط را غیرفعال می‌کند. رفتارها:
        - اگر logout_all=True باشد: همهٔ OTPVerification‌های فعال کاربر پردازش شده و هر دو توکن access و refresh بلک‌لیست و آن رکوردها غیرفعال می‌شوند.
        - در غیر این صورت، اگر refresh_token تامین شده باشد: فقط آن refresh token بلک‌لیست شده و رکورد OTPVerification متناظر غیرفعال می‌گردد.
        - اگر هیچ refresh_token‌ای داده نشود و logout_all=False، تغییری انجام نمی‌دهد (ولی موفقیت را برمی‌گرداند).
        
        Parameters:
            user: نمونهٔ مدل Django User برای کاربری که باید خارج شود.
            refresh_token (str, optional): در صورت ارائه، فقط همان جلسه/توکن خاص بلک‌لیست و غیرفعال می‌شود.
            logout_all (bool, optional): اگر True باشد، همهٔ جلسات فعال کاربر لغو می‌شوند.
        
        Returns:
            bool: True در صورت اجرای موفق عملیات (حتی اگر موردی برای لغو وجود نداشته باشد)، و False در صورت بروز خطا.
        """
        try:
            if logout_all:
                # مسدود کردن همه توکن‌های فعال کاربر
                active_verifications = OTPVerification.objects.filter(
                    user=user,
                    is_active=True
                )
                
                for verification in active_verifications:
                    # مسدود کردن access token
                    AuthService.blacklist_token(
                        verification.access_token,
                        'access',
                        user,
                        'Logout all devices'
                    )
                    
                    # مسدود کردن refresh token
                    AuthService.blacklist_token(
                        verification.refresh_token,
                        'refresh',
                        user,
                        'Logout all devices'
                    )
                    
                    # غیرفعال کردن verification
                    verification.deactivate()
                
                logger.info(f"User {user.username} logged out from all devices")
                
            elif refresh_token:
                # مسدود کردن توکن خاص
                AuthService.blacklist_token(
                    refresh_token,
                    'refresh',
                    user,
                    'User logout'
                )
                
                # غیرفعال کردن verification مربوطه
                OTPVerification.objects.filter(
                    user=user,
                    refresh_token=refresh_token,
                    is_active=True
                ).update(is_active=False)
                
                logger.info(f"User {user.username} logged out from single device")
            
            return True
            
        except Exception as e:
            logger.error(f"Error in logout: {e}")
            return False
    
    @staticmethod
    def get_active_sessions(user: User) -> list:
        """
        لیستی از نشست‌های فعال (OTPVerification) مرتبط با کاربر را برمی‌گرداند.
        
        این تابع تمام رکوردهای OTPVerification فعال مربوط به کاربر را مرتب‌شده بر اساس زمان تایید (جدیدترین ابتدا) خوانده و برای هر نشست اطلاعاتی شامل شناسه نشست، شناسه و نام دستگاه، زمان تایید (ISO)، آخرین فعالیت (در حال حاضر برابر با زمان تایید) و اطلاعات شبکه/عامل کاربر را بازمی‌گرداند. مناسب برای نمایش جلسات فعال کاربر در پنل مدیریت یا صفحه جلسات کاربر.
        
        Parameters:
            user (User): نمونه مدل کاربر Django که نشست‌های فعال آن باید بازیابی شود.
        
        Returns:
            list: لیستی از دیکشنری‌ها که هر کدام نماینده یک نشست فعال هستند با کلیدهای:
                - id (str): شناسه نشست (UUID) به صورت رشته
                - device_id (str): شناسه دستگاه
                - device_name (str): نام یا توصیف دستگاه
                - verified_at (str): زمان تایید نشست به فرمت ISO 8601
                - last_activity (str): زمان آخرین فعالیت به فرمت ISO 8601 (فعلاً برابر با verified_at)
                - ip_address (str): آدرس IP ثبت‌شده برای درخواست OTP
                - user_agent (str): رشته User-Agent ثبت‌شده برای درخواست OTP
        """
        sessions = []
        
        verifications = OTPVerification.objects.filter(
            user=user,
            is_active=True
        ).order_by('-verified_at')
        
        for verification in verifications:
            sessions.append({
                'id': str(verification.id),
                'device_id': verification.device_id,
                'device_name': verification.device_name,
                'verified_at': verification.verified_at.isoformat(),
                'last_activity': verification.verified_at.isoformat(),  # TODO: track last activity
                'ip_address': verification.otp_request.ip_address,
                'user_agent': verification.otp_request.user_agent
            })
        
        return sessions
    
    @staticmethod
    def revoke_session(user: User, session_id: str) -> bool:
        """
        نشست مشخص کاربر را با مسدود کردن توکن‌های مرتبط و غیرفعال‌سازی رکورد OTPVerification لغو می‌کند.
        
        این تابع توکن‌های access و refresh مربوط به نشست را در TokenBlacklist ثبت می‌کند (با دلیل "Session revoked") و سپس رکورد OTPVerification مربوطه را غیرفعال می‌کند. اگر نشست با id داده‌شده وجود نداشته باشد یا از قبل غیرفعال باشد، تابع False بازمی‌گرداند. در صورت موفقیت True بازمی‌گرداند. هر خطای غیرمنتظره نیز باعث بازگشت False می‌شود.
        
        Parameters:
            user (User): کاربر مالک نشست.
            session_id (str): شناسه یکتا (UUID یا PK) رکورد OTPVerification که باید لغو شود.
        
        Returns:
            bool: True در صورت موفقیت لغو نشست؛ False اگر نشست یافت نشد یا خطا رخ داد.
        """
        try:
            verification = OTPVerification.objects.get(
                id=session_id,
                user=user,
                is_active=True
            )
            
            # مسدود کردن توکن‌ها
            AuthService.blacklist_token(
                verification.access_token,
                'access',
                user,
                'Session revoked'
            )
            
            AuthService.blacklist_token(
                verification.refresh_token,
                'refresh',
                user,
                'Session revoked'
            )
            
            # غیرفعال کردن verification
            verification.deactivate()
            
            logger.info(
                f"Session revoked: user={user.username}, "
                f"session={session_id}"
            )
            
            return True
            
        except OTPVerification.DoesNotExist:
            logger.warning(
                f"Session not found for revocation: "
                f"user={user.username}, session={session_id}"
            )
            return False
        except Exception as e:
            logger.error(f"Error revoking session: {e}")
            return False
    
    @staticmethod
    def cleanup_expired_blacklist():
        """
        یکپارچه‌سازی و حذف ورودی‌های منقضی‌شده از جدول TokenBlacklist.
        
        این تابع رکوردهای TokenBlacklist را که فیلد `expires_at` آنها کمتر از زمان جاری (timezone.now()) است حذف می‌کند و تعداد رکوردهای حذف‌شده را برمی‌گرداند. حذف به‌صورت دائمی در دیتابیس انجام می‌شود؛ در صورت حذف شدن هر رکورد، یک پیام لاگ اطلاع‌رسانی ثبت می‌شود.
        
        Returns:
            int: تعداد رکوردهای حذف‌شده از TokenBlacklist.
        """
        deleted_count = TokenBlacklist.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()[0]
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} expired blacklisted tokens")
        
        return deleted_count