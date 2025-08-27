"""
سرویس یکپارچه کاوه‌نگار برای ارسال پیامک
Kavenegar Service for SMS Sending
"""

from kavenegar import KavenegarAPI, APIException, HTTPException
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class KavenegarService:
    """
    سرویس ارسال پیامک با کاوه‌نگار
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'KAVENEGAR_API_KEY', None)
        if not self.api_key:
            raise ValueError("KAVENEGAR_API_KEY not found in settings")
        
        self.api = KavenegarAPI(self.api_key)
        self.sender = getattr(settings, 'KAVENEGAR_SENDER', None)
        self.otp_template = getattr(settings, 'KAVENEGAR_OTP_TEMPLATE', 'verify')
    
    def send_otp(self, phone_number: str, otp_code: str, template: str = None) -> dict:
        """
        ارسال کد OTP
        
        Args:
            phone_number: شماره موبایل گیرنده
            otp_code: کد OTP
            template: نام قالب (اختیاری)
            
        Returns:
            dict: نتیجه ارسال شامل message_id
        """
        try:
            # استفاده از template پیش‌فرض اگر مشخص نشده
            if not template:
                template = self.otp_template
            
            # ارسال با استفاده از verify API (برای OTP)
            params = {
                'receptor': phone_number,
                'token': otp_code,
                'template': template
            }
            
            # اگر token2 یا token3 نیاز است
            # params['token2'] = 'مقدار'
            # params['token3'] = 'مقدار'
            
            response = self.api.verify_lookup(params)
            
            # لاگ موفقیت
            logger.info(
                f"OTP sent successfully to {phone_number}, "
                f"message_id: {response['messageid']}"
            )
            
            return {
                'success': True,
                'message_id': str(response['messageid']),
                'status': response['status'],
                'status_text': response['statustext']
            }
            
        except APIException as e:
            # خطای API کاوه‌نگار
            logger.error(f"Kavenegar API error: {e}")
            return {
                'success': False,
                'error': 'خطا در ارسال پیامک',
                'error_code': getattr(e, 'status', None),
                'error_detail': str(e)
            }
            
        except HTTPException as e:
            # خطای HTTP
            logger.error(f"Kavenegar HTTP error: {e}")
            return {
                'success': False,
                'error': 'خطا در ارتباط با سرور پیامک',
                'error_detail': str(e)
            }
            
        except Exception as e:
            # خطای عمومی
            logger.error(f"Unexpected error in Kavenegar service: {e}")
            return {
                'success': False,
                'error': 'خطای غیرمنتظره در ارسال پیامک',
                'error_detail': str(e)
            }
    
    def send_simple_sms(self, phone_number: str, message: str) -> dict:
        """
        ارسال پیامک ساده (غیر OTP)
        
        Args:
            phone_number: شماره موبایل گیرنده
            message: متن پیام
            
        Returns:
            dict: نتیجه ارسال
        """
        try:
            params = {
                'receptor': phone_number,
                'message': message
            }
            
            if self.sender:
                params['sender'] = self.sender
            
            response = self.api.sms_send(params)
            
            logger.info(
                f"SMS sent successfully to {phone_number}, "
                f"message_id: {response['messageid']}"
            )
            
            return {
                'success': True,
                'message_id': str(response['messageid']),
                'status': response['status']
            }
            
        except Exception as e:
            logger.error(f"Error sending simple SMS: {e}")
            return {
                'success': False,
                'error': 'خطا در ارسال پیامک',
                'error_detail': str(e)
            }
    
    def get_message_status(self, message_id: str) -> dict:
        """
        دریافت وضعیت پیام ارسال شده
        
        Args:
            message_id: شناسه پیام
            
        Returns:
            dict: وضعیت پیام
        """
        try:
            response = self.api.sms_status({'messageid': message_id})
            
            return {
                'success': True,
                'status': response['status'],
                'statustext': response['statustext']
            }
            
        except Exception as e:
            logger.error(f"Error getting message status: {e}")
            return {
                'success': False,
                'error': 'خطا در دریافت وضعیت پیام',
                'error_detail': str(e)
            }
    
    def send_voice_otp(self, phone_number: str, otp_code: str) -> dict:
        """
        ارسال OTP به صورت تماس صوتی
        
        Args:
            phone_number: شماره موبایل
            otp_code: کد OTP
            
        Returns:
            dict: نتیجه ارسال
        """
        try:
            # تبدیل کد به متن قابل خواندن
            # مثلاً 123456 به "یک دو سه چهار پنج شش"
            spoken_code = ' '.join(otp_code)
            
            message = f"کد تأیید شما: {spoken_code}"
            
            params = {
                'receptor': phone_number,
                'message': message
            }
            
            response = self.api.call_maketts(params)
            
            logger.info(
                f"Voice OTP sent successfully to {phone_number}, "
                f"message_id: {response['messageid']}"
            )
            
            return {
                'success': True,
                'message_id': str(response['messageid']),
                'status': response['status']
            }
            
        except Exception as e:
            logger.error(f"Error sending voice OTP: {e}")
            return {
                'success': False,
                'error': 'خطا در برقراری تماس صوتی',
                'error_detail': str(e)
            }
    
    @staticmethod
    def format_phone_number(phone_number: str) -> str:
        """
        فرمت کردن شماره تلفن برای کاوه‌نگار
        
        Args:
            phone_number: شماره تلفن
            
        Returns:
            str: شماره فرمت شده
        """
        # حذف فاصله‌ها و کاراکترهای اضافی
        phone_number = phone_number.strip().replace(' ', '').replace('-', '')
        
        # حذف +98 یا 0098 از ابتدا
        if phone_number.startswith('+98'):
            phone_number = '0' + phone_number[3:]
        elif phone_number.startswith('0098'):
            phone_number = '0' + phone_number[4:]
        elif phone_number.startswith('98'):
            phone_number = '0' + phone_number[2:]
        
        return phone_number