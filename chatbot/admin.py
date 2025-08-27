"""
پنل مدیریت سیستم چت‌بات
Chatbot Admin Panel
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import ChatbotSession, Conversation, Message, ChatbotResponse


@admin.register(ChatbotSession)
class ChatbotSessionAdmin(admin.ModelAdmin):
    """
    پنل مدیریت جلسات چت‌بات
    """
    list_display = [
        'id', 'user', 'session_type', 'status', 
        'started_at', 'last_activity', 'conversation_count'
    ]
    list_filter = [
        'session_type', 'status', 'started_at'
    ]
    search_fields = [
        'user__phone_number', 'user__first_name', 'user__last_name'
    ]
    readonly_fields = [
        'id', 'started_at', 'duration_display'
    ]
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('id', 'user', 'session_type', 'status')
        }),
        ('زمان‌بندی', {
            'fields': ('started_at', 'last_activity', 'ended_at', 'expires_at', 'duration_display')
        }),
        ('داده‌ها', {
            'fields': ('context_data', 'metadata'),
            'classes': ('collapse',)
        }),
    )
    
    def conversation_count(self, obj):
        """
        تعداد مکالمات جلسه
        """
        count = obj.conversations.count()
        if count > 0:
            url = reverse('admin:chatbot_conversation_changelist') + f'?session__id__exact={obj.id}'
            return format_html('<a href="{}">{} مکالمه</a>', url, count)
        return '0 مکالمه'
    conversation_count.short_description = 'تعداد مکالمات'
    
    def duration_display(self, obj):
        """
        نمایش مدت زمان جلسه
        """
        duration = obj.duration
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
    duration_display.short_description = 'مدت زمان'


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """
    پنل مدیریت مکالمات
    """
    list_display = [
        'id', 'session_user', 'conversation_type', 'title',
        'is_active', 'started_at', 'message_count_display'
    ]
    list_filter = [
        'conversation_type', 'is_active', 'started_at',
        'session__session_type'
    ]
    search_fields = [
        'title', 'session__user__phone_number',
        'session__user__first_name', 'session__user__last_name'
    ]
    readonly_fields = [
        'id', 'started_at', 'message_count_display', 'last_message_time'
    ]
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('id', 'session', 'conversation_type', 'title', 'is_active')
        }),
        ('زمان‌بندی', {
            'fields': ('started_at', 'updated_at', 'last_message_time')
        }),
        ('آمار', {
            'fields': ('message_count_display',)
        }),
        ('محتوا', {
            'fields': ('summary', 'tags'),
            'classes': ('collapse',)
        }),
        ('داده‌ها', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )
    
    def session_user(self, obj):
        """
        کاربر جلسه
        """
        return obj.session.user
    session_user.short_description = 'کاربر'
    
    def message_count_display(self, obj):
        """
        تعداد پیام‌ها
        """
        count = obj.message_count
        if count > 0:
            url = reverse('admin:chatbot_message_changelist') + f'?conversation__id__exact={obj.id}'
            return format_html('<a href="{}">{} پیام</a>', url, count)
        return '0 پیام'
    message_count_display.short_description = 'تعداد پیام‌ها'


class MessageInline(admin.TabularInline):
    """
    نمایش پیام‌ها به صورت inline
    """
    model = Message
    extra = 0
    readonly_fields = ['id', 'created_at', 'processing_time']
    fields = [
        'sender_type', 'message_type', 'content', 
        'ai_confidence', 'is_sensitive', 'created_at'
    ]
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    پنل مدیریت پیام‌ها
    """
    list_display = [
        'id', 'conversation_title', 'sender_type', 'message_type',
        'content_preview', 'ai_confidence', 'is_sensitive', 'created_at'
    ]
    list_filter = [
        'sender_type', 'message_type', 'is_sensitive', 'created_at',
        'conversation__session__session_type'
    ]
    search_fields = [
        'content', 'conversation__title',
        'conversation__session__user__phone_number'
    ]
    readonly_fields = [
        'id', 'created_at', 'processing_time'
    ]
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('id', 'conversation', 'sender_type', 'message_type')
        }),
        ('محتوا', {
            'fields': ('content', 'response_data')
        }),
        ('تحلیل AI', {
            'fields': ('ai_confidence', 'processing_time'),
            'classes': ('collapse',)
        }),
        ('امنیت', {
            'fields': ('is_sensitive',)
        }),
        ('زمان‌بندی', {
            'fields': ('created_at', 'edited_at')
        }),
        ('داده‌ها', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )
    
    def conversation_title(self, obj):
        """
        عنوان مکالمه
        """
        return obj.conversation.title or f"مکالمه {obj.conversation.conversation_type}"
    conversation_title.short_description = 'مکالمه'
    
    def content_preview(self, obj):
        """
        پیش‌نمایش محتوا
        """
        content = obj.content
        if len(content) > 50:
            content = content[:50] + '...'
        
        if obj.is_sensitive:
            return format_html('<span style="color: red;">{}</span>', content)
        return content
    content_preview.short_description = 'محتوا'


@admin.register(ChatbotResponse)
class ChatbotResponseAdmin(admin.ModelAdmin):
    """
    پنل مدیریت پاسخ‌های چت‌بات
    """
    list_display = [
        'id', 'category', 'target_user', 'response_preview',
        'priority', 'is_active', 'created_at'
    ]
    list_filter = [
        'category', 'target_user', 'is_active', 'priority'
    ]
    search_fields = [
        'response_text', 'trigger_keywords'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at'
    ]
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('id', 'category', 'target_user', 'is_active', 'priority')
        }),
        ('محرک‌ها', {
            'fields': ('trigger_keywords',)
        }),
        ('پاسخ', {
            'fields': ('response_text', 'response_data')
        }),
        ('زمان‌بندی', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def response_preview(self, obj):
        """
        پیش‌نمایش پاسخ
        """
        text = obj.response_text
        if len(text) > 50:
            text = text[:50] + '...'
        return text
    response_preview.short_description = 'پیش‌نمایش پاسخ'


# تنظیمات اضافی admin
admin.site.site_header = 'پنل مدیریت سیستم چت‌بات هلسا'
admin.site.site_title = 'مدیریت چت‌بات'
admin.site.index_title = 'خوش آمدید به پنل مدیریت چت‌بات'