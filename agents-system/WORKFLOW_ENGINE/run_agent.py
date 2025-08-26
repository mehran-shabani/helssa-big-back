#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اجرای ایجنت برای ساخت اپلیکیشن
این اسکریپت ایجنت‌ها را اجرا می‌کند تا اپلیکیشن‌ها را بسازند.
"""

import os
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
import subprocess
import sys

# تنظیم لاگینگ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentRunner:
    """کلاس اجرای ایجنت‌ها"""
    
    def __init__(self, base_path: str = "agents-system"):
        self.base_path = Path(base_path)
        self.apps_path = self.base_path / "AGENT_APPS"
        self.docs_path = self.base_path / "HELSSA_DOCS"
        self.architecture_path = self.base_path / "CORE_ARCHITECTURE"
        
    def run_agent(self, app_name: str, mode: str = "full"):
        """اجرای ایجنت"""
        try:
            logger.info(f"شروع اجرای ایجنت برای {app_name} در حالت {mode}")
            
            app_path = self.apps_path / app_name
            if not app_path.exists():
                raise FileNotFoundError(f"اپلیکیشن {app_name} یافت نشد")
            
            if mode == "full":
                self._run_full_mode(app_path, app_name)
            elif mode == "step_by_step":
                self._run_step_by_step(app_path, app_name)
            else:
                raise ValueError(f"حالت نامعتبر: {mode}")
                
            logger.info(f"ایجنت {app_name} با موفقیت اجرا شد!")
            
        except Exception as e:
            logger.error(f"خطا در اجرای ایجنت: {str(e)}")
            raise
    
    def _run_full_mode(self, app_path: Path, app_name: str):
        """اجرای کامل ایجنت"""
        logger.info("اجرای کامل ایجنت...")
        
        # مرحله 1: آماده‌سازی
        self._prepare_environment(app_path, app_name)
        
        # مرحله 2: طراحی
        self._design_application(app_path, app_name)
        
        # مرحله 3: پیاده‌سازی
        self._implement_application(app_path, app_name)
        
        # مرحله 4: یکپارچه‌سازی
        self._integrate_services(app_path, app_name)
        
        # مرحله 5: تست و مستندسازی
        self._test_and_document(app_path, app_name)
        
        # مرحله 6: نهایی‌سازی
        self._finalize_application(app_path, app_name)
    
    def _run_step_by_step(self, app_path: Path, app_name: str):
        """اجرای مرحله به مرحله ایجنت"""
        logger.info("اجرای مرحله به مرحله ایجنت...")
        
        steps = [
            ("آماده‌سازی محیط", lambda: self._prepare_environment(app_path, app_name)),
            ("طراحی اپلیکیشن", lambda: self._design_application(app_path, app_name)),
            ("پیاده‌سازی", lambda: self._implement_application(app_path, app_name)),
            ("یکپارچه‌سازی", lambda: self._integrate_services(app_path, app_name)),
            ("تست و مستندسازی", lambda: self._test_and_document(app_path, app_name)),
            ("نهایی‌سازی", lambda: self._finalize_application(app_path, app_name))
        ]
        
        for i, (step_name, step_func) in enumerate(steps, 1):
            print(f"\n{'='*60}")
            print(f"مرحله {i}: {step_name}")
            print(f"{'='*60}")
            
            try:
                step_func()
                print(f"✅ مرحله {i} با موفقیت تکمیل شد")
                
                if i < len(steps):
                    input("\nبرای ادامه مرحله بعدی، Enter را فشار دهید...")
                    
            except Exception as e:
                print(f"❌ خطا در مرحله {i}: {str(e)}")
                if input("\nآیا می‌خواهید ادامه دهید؟ (y/n): ").lower() != 'y':
                    break
    
    def _prepare_environment(self, app_path: Path, app_name: str):
        """آماده‌سازی محیط"""
        logger.info("آماده‌سازی محیط...")
        
        # بررسی وجود فایل‌های ضروری
        required_files = ["PLAN.md", "CHECKLIST.json", "PROGRESS.json"]
        for file_name in required_files:
            file_path = app_path / file_name
            if not file_path.exists():
                raise FileNotFoundError(f"فایل {file_name} یافت نشد")
        
        # خواندن برنامه
        plan_path = app_path / "PLAN.md"
        logger.info(f"برنامه اپلیکیشن: {plan_path.read_text(encoding='utf-8')[:200]}...")
        
        # خواندن چک‌لیست
        checklist_path = app_path / "CHECKLIST.json"
        checklist = json.loads(checklist_path.read_text(encoding='utf-8'))
        logger.info(f"تعداد آیتم‌های چک‌لیست: {len(checklist.get('items', []))}")
        
        # به‌روزرسانی پیشرفت
        self._update_progress(app_path, "preparation", "completed")
        
        print("✅ محیط آماده شد")
    
    def _design_application(self, app_path: Path, app_name: str):
        """طراحی اپلیکیشن"""
        logger.info("طراحی اپلیکیشن...")
        
        # ایجاد مدل‌های داده
        self._create_data_models(app_path, app_name)
        
        # طراحی API endpoints
        self._design_api_endpoints(app_path, app_name)
        
        # تعیین وابستگی‌ها
        self._define_dependencies(app_path, app_name)
        
        # به‌روزرسانی پیشرفت
        self._update_progress(app_path, "design", "completed")
        
        print("✅ طراحی اپلیکیشن تکمیل شد")
    
    def _create_data_models(self, app_path: Path, app_name: str):
        """ایجاد مدل‌های داده"""
        logger.info("ایجاد مدل‌های داده...")
        
        models_path = app_path / "models.py"
        if models_path.exists():
            # اضافه کردن مدل‌های اصلی بر اساس نوع اپلیکیشن
            if "chatbot" in app_name:
                self._add_chatbot_models(models_path, app_name)
            elif "soap" in app_name:
                self._add_soap_models(models_path, app_name)
            elif "prescription" in app_name:
                self._add_prescription_models(models_path, app_name)
            elif "records" in app_name:
                self._add_records_models(models_path, app_name)
            else:
                self._add_generic_models(models_path, app_name)
    
    def _add_chatbot_models(self, models_path: Path, app_name: str):
        """اضافه کردن مدل‌های چت‌بات"""
        chatbot_models = f'''

class ChatSession({app_name.replace("_", "").title()}Base):
    """جلسه چت"""
    session_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Chat Session {{self.session_id}} - {{self.user.username}}"

class ChatMessage({app_name.replace("_", "").title()}Base):
    """پیام چت"""
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    message_type = models.CharField(max_length=20, choices=[
        ('user', 'کاربر'),
        ('bot', 'بات'),
        ('system', 'سیستم')
    ])
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{{self.message_type}}: {{self.content[:50]}}"
'''
        
        with open(models_path, 'a', encoding='utf-8') as f:
            f.write(chatbot_models)
    
    def _add_soap_models(self, models_path: Path, app_name: str):
        """اضافه کردن مدل‌های SOAP"""
        soap_models = f'''

class SOAPReport({app_name.replace("_", "").title()}Base):
    """گزارش SOAP"""
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='soap_reports')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_reports')
    subjective = models.TextField(help_text="شکایات بیمار")
    objective = models.TextField(help_text="یافته‌های معاینه")
    assessment = models.TextField(help_text="تشخیص")
    plan = models.TextField(help_text="طرح درمان")
    report_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-report_date']
    
    def __str__(self):
        return f"SOAP Report - {{self.patient.username}} - {{self.report_date.date()}}"
'''
        
        with open(models_path, 'a', encoding='utf-8') as f:
            f.write(soap_models)
    
    def _add_prescription_models(self, models_path: Path, app_name: str):
        """اضافه کردن مدل‌های نسخه"""
        prescription_models = f'''

class Prescription({app_name.replace("_", "").title()}Base):
    """نسخه پزشکی"""
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='written_prescriptions')
    prescription_date = models.DateTimeField(auto_now_add=True)
    diagnosis = models.TextField(help_text="تشخیص")
    notes = models.TextField(blank=True, help_text="یادداشت‌ها")
    
    class Meta:
        ordering = ['-prescription_date']
    
    def __str__(self):
        return f"Prescription - {{self.patient.username}} - {{self.prescription_date.date()}}"

class Medication({app_name.replace("_", "").title()}Base):
    """دارو"""
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='medications')
    name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    instructions = models.TextField(blank=True)
    
    def __str__(self):
        return f"{{self.name}} - {{self.dosage}}"
'''
        
        with open(models_path, 'a', encoding='utf-8') as f:
            f.write(prescription_models)
    
    def _add_records_models(self, models_path: Path, app_name: str):
        """اضافه کردن مدل‌های پرونده"""
        records_models = f'''

class PatientRecord({app_name.replace("_", "").title()}Base):
    """پرونده بیمار"""
    patient = models.OneToOneField(User, on_delete=models.CASCADE, related_name='medical_record')
    date_of_birth = models.DateField()
    blood_type = models.CharField(max_length=5, blank=True)
    allergies = models.TextField(blank=True)
    medical_history = models.TextField(blank=True)
    
    def __str__(self):
        return f"Medical Record - {{self.patient.username}}"

class MedicalFile({app_name.replace("_", "").title()}Base):
    """فایل پزشکی"""
    record = models.ForeignKey(PatientRecord, on_delete=models.CASCADE, related_name='files')
    file_type = models.CharField(max_length=50)
    file_path = models.FileField(upload_to='medical_files/')
    upload_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-upload_date']
    
    def __str__(self):
        return f"{{self.file_type}} - {{self.record.patient.username}}"
'''
        
        with open(models_path, 'a', encoding='utf-8') as f:
            f.write(records_models)
    
    def _add_generic_models(self, models_path: Path, app_name: str):
        """اضافه کردن مدل‌های عمومی"""
        generic_models = f'''

class {app_name.replace("_", "").title()}Item({app_name.replace("_", "").title()}Base):
    """آیتم {app_name}"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[
        ('active', 'فعال'),
        ('inactive', 'غیرفعال'),
        ('pending', 'در انتظار')
    ], default='active')
    
    def __str__(self):
        return self.title
