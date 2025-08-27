"""
تنظیمات اپ چت‌بات
Chatbot App Settings
"""

import os
from django.conf import settings

# تنظیمات پیش‌فرض چت‌بات
CHATBOT_SETTINGS = {
    # تنظیمات عمومی
    'DEFAULT_SESSION_TIMEOUT': 3600,  # 1 ساعت (ثانیه)
    'MAX_MESSAGE_LENGTH': 4000,       # حداکثر طول پیام
    'MAX_CONVERSATION_MESSAGES': 1000, # حداکثر پیام در مکالمه
    'AUTO_SAVE_INTERVAL': 30,         # فاصله خودکار ذخیره (ثانیه)
    
    # تنظیمات AI
    'AI_CONFIDENCE_THRESHOLD': 0.7,   # حد آستانه اطمینان AI
    'USE_PREDEFINED_RESPONSES': True,  # استفاده از پاسخ‌های از پیش تعریف شده
    'ENABLE_CONTEXT_LEARNING': False, # یادگیری از زمینه (نیاز به AI پیشرفته)
    
    # تنظیمات امنیت
    'ENABLE_CONTENT_FILTERING': True,  # فیلتر محتوای حساس
    'LOG_SENSITIVE_ATTEMPTS': True,    # ثبت تلاش‌های ارسال محتوای حساس
    'MASK_SENSITIVE_DATA': True,       # پنهان کردن داده‌های حساس در لاگ
    
    # تنظیمات Rate Limiting
    'ENABLE_RATE_LIMITING': True,
    'RATE_LIMIT_STORAGE': 'cache',     # نحوه ذخیره محدودیت‌ها
    
    # تنظیمات پردازش پیام
    'MESSAGE_PROCESSING_TIMEOUT': 30,  # تایم‌اوت پردازش پیام (ثانیه)
    'ENABLE_ASYNC_PROCESSING': False,  # پردازش غیرهمزمان
    'BATCH_MESSAGE_PROCESSING': False, # پردازش دسته‌ای پیام‌ها
    
    # تنظیمات ذخیره‌سازی
    'STORE_MESSAGE_METADATA': True,    # ذخیره متادیتای پیام‌ها
    'COMPRESS_OLD_MESSAGES': False,    # فشرده‌سازی پیام‌های قدیمی
    'AUTO_CLEANUP_OLD_SESSIONS': True, # پاکسازی خودکار جلسات قدیمی
    'CLEANUP_AFTER_DAYS': 30,          # پاکسازی بعد از چند روز
    
    # تنظیمات چت‌بات بیمار
    'PATIENT_CHATBOT': {
        'ENABLE_SYMPTOM_ASSESSMENT': True,
        'ENABLE_APPOINTMENT_BOOKING': True,
        'ENABLE_MEDICATION_REMINDERS': False,
        'MAX_DAILY_SESSIONS': 10,
        'SESSION_TIMEOUT': 1800,  # 30 دقیقه
        'GREETING_MESSAGE': 'سلام! من دستیار هوشمند هلسا هستم. چطور می‌توانم کمکتان کنم؟',
    },
    
    # تنظیمات چت‌بات پزشک
    'DOCTOR_CHATBOT': {
        'ENABLE_DIAGNOSIS_SUPPORT': True,
        'ENABLE_TREATMENT_PROTOCOLS': True,
        'ENABLE_DRUG_INTERACTIONS': True,
        'ENABLE_LITERATURE_SEARCH': True,
        'MAX_DAILY_SESSIONS': 50,
        'SESSION_TIMEOUT': 3600,  # 1 ساعت
        'GREETING_MESSAGE': 'سلام دکتر! من دستیار هوشمند پزشکی هلسا هستم. چطور می‌توانم در کار بالینی شما کمک کنم؟',
    },
    
    # تنظیمات لاگ
    'LOGGING': {
        'ENABLE_CONVERSATION_LOGGING': True,
        'ENABLE_PERFORMANCE_LOGGING': True,
        'ENABLE_ERROR_LOGGING': True,
        'LOG_LEVEL': 'INFO',
        'LOG_FILE_PATH': None,  # پیش‌فرض: استفاده از تنظیمات Django
    },
    
    # تنظیمات کش
    'CACHING': {
        'ENABLE_RESPONSE_CACHING': True,
        'CACHE_TIMEOUT': 300,  # 5 دقیقه
        'CACHE_KEY_PREFIX': 'chatbot:',
        'CACHE_BACKEND': 'default',
    },
    
    # تنظیمات یکپارچه‌سازی خارجی
    'EXTERNAL_INTEGRATIONS': {
        'ENABLE_MEDICAL_API': False,
        'ENABLE_DRUG_DATABASE': False,
        'ENABLE_APPOINTMENT_SYSTEM': False,
        'API_TIMEOUT': 10,  # ثانیه
    }
}

# ادغام تنظیمات از فایل settings.py اصلی
if hasattr(settings, 'CHATBOT_SETTINGS'):
    CHATBOT_SETTINGS.update(settings.CHATBOT_SETTINGS)

# تنظیمات محیط (Environment Variables)
def get_env_setting(key: str, default=None, cast_type=str):
    """
    دریافت تنظیمات از متغیرهای محیط
    """
    value = os.environ.get(f'CHATBOT_{key}', default)
    if value is None:
        return default
    
    try:
        if cast_type == bool:
            return value.lower() in ('true', '1', 'yes', 'on')
        return cast_type(value)
    except (ValueError, TypeError):
        return default

# بروزرسانی تنظیمات از متغیرهای محیط
CHATBOT_SETTINGS.update({
    'DEFAULT_SESSION_TIMEOUT': get_env_setting('SESSION_TIMEOUT', 
                                                CHATBOT_SETTINGS['DEFAULT_SESSION_TIMEOUT'], 
                                                int),
    'MAX_MESSAGE_LENGTH': get_env_setting('MAX_MESSAGE_LENGTH', 
                                          CHATBOT_SETTINGS['MAX_MESSAGE_LENGTH'], 
                                          int),
    'ENABLE_RATE_LIMITING': get_env_setting('ENABLE_RATE_LIMITING', 
                                            CHATBOT_SETTINGS['ENABLE_RATE_LIMITING'], 
                                            bool),
    'AI_CONFIDENCE_THRESHOLD': get_env_setting('AI_CONFIDENCE_THRESHOLD', 
                                               CHATBOT_SETTINGS['AI_CONFIDENCE_THRESHOLD'], 
                                               float),
})

# تابع کمکی برای دسترسی آسان به تنظیمات
def get_chatbot_setting(key: str, default=None):
    """
    دریافت تنظیمات چت‌بات
    
    Args:
        key: کلید تنظیمات (می‌تواند به صورت nested باشد مثل 'PATIENT_CHATBOT.ENABLE_SYMPTOM_ASSESSMENT')
        default: مقدار پیش‌فرض
    
    Returns:
        مقدار تنظیمات
    """
    keys = key.split('.')
    value = CHATBOT_SETTINGS
    
    try:
        for k in keys:
            value = value[k]
        return value
    except (KeyError, TypeError):
        return default

# صادر کردن تنظیمات
__all__ = ['CHATBOT_SETTINGS', 'get_chatbot_setting']