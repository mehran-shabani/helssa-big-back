"""
{APP_NAME} Admin
Part of HELSSA Platform

Django admin configuration for {APP_DESCRIPTION}
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import {MainModel}


@admin.register({MainModel})
class {MainModel}Admin(admin.ModelAdmin):
    """
    Admin configuration for {MainModel}
    """
    
    list_display = [
        'title',
        'user_link',
        'status_colored',
        'created_at',
        'is_active'
    ]
    
    list_filter = [
        'status',
        'is_active',
        'created_at',
        'user__user_type'
    ]
    
    search_fields = [
        'title',
        'description',
        'user__username',
        'user__email'
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'created_by'
    ]
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'description', 'status')
        }),
        ('اطلاعات کاربر', {
            'fields': ('user', 'created_by')
        }),
        ('تنظیمات', {
            'fields': ('is_active',)
        }),
        ('اطلاعات سیستم', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def user_link(self, obj):
        """Create clickable link to user"""
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '-'
    user_link.short_description = 'کاربر'
    
    def status_colored(self, obj):
        """Display status with color coding"""
        colors = {
            'pending': '#ffc107',     # yellow
            'processing': '#007bff',   # blue
            'completed': '#28a745',    # green
            'failed': '#dc3545',       # red
        }
        
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display_persian()
        )
    status_colored.short_description = 'وضعیت'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related(
            'user', 'created_by'
        )
    
    def save_model(self, request, obj, form, change):
        """Set created_by when creating new objects"""
        if not change:  # Creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    actions = ['mark_as_completed', 'mark_as_failed', 'activate_records', 'deactivate_records']
    
    def mark_as_completed(self, request, queryset):
        """Mark selected records as completed"""
        updated = queryset.update(status='completed')
        self.message_user(
            request,
            f'{updated} رکورد به عنوان تکمیل شده علامت‌گذاری شد.'
        )
    mark_as_completed.short_description = 'علامت‌گذاری به عنوان تکمیل شده'
    
    def mark_as_failed(self, request, queryset):
        """Mark selected records as failed"""
        updated = queryset.update(status='failed')
        self.message_user(
            request,
            f'{updated} رکورد به عنوان ناموفق علامت‌گذاری شد.'
        )
    mark_as_failed.short_description = 'علامت‌گذاری به عنوان ناموفق'
    
    def activate_records(self, request, queryset):
        """Activate selected records"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} رکورد فعال شد.'
        )
    activate_records.short_description = 'فعال‌سازی رکوردها'
    
    def deactivate_records(self, request, queryset):
        """Deactivate selected records"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} رکورد غیرفعال شد.'
        )
    deactivate_records.short_description = 'غیرفعال‌سازی رکوردها'


# Custom admin site configuration for {APP_NAME}
class {AppName}AdminConfig:
    """
    Custom admin configuration for {APP_NAME}
    """
    
    def __init__(self):
        self.setup_admin_site()
    
    def setup_admin_site(self):
        """Setup custom admin site properties"""
        admin.site.site_header = f"مدیریت {APP_NAME}"
        admin.site.site_title = f"{APP_NAME} Admin"
        admin.site.index_title = f"پنل مدیریت {APP_NAME}"
    
    def customize_admin_interface(self):
        """Add custom CSS/JS to admin interface"""
        # This can be implemented with custom admin templates
        pass


# Initialize admin configuration
{app_name}_admin_config = {AppName}AdminConfig()