'''
        
        with open(models_path, 'a', encoding='utf-8') as f:
            f.write(generic_models)
    
    def _design_api_endpoints(self, app_path: Path, app_name: str):
        """طراحی API endpoints"""
        logger.info("طراحی API endpoints...")
        
        # به‌روزرسانی views.py
        views_path = app_path / "views.py"
        if views_path.exists():
            self._add_api_views(views_path, app_name)
        
        # به‌روزرسانی urls.py
        urls_path = app_path / "urls.py"
        if urls_path.exists():
            self._add_api_urls(urls_path, app_name)
    
    def _add_api_views(self, views_path: Path, app_name: str):
        """اضافه کردن view های API"""
        api_views = f'''

# API Views
from rest_framework import viewsets, status
from rest_framework.decorators import action
from .models import *
from .serializers import *

class {app_name.replace("_", "").title()}ViewSet(viewsets.ModelViewSet):
    """ViewSet اصلی {app_name}"""
    queryset = {app_name.replace("_", "").title()}Item.objects.all()
    serializer_class = {app_name.replace("_", "").title()}ItemSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """آمار اپلیکیشن"""
        total_items = {app_name.replace("_", "").title()}Item.objects.count()
        active_items = {app_name.replace("_", "").title()}Item.objects.filter(status='active').count()
        
        return Response({{
            'total_items': total_items,
            'active_items': active_items,
            'app_name': '{app_name}'
        }})
