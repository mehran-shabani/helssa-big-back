"""
مدل‌های سیستم چت‌بات
Chatbot System Models
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinLengthValidator
import uuid

User = get_user_model()


class ChatbotSession(models.Model):
    """
    جلسه چت‌بات برای پیگیری مکالمات کاربر
    """
    
    SESSION_TYPES = [
        ('patient', 'بیمار'),
        ('doctor', 'پزشک'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'فعال'),
        ('paused', 'متوقف'),
        ('completed', 'تکمیل شده'),
        ('expired', 'منقضی'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chatbot_sessions',
        verbose_name='کاربر'
    )
    
    session_type = models.CharField(
        max_length=10,
        choices=SESSION_TYPES,
        verbose_name='نوع جلسه'
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='وضعیت'
    )
    
    context_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='داده‌های زمینه',
        help_text='اطلاعات زمینه‌ای برای حفظ وضعیت مکالمه'
    )
    
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='زمان شروع'
    )
    
    last_activity = models.DateTimeField(
        auto_now=True,
        verbose_name='آخرین فعالیت'
    )
    
    ended_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='زمان پایان'
    )
    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='زمان انقضا'
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='اطلاعات اضافی'
    )
    
    class Meta:
        verbose_name = 'جلسه چت‌بات'
        verbose_name_plural = 'جلسات چت‌بات'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['session_type', 'status']),
            models.Index(fields=['started_at']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        """
        نمایش متنی جلسه چت‌بات
        """
        return f"جلسه {self.session_type} - {self.user} ({self.status})"
    
    @property
    def is_active(self):
        """
        بررسی فعال بودن جلسه
        """
        return self.status == 'active' and (
            not self.expires_at or timezone.now() < self.expires_at
        )
    
    @property
    def duration(self):
        """
        مدت زمان جلسه
        """
        if self.ended_at:
            return self.ended_at - self.started_at
        return timezone.now() - self.started_at
    
    def end_session(self):
        """
        پایان دادن به جلسه
        """
        self.status = 'completed'
        self.ended_at = timezone.now()
        self.save(update_fields=['status', 'ended_at'])


class Conversation(models.Model):
    """
    مکالمه در چت‌بات
    """
    
    CONVERSATION_TYPES = [
        ('patient_inquiry', 'استعلام بیمار'),
        ('doctor_consultation', 'مشاوره پزشک'),
        ('symptom_check', 'بررسی علائم'),
        ('medication_info', 'اطلاعات دارو'),
        ('appointment', 'نوبت‌گیری'),
        ('general', 'عمومی'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    session = models.ForeignKey(
        ChatbotSession,
        on_delete=models.CASCADE,
        related_name='conversations',
        verbose_name='جلسه'
    )
    
    conversation_type = models.CharField(
        max_length=20,
        choices=CONVERSATION_TYPES,
        default='general',
        verbose_name='نوع مکالمه'
    )
    
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='عنوان'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
    )
    
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='زمان شروع'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='آخرین بروزرسانی'
    )
    
    summary = models.TextField(
        blank=True,
        verbose_name='خلاصه مکالمه'
    )
    
    tags = models.JSONField(
        default=list,
        blank=True,
        verbose_name='برچسب‌ها'
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='اطلاعات اضافی'
    )
    
    class Meta:
        verbose_name = 'مکالمه'
        verbose_name_plural = 'مکالمات'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['session', 'is_active']),
            models.Index(fields=['conversation_type']),
            models.Index(fields=['started_at']),
        ]
    
    def __str__(self):
        """
        نمایش متنی مکالمه
        """
        title = self.title or f"مکالمه {self.conversation_type}"
        return f"{title} - {self.session.user}"
    
    @property
    def message_count(self):
        """
        تعداد پیام‌های مکالمه
        """
        return self.messages.count()
    
    @property
    def last_message_time(self):
        """
        زمان آخرین پیام
        """
        last_message = self.messages.order_by('-created_at').first()
        return last_message.created_at if last_message else self.started_at


class Message(models.Model):
    """
    پیام در مکالمه چت‌بات
    """
    
    SENDER_TYPES = [
        ('user', 'کاربر'),
        ('bot', 'ربات'),
        ('system', 'سیستم'),
    ]
    
    MESSAGE_TYPES = [
        ('text', 'متن'),
        ('quick_reply', 'پاسخ سریع'),
        ('attachment', 'پیوست'),
        ('card', 'کارت'),
        ('carousel', 'کاروسل'),
        ('typing', 'در حال تایپ'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='مکالمه'
    )
    
    sender_type = models.CharField(
        max_length=10,
        choices=SENDER_TYPES,
        verbose_name='نوع فرستنده'
    )
    
    message_type = models.CharField(
        max_length=15,
        choices=MESSAGE_TYPES,
        default='text',
        verbose_name='نوع پیام'
    )
    
    content = models.TextField(
        validators=[MinLengthValidator(1)],
        verbose_name='محتوا'
    )
    
    response_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='داده‌های پاسخ',
        help_text='پاسخ‌های ساختاریافته یا گزینه‌ها'
    )
    
    ai_confidence = models.FloatField(
        null=True,
        blank=True,
        verbose_name='اطمینان AI',
        help_text='درجه اطمینان پاسخ هوش مصنوعی (0.0 تا 1.0)'
    )
    
    processing_time = models.FloatField(
        null=True,
        blank=True,
        verbose_name='زمان پردازش',
        help_text='زمان پردازش به ثانیه'
    )
    
    is_sensitive = models.BooleanField(
        default=False,
        verbose_name='حساس',
        help_text='آیا پیام حاوی اطلاعات حساس است؟'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='زمان ایجاد'
    )
    
    edited_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='زمان ویرایش'
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='اطلاعات اضافی'
    )
    
    class Meta:
        verbose_name = 'پیام'
        verbose_name_plural = 'پیام‌ها'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['sender_type', 'created_at']),
            models.Index(fields=['message_type']),
            models.Index(fields=['is_sensitive']),
        ]
    
    def __str__(self):
        """
        نمایش متنی پیام
        """
        content_preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"{self.sender_type}: {content_preview}"
    
    @property
    def is_from_user(self):
        """
        بررسی اینکه پیام از کاربر ارسال شده
        """
        return self.sender_type == 'user'
    
    @property
    def is_from_bot(self):
        """
        بررسی اینکه پیام از ربات ارسال شده
        """
        return self.sender_type == 'bot'


class ChatbotResponse(models.Model):
    """
    پاسخ‌های از پیش تعریف شده چت‌بات
    """
    
    RESPONSE_CATEGORIES = [
        ('greeting', 'خوشامدگویی'),
        ('symptom_inquiry', 'پرسش علائم'),
        ('medication_info', 'اطلاعات دارو'),
        ('appointment_booking', 'نوبت‌گیری'),
        ('emergency', 'اورژانس'),
        ('general_health', 'سلامت عمومی'),
        ('farewell', 'خداحافظی'),
        ('error', 'خطا'),
        ('unknown', 'نامشخص'),
    ]
    
    TARGET_USERS = [
        ('patient', 'بیمار'),
        ('doctor', 'پزشک'),
        ('both', 'هر دو'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    category = models.CharField(
        max_length=20,
        choices=RESPONSE_CATEGORIES,
        verbose_name='دسته‌بندی'
    )
    
    target_user = models.CharField(
        max_length=10,
        choices=TARGET_USERS,
        default='both',
        verbose_name='کاربر هدف'
    )
    
    trigger_keywords = models.JSONField(
        default=list,
        verbose_name='کلمات کلیدی محرک'
    )
    
    response_text = models.TextField(
        verbose_name='متن پاسخ'
    )
    
    response_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='داده‌های پاسخ'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
    )
    
    priority = models.IntegerField(
        default=1,
        verbose_name='اولویت',
        help_text='عدد بالاتر = اولویت بیشتر'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='زمان ایجاد'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='آخرین بروزرسانی'
    )
    
    class Meta:
        verbose_name = 'پاسخ چت‌بات'
        verbose_name_plural = 'پاسخ‌های چت‌بات'
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['target_user', 'is_active']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        """
        نمایش متنی پاسخ
        """
        return f"{self.category} - {self.target_user} (اولویت: {self.priority})"