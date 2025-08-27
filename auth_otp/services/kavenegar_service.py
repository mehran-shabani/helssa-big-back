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
        """
        مقداردهی اولیه سرویس کاوه‌نگار: کلید API را از تنظیمات می‌خواند، نمونهٔ KavenegarAPI را می‌سازد و مقادیر sender و الگوی OTP را مقداردهی می‌کند.
        
        جزئیات:
        - از تنظیمات Django مقدار KAVENEGAR_API_KEY را می‌خواند و آن را در self.api_key قرار می‌دهد. در صورت نبودن این مقدار، ValueError با پیام "KAVENEGAR_API_KEY not found in settings" پرتاب می‌شود.
        - با استفاده از api_key یک نمونهٔ KavenegarAPI در self.api ساخته می‌شود (وابستگی به کلاینت کتابخانه ka‎venegar).
        - مقدار فرستنده را از KAVENEGAR_SENDER می‌خواند و در self.sender قرار می‌دهد (در صورت عدم وجود None خواهد بود).
        - الگوی پیش‌فرض OTP را از KAVENEGAR_OTP_TEMPLATE می‌خواند و در self.otp_template قرار می‌دهد؛ اگر این تنظیم موجود نباشد مقدار پیش‌فرض 'verify' استفاده می‌شود.
        
        عوارض جانبی:
        - پرتاب ValueError در صورت نبود KAVENEGAR_API_KEY.
        - ایجاد و ذخیرهٔ نمونهٔ کلاینت KavenegarAPI در وضعیت شیء.
        """
        self.api_key = getattr(settings, 'KAVENEGAR_API_KEY', None)
        if not self.api_key:
            raise ValueError("KAVENEGAR_API_KEY not found in settings")
        
        self.api = KavenegarAPI(self.api_key)
        self.sender = getattr(settings, 'KAVENEGAR_SENDER', None)
        self.otp_template = getattr(settings, 'KAVENEGAR_OTP_TEMPLATE', 'verify')
    
    def send_otp(self, phone_number: str, otp_code: str, template: str = None) -> dict:
        """
        ارسال کد اعتبارسنجی (OTP) با استفاده از سرویس Kavenegar.
        
        این متد یک کد OTP را با API تایید کاوه‌نگار (verify_lookup) به شماره‌ی مقصد ارسال می‌کند. اگر آرگومان template مشخص نشده باشد، قالب پیش‌فرض سرویس (self.otp_template) استفاده می‌شود.
        
        Parameters:
            phone_number (str): شماره دریافت‌کننده؛ باید در قالبی که سرویس کاوه‌نگار می‌پذیرد باشد (می‌توان از staticmethod format_phone_number برای نرمال‌سازی استفاده کرد).
            otp_code (str): رشته‌ی کد OTP که باید ارسال شود.
            template (str, optional): نام قالب verify برای ارسال OTP؛ در صورت عدم تعیین، از self.otp_template استفاده می‌شود.
        
        Returns:
            dict: ساختاری با اطلاعات نتیجه ارسال. میدان‌های ممکن:
                - success (bool): نشان‌دهندهٔ موفقیت درخواست.
                - message_id (str): شناسهٔ پیام برگشتی از API (در صورت موفقیت).
                - status: کد وضعیت بازگشتی از API (در صورت موفقیت).
                - status_text (str): توضیح وضعیت از API (در صورت موفقیت).
                - error (str): پیام خطای قابل‌نمایش به فارسی (در صورت شکست).
                - error_code: کد خطای API اگر موجود باشد.
                - error_detail (str): جزئیات خطا (متن استثناء) برای عیب‌یابی.
        
        توجه: متد تمام استثناء‌ها را داخل خود هندل می‌کند و به‌جای پرتاب استثناء، نتیجهٔ خطا را به‌صورت دیکشنری بازمی‌گرداند.
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
        ارسال یک پیامک متنی ساده (غیر OTP) به گیرنده مشخص با استفاده از کلاینت Kavenegar.
        
        توضیحات:
            پیام با استفاده از متد sms_send کلاینت Kavenegar ارسال می‌شود. در صورت تنظیم بودن صفت sender در نمونهٔ سرویس، آن به پارامترهای ارسال اضافه خواهد شد. تابع خطاها را داخل خود مدیریت کرده و به‌جای پرتاب استثنا، یک دیکشنری وضعیت بازمی‌گرداند.
        
        پارامترها:
            phone_number (str): شماره گیرنده؛ باید به شکلی که توسط سرویس پیامکی پذیرفته می‌شود (مثلاً فرمت محلی/بین‌المللی) ارائه شود.
            message (str): متن پیام ارسالی.
        
        مقدار بازگشتی:
            dict: ساختاری با کلیدهای زیر
                - success (bool): نشان‌دهندهٔ موفقیت عملیات.
                - message_id (str): شناسهٔ پیام در صورت موفقیت.
                - status: وضعیت بازگشتی از API در صورت موفقیت.
                - error (str): متن خطا به زبان فارسی در صورت عدم موفقیت.
                - error_detail (str): توضیحات تکمیلی خطا (رشتهٔ نمایشی از استثنا) در صورت عدم موفقیت.
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
        وضعیت یک پیام ارسال‌شده را از سرویس کاوِن‌نگار بازیابی می‌کند.
        
        جزئیات:
        - این متد از API داخلی (self.api.sms_status) برای دریافت وضعیت پیام با شناسهٔ ارائه‌شده استفاده می‌کند.
        - در صورت موفقیت، دیکشنری شامل وضعیت بازگردانده می‌شود.
        - در صورت بروز هر خطا، خطا لاگ شده و دیکشنری حاوی اطلاعات خطا بازگردانده می‌شود.
        
        Parameters:
            message_id (str): شناسهٔ پیام که توسط کاوِن‌نگار هنگام ارسال پیام بازگردانده شده است.
        
        Returns:
            dict: در حالت موفق:
                {
                    'success': True,
                    'status': <کد وضعیت از پاسخ کاوِن‌نگار>,
                    'statustext': <توضیح متنی وضعیت>
                }
                در حالت خطا:
                {
                    'success': False,
                    'error': 'خطا در دریافت وضعیت پیام',
                    'error_detail': <رشتهٔ توضیح خطای داخلی>
                }
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
        ارسال کد یک‌بارمصرف (OTP) به‌صورت تماس صوتی و بازگرداندن نتیجهٔ ساختاری.
        
        این متد کد عددی را به شکل قابل خواندن برای تولید پیام صوتی آماده می‌کند، درخواست ایجاد تماس صوتی با متن پیام را به سرویس کاون‌نگار می‌فرستد و نتیجهٔ عملیات را به‌صورت دیکشنری بازمی‌گرداند. در حالت موفق مقدار‌های `success`, `message_id` و `status` برگشت داده می‌شوند؛ در صورت بروز خطا مقدار `success` برابر False و کلیدهای `error` و `error_detail` برای توضیحات خطا برگردانده می‌شوند.
        
        Parameters:
            phone_number (str): شماره گیرنده به فرمت مورد انتظار (پیش از ارسال معمولاً با `format_phone_number` نرمال‌سازی شود).
            otp_code (str): کد OTP به‌صورت رشتهٔ عددی (مثلاً "123456").
        
        Returns:
            dict: ساختاری که وضعیت عملیات را نشان می‌دهد.
                - در موفقیت: {'success': True, 'message_id': str, 'status': ...}
                - در خطا: {'success': False, 'error': str, 'error_detail': str}
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
        شماره تلفن را برای استفاده در API کاوه‌نگار نرمال‌سازی می‌کند.
        
        این تابع فضاها و خط تیره‌ها را حذف کرده و پیش‌شماره‌های بین‌المللی رایج ایران را به قالب محلی با صفر پیش‌شماره تبدیل می‌کند. به‌طور مشخص:
        - حذف فاصله‌ها و کاراکتر '-'.
        - تبدیل پیش‌وندهای '+98'، '0098' یا '98' به '0' در ابتدا (مثلاً '+98912...' → '0912...').
        
        Parameters:
            phone_number (str): شماره تلفن ورودی که ممکن است حاوی فاصله، خط تیره یا پیش‌شماره بین‌المللی باشد.
        
        Returns:
            str: شماره تلفن نرمال‌شده متناسب با قالب مورد انتظار کاوه‌نگار.
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