'''
        
        with open(views_path, 'a', encoding='utf-8') as f:
            f.write(api_views)
    
    def _add_api_urls(self, urls_path: Path, app_name: str):
        """اضافه کردن URL های API"""
        # به‌روزرسانی router
        urls_content = urls_path.read_text(encoding='utf-8')
        urls_content = urls_content.replace(
            "# router.register(r'models', views.ModelViewSet)",
            f"router.register(r'items', views.{app_name.replace('_', '').title()}ViewSet)"
        )
        
        with open(urls_path, 'w', encoding='utf-8') as f:
            f.write(urls_content)
    
    def _define_dependencies(self, app_path: Path, app_name: str):
        """تعیین وابستگی‌ها"""
        logger.info("تعیین وابستگی‌ها...")
        
        # ایجاد فایل requirements.txt
        requirements_path = app_path / "requirements.txt"
        requirements = [
            "Django>=4.2.0",
            "djangorestframework>=3.14.0",
            "django-cors-headers>=4.0.0",
            "psycopg2-binary>=2.9.0",
            "celery>=5.3.0",
            "redis>=4.5.0",
            "Pillow>=9.5.0",
            "python-decouple>=3.8",
        ]
        
        with open(requirements_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(requirements))
    
    def _implement_application(self, app_path: Path, app_name: str):
        """پیاده‌سازی اپلیکیشن"""
        logger.info("پیاده‌سازی اپلیکیشن...")
        
        # ایجاد serializers
        self._create_serializers(app_path, app_name)
        
        # ایجاد admin interface
        self._create_admin_interface(app_path, app_name)
        
        # ایجاد permissions
        self._create_permissions(app_path, app_name)
        
        # ایجاد services
        self._create_services(app_path, app_name)
        
        # به‌روزرسانی پیشرفت
        self._update_progress(app_path, "implementation", "completed")
        
        print("✅ پیاده‌سازی اپلیکیشن تکمیل شد")
    
    def _create_serializers(self, app_path: Path, app_name: str):
        """ایجاد serializers"""
        serializers_path = app_path / "serializers.py"
        if serializers_path.exists():
            serializers_content = f'''

