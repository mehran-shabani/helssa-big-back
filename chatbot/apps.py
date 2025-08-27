"""
پیکربندی اپ چت‌بات
Chatbot App Configuration
"""

from django.apps import AppConfig


class ChatbotConfig(AppConfig):
    """
    پیکربندی اپ چت‌بات برای بیماران و پزشکان
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chatbot'
    verbose_name = 'سیستم چت‌بات'
    
    def ready(self):
        """
        تنظیمات اولیه هنگام آماده شدن اپ
        """
        pass