"""
تنظیمات اپلیکیشن RBAC (Role-Based Access Control)
"""
from django.apps import AppConfig


class RbacConfig(AppConfig):
    """پیکربندی اپلیکیشن RBAC"""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rbac'
    verbose_name = 'مدیریت نقش‌ها و دسترسی‌ها'
    
    def ready(self):
        """
        اجرای کدهای مورد نیاز هنگام بارگذاری اپلیکیشن
        """
        # ثبت سیگنال‌ها در صورت نیاز
        pass