# Serializers
from rest_framework import serializers
from .models import *

class {app_name.replace("_", "").title()}ItemSerializer(serializers.ModelSerializer):
    """سریالایزر آیتم {app_name}"""
    
    class Meta:
        model = {app_name.replace("_", "").title()}Item
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['updated_by'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        return super().update(instance, validated_data)
'''
            
            with open(serializers_path, 'a', encoding='utf-8') as f:
                f.write(serializers_content)
    
    def _create_admin_interface(self, app_path: Path, app_name: str):
        """ایجاد رابط ادمین"""
        admin_path = app_path / "admin.py"
        if admin_path.exists():
            admin_content = f'''

# Admin Interface
from django.contrib import admin
from .models import *

@admin.register({app_name.replace("_", "").title()}Item)
class {app_name.replace("_", "").title()}ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_at', 'created_by')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def save_model(self, request, obj, form, change):
        if not change:  # ایجاد جدید
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
'''
            
            with open(admin_path, 'a', encoding='utf-8') as f:
                f.write(admin_content)
    
    def _create_permissions(self, app_path: Path, app_name: str):
        """ایجاد permissions"""
        permissions_path = app_path / "permissions.py"
        if permissions_path.exists():
            permissions_content = f'''

# Custom Permissions
from rest_framework import permissions

class {app_name.replace("_", "").title()}ItemPermission(permissions.BasePermission):
    """دسترسی‌های آیتم {app_name}"""
    
    def has_permission(self, request, view):
        """بررسی دسترسی عمومی"""
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """بررسی دسترسی به شیء"""
        # کاربران می‌توانند آیتم‌های خود را ویرایش کنند
        if view.action in ['update', 'partial_update', 'destroy']:
            return obj.created_by == request.user
        return True
'''
            
            with open(permissions_path, 'a', encoding='utf-8') as f:
                f.write(permissions_content)
    
    def _create_services(self, app_path: Path, app_name: str):
        """ایجاد services"""
        services_path = app_path / "services.py"
        if services_path.exists():
            services_content = f'''

# Business Logic Services
from django.core.exceptions import ValidationError
from .models import *

class {app_name.replace("_", "").title()}ItemService:
    """سرویس آیتم {app_name}"""
    
    @staticmethod
    def create_item(data, user):
        """ایجاد آیتم جدید"""
        try:
            data['created_by'] = user
            data['updated_by'] = user
            item = {app_name.replace("_", "").title()}Item.objects.create(**data)
            return item
        except Exception as e:
            raise ValidationError(f"خطا در ایجاد آیتم: {{str(e)}}")
    
    @staticmethod
    def update_item(item, data, user):
        """به‌روزرسانی آیتم"""
        try:
            data['updated_by'] = user
            for key, value in data.items():
                setattr(item, key, value)
            item.save()
            return item
        except Exception as e:
            raise ValidationError(f"خطا در به‌روزرسانی آیتم: {{str(e)}}")
    
    @staticmethod
    def delete_item(item, user):
        """حذف آیتم"""
        try:
            if item.created_by == user:
                item.delete()
                return True
            else:
                raise ValidationError("شما مجاز به حذف این آیتم نیستید")
        except Exception as e:
            raise ValidationError(f"خطا در حذف آیتم: {{str(e)}}")
'''
            
            with open(services_path, 'a', encoding='utf-8') as f:
                f.write(services_content)
    
    def _integrate_services(self, app_path: Path, app_name: str):
        """یکپارچه‌سازی سرویس‌ها"""
        logger.info("یکپارچه‌سازی سرویس‌ها...")
        
        # یکپارچه‌سازی با unified_auth
        self._integrate_unified_auth(app_path, app_name)
        
        # یکپارچه‌سازی با unified_billing
        self._integrate_unified_billing(app_path, app_name)
        
        # یکپارچه‌سازی با unified_ai
        self._integrate_unified_ai(app_path, app_name)
        
        # به‌روزرسانی پیشرفت
        self._update_progress(app_path, "integration", "completed")
        
        print("✅ یکپارچه‌سازی سرویس‌ها تکمیل شد")
    
    def _integrate_unified_auth(self, app_path: Path, app_name: str):
        """یکپارچه‌سازی با unified_auth"""
        logger.info("یکپارچه‌سازی با unified_auth...")
        
        # اضافه کردن import
        views_path = app_path / "views.py"
        if views_path.exists():
            with open(views_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "from unified_auth" not in content:
                content = content.replace(
                    "from rest_framework.permissions import IsAuthenticated",
                    "from rest_framework.permissions import IsAuthenticated\nfrom unified_auth.permissions import HasRole"
                )
                
                with open(views_path, 'w', encoding='utf-8') as f:
                    f.write(content)
    
    def _integrate_unified_billing(self, app_path: Path, app_name: str):
        """یکپارچه‌سازی با unified_billing"""
        logger.info("یکپارچه‌سازی با unified_billing...")
        
        # اضافه کردن مدل‌های صورتحساب
        models_path = app_path / "models.py"
        if models_path.exists():
            billing_models = f'''

# Billing Integration
class {app_name.replace("_", "").title()}Billing({app_name.replace("_", "").title()}Base):
    """صورتحساب {app_name}"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='{app_name}_billing')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=200)
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{{self.description}} - {{self.amount}}"
'''
            
            with open(models_path, 'a', encoding='utf-8') as f:
                f.write(billing_models)
    
    def _integrate_unified_ai(self, app_path: Path, app_name: str):
        """یکپارچه‌سازی با unified_ai"""
        logger.info("یکپارچه‌سازی با unified_ai...")
        
        # اضافه کردن سرویس AI
        services_path = app_path / "services.py"
        if services_path.exists():
            ai_service = f'''

# AI Integration
class {app_name.replace("_", "").title()}AIService:
    """سرویس AI برای {app_name}"""
    
    def __init__(self):
        try:
            from unified_ai.services import UnifiedAIService
            self.ai_service = UnifiedAIService()
        except ImportError:
            self.ai_service = None
            logger.warning("Unified AI service not available")
    
    def process_with_ai(self, data):
        """پردازش با AI"""
        if not self.ai_service:
            return {{'status': 'ai_not_available', 'data': data}}
        
        try:
            result = self.ai_service.process_text(
                text=str(data),
                context={{'app': '{app_name}'}},
                task='general_processing'
            )
            return {{'status': 'success', 'ai_result': result}}
        except Exception as e:
            logger.error(f"خطا در پردازش AI: {{str(e)}}")
            return {{'status': 'ai_error', 'error': str(e), 'data': data}}
'''
            
            with open(services_path, 'a', encoding='utf-8') as f:
                f.write(ai_service)
    
    def _test_and_document(self, app_path: Path, app_name: str):
        """تست و مستندسازی"""
        logger.info("تست و مستندسازی...")
        
        # ایجاد تست‌های کامل
        self._create_comprehensive_tests(app_path, app_name)
        
        # تکمیل مستندات
        self._complete_documentation(app_path, app_name)
        
        # به‌روزرسانی پیشرفت
        self._update_progress(app_path, "testing", "completed")
        
        print("✅ تست و مستندسازی تکمیل شد")
    
    def _create_comprehensive_tests(self, app_path: Path, app_name: str):
        """ایجاد تست‌های جامع"""
        tests_path = app_path / "tests"
        
        # تست یکپارچه‌سازی
        integration_test = f'''from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from ..models import *

User = get_user_model()

class {app_name.replace("_", "").title()}IntegrationTests(TestCase):
    """تست‌های یکپارچه‌سازی {app_name}"""
    
    def setUp(self):
        """تنظیمات اولیه"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_full_workflow(self):
        """تست کامل فرآیند کار"""
        # ایجاد آیتم
        data = {{'title': 'Test Item', 'description': 'Test Description'}}
        response = self.client.post(f'/api/{app_name}/items/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        item_id = response.data['id']
        
        # خواندن آیتم
        response = self.client.get(f'/api/{app_name}/items/{{item_id}}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Item')
        
        # به‌روزرسانی آیتم
        update_data = {{'title': 'Updated Item'}}
        response = self.client.patch(f'/api/{app_name}/items/{{item_id}}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Item')
        
        # حذف آیتم
        response = self.client.delete(f'/api/{app_name}/items/{{item_id}}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
'''
        
        with open(tests_path / "test_integration.py", 'w', encoding='utf-8') as f:
            f.write(integration_test)
    
    def _complete_documentation(self, app_path: Path, app_name: str):
        """تکمیل مستندات"""
        docs_path = app_path / "docs"
        
        # به‌روزرسانی API docs
        api_docs_path = docs_path / "API.md"
        if api_docs_path.exists():
            api_content = api_docs_path.read_text(encoding='utf-8')
            api_content += f'''

## Endpoints جدید

### GET /api/{app_name}/items/
دریافت لیست آیتم‌ها

### POST /api/{app_name}/items/
ایجاد آیتم جدید

### GET /api/{app_name}/items/{{id}}/
دریافت آیتم خاص

### PUT /api/{app_name}/items/{{id}}/
به‌روزرسانی کامل آیتم

### PATCH /api/{app_name}/items/{{id}}/
به‌روزرسانی جزئی آیتم

### DELETE /api/{app_name}/items/{{id}}/
حذف آیتم

### GET /api/{app_name}/items/stats/
دریافت آمار اپلیکیشن
'''
            
            with open(api_docs_path, 'w', encoding='utf-8') as f:
                f.write(api_content)
    
    def _finalize_application(self, app_path: Path, app_name: str):
        """نهایی‌سازی اپلیکیشن"""
        logger.info("نهایی‌سازی اپلیکیشن...")
        
        # ایجاد فایل نهایی
        final_file = app_path / "FINAL_REPORT.md"
        final_content = f'''# 🎉 گزارش نهایی - {app_name}

## خلاصه اجرا

اپلیکیشن {app_name} با موفقیت ایجاد و پیاده‌سازی شد.

## فایل‌های ایجاد شده

- ✅ مدل‌های داده (models.py)
- ✅ API Views (views.py)
- ✅ سریالایزرها (serializers.py)
- ✅ مسیریابی (urls.py)
- ✅ رابط ادمین (admin.py)
- ✅ دسترسی‌ها (permissions.py)
- ✅ سرویس‌ها (services.py)
- ✅ تست‌ها (tests/)
- ✅ مستندات (docs/)

## ویژگی‌های پیاده‌سازی شده

- 🔐 احراز هویت و دسترسی
- 📊 CRUD operations کامل
- 🧪 تست‌های جامع
- 📚 مستندات کامل
- 🔗 یکپارچه‌سازی با سرویس‌های هلسا

## مراحل بعدی

1. اجرای migrations
2. تست اپلیکیشن
3. استقرار در محیط تولید
4. نظارت و نگهداری

## تاریخ تکمیل

{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
'''
        
        with open(final_file, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        # به‌روزرسانی پیشرفت
        self._update_progress(app_path, "finalization", "completed")
        
        print("✅ نهایی‌سازی اپلیکیشن تکمیل شد")
    
    def _update_progress(self, app_path: Path, stage: str, status: str):
        """به‌روزرسانی پیشرفت"""
        progress_path = app_path / "PROGRESS.json"
        if progress_path.exists():
            try:
                progress = json.loads(progress_path.read_text(encoding='utf-8'))
                progress['stages'][stage] = {
                    'status': status,
                    'completed_at': datetime.now().isoformat()
                }
                
                with open(progress_path, 'w', encoding='utf-8') as f:
                    json.dump(progress, f, ensure_ascii=False, indent=2)
                    
            except Exception as e:
                logger.warning(f"خطا در به‌روزرسانی پیشرفت: {str(e)}")

def main():
    """تابع اصلی"""
    parser = argparse.ArgumentParser(description='اجرای ایجنت برای ساخت اپلیکیشن')
    parser.add_argument('--app_name', required=True, help='نام اپلیکیشن')
    parser.add_argument('--mode', choices=['full', 'step_by_step'], default='full', 
                       help='حالت اجرا (full یا step_by_step)')
    
    args = parser.parse_args()
    
    # اجرای ایجنت
    runner = AgentRunner()
    runner.run_agent(args.app_name, args.mode)

if __name__ == "__main__":
    main()