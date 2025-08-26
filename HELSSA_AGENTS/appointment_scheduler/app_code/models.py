"""
{APP_NAME} Models
Part of HELSSA Platform

This module defines the data models for {APP_DESCRIPTION}
following the standard HELSSA model pattern.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
import uuid

User = get_user_model()


class BaseModel(models.Model):
    """
    Abstract base model with common fields for all {APP_NAME} models
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به‌روزرسانی')
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='%(class)s_created',
        verbose_name='ایجادکننده'
    )
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    
    class Meta:
        abstract = True
        ordering = ['-created_at']


class {MainModel}(BaseModel):
    """
    Main model for {APP_NAME}
    """
    # Add your specific fields here
    title = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(3)],
        verbose_name='عنوان'
    )
    description = models.TextField(
        blank=True,
        verbose_name='توضیحات'
    )
    
    # Foreign keys to unified services
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='{app_name}_{main_model_lower}s',
        verbose_name='کاربر'
    )
    
    # Status field
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('processing', 'در حال پردازش'),
        ('completed', 'تکمیل شده'),
        ('failed', 'ناموفق'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت'
    )
    
    class Meta:
        verbose_name = '{MAIN_MODEL_VERBOSE_NAME}'
        verbose_name_plural = '{MAIN_MODEL_VERBOSE_NAME_PLURAL}'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def get_status_display_persian(self):
        """Return Persian status display"""
        status_map = {
            'pending': 'در انتظار',
            'processing': 'در حال پردازش', 
            'completed': 'تکمیل شده',
            'failed': 'ناموفق',
        }
        return status_map.get(self.status, self.status)


# Add more models as needed based on your PLAN.md