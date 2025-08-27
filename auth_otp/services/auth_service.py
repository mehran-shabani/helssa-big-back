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
        ایجاد کاربر جدید یا دریافت کاربر موجود
        
        Args:
            phone_number: شماره موبایل
            user_type: نوع کاربر
            
        Returns:
            Tuple[User, bool]: (کاربر، آیا جدید ایجاد شد)
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
        تولید توکن‌های JWT
        
        Args:
            user: کاربر
            
        Returns:
            dict: توکن‌ها و اطلاعات
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
        ایجاد رکورد تأییدیه
        
        Args:
            otp_request: درخواست OTP
            user: کاربر
            tokens: توکن‌ها
            device_id: شناسه دستگاه
            device_name: نام دستگاه
            session_key: کلید نشست
            
        Returns:
            OTPVerification: رکورد تأییدیه
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
        تازه‌سازی Access Token
        
        Args:
            refresh_token: Refresh Token
            
        Returns:
            Tuple[bool, dict]: (موفقیت، توکن جدید/خطا)
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
        مسدود کردن توکن
        
        Args:
            token: توکن
            token_type: نوع توکن
            user: کاربر
            reason: دلیل
            
        Returns:
            bool: موفقیت
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
        خروج کاربر از سیستم
        
        Args:
            user: کاربر
            refresh_token: توکن refresh برای مسدود کردن
            logout_all: خروج از همه دستگاه‌ها
            
        Returns:
            bool: موفقیت
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
        دریافت نشست‌های فعال کاربر
        
        Args:
            user: کاربر
            
        Returns:
            list: لیست نشست‌های فعال
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
        لغو یک نشست خاص
        
        Args:
            user: کاربر
            session_id: شناسه نشست
            
        Returns:
            bool: موفقیت
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
        """پاکسازی توکن‌های منقضی از blacklist"""
        deleted_count = TokenBlacklist.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()[0]
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} expired blacklisted tokens")
        
        return deleted_count