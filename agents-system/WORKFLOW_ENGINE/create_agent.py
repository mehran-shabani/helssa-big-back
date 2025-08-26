#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ایجاد ایجنت جدید برای پلتفرم هلسا
این اسکریپت یک ایجنت جدید با تمام قالب‌ها و پیکربندی‌های مورد نیاز ایجاد می‌کند.
"""

import os
import json
import argparse
import shutil
from pathlib import Path
from datetime import datetime
import logging

# تنظیم لاگینگ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentCreator:
    """کلاس ایجاد ایجنت جدید"""
    
    def __init__(self, base_path: str = "agents-system"):
        self.base_path = Path(base_path)
        self.templates_path = self.base_path / "AGENT_TEMPLATES"
        self.apps_path = self.base_path / "AGENT_APPS"
        
    def create_agent(self, app_name: str, description: str, config: dict = None):
        """ایجاد ایجنت جدید"""
        try:
            logger.info(f"شروع ایجاد ایجنت برای اپلیکیشن: {app_name}")
            
            # ایجاد پوشه اپلیکیشن
            app_path = self.apps_path / app_name
            app_path.mkdir(parents=True, exist_ok=True)
            
            # کپی قالب‌ها
            self._copy_templates(app_path, app_name, description)
            
            # ایجاد فایل‌های اصلی
            self._create_main_files(app_path, app_name, description)
            
            # ایجاد ساختار پوشه‌ها
            self._create_folder_structure(app_path)
            
            # ایجاد فایل‌های تست
            self._create_test_files(app_path, app_name)
            
            # ایجاد مستندات
            self._create_documentation(app_path, app_name, description)
            
            # ایجاد فایل‌های Django
            self._create_django_files(app_path, app_name)
            
            # به‌روزرسانی فایل‌های پیکربندی
            self._update_config_files(app_name, config)
            
            logger.info(f"ایجنت برای {app_name} با موفقیت ایجاد شد!")
            self._print_summary(app_name, app_path)
            
        except Exception as e:
            logger.error(f"خطا در ایجاد ایجنت: {str(e)}")
            raise
    
    def _copy_templates(self, app_path: Path, app_name: str, description: str):
        """کپی قالب‌های استاندارد"""
        logger.info("کپی قالب‌های استاندارد...")
        
        # کپی PLAN.md
        plan_template = self.templates_path / "PLAN.md.template"
        if plan_template.exists():
            plan_content = plan_template.read_text(encoding='utf-8')
            plan_content = plan_content.replace("{{APP_NAME}}", app_name)
            plan_content = plan_content.replace("{{DESCRIPTION}}", description)
            plan_content = plan_content.replace("{{CREATION_DATE}}", datetime.now().strftime("%Y-%m-%d"))
            (app_path / "PLAN.md").write_text(plan_content, encoding='utf-8')
        
        # کپی CHECKLIST.json
        checklist_template = self.templates_path / "CHECKLIST.json.template"
        if checklist_template.exists():
            checklist_content = checklist_template.read_text(encoding='utf-8')
            checklist_content = checklist_content.replace("{{APP_NAME}}", app_name)
            (app_path / "CHECKLIST.json").write_text(checklist_content, encoding='utf-8')
        
        # کپی PROGRESS.json
        progress_template = self.templates_path / "PROGRESS.json.template"
        if progress_template.exists():
            progress_content = progress_template.read_text(encoding='utf-8')
            progress_content = progress_content.replace("{{APP_NAME}}", app_name)
            (app_path / "PROGRESS.json").write_text(progress_content, encoding='utf-8')
        
        # کپی LOG.md
        log_template = self.templates_path / "LOG.md.template"
        if log_template.exists():
            log_content = log_template.read_text(encoding='utf-8')
            log_content = log_content.replace("{{APP_NAME}}", app_name)
            log_content = log_content.replace("{{CREATION_DATE}}", datetime.now().strftime("%Y-%m-%d"))
            (app_path / "LOG.md").write_text(log_content, encoding='utf-8')
        
        # کپی README.md
        readme_template = self.templates_path / "README.md.template"
        if readme_template.exists():
            readme_content = readme_template.read_text(encoding='utf-8')
            readme_content = readme_content.replace("{{APP_NAME}}", app_name)
            readme_content = readme_content.replace("{{DESCRIPTION}}", description)
            (app_path / "README.md").write_text(readme_content, encoding='utf-8')
    
    def _create_main_files(self, app_path: Path, app_name: str, description: str):
        """ایجاد فایل‌های اصلی"""
        logger.info("ایجاد فایل‌های اصلی...")
        
        # ایجاد فایل __init__.py
        (app_path / "__init__.py").write_text("# Django app initialization\n", encoding='utf-8')
        
        # ایجاد فایل apps.py
        apps_content = f'''from django.apps import AppConfig

class {app_name.replace("_", "").title()}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '{app_name}'
    verbose_name = '{description}'
'''
        (app_path / "apps.py").write_text(apps_content, encoding='utf-8')
        
        # ایجاد فایل models.py
        models_content = f'''from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class {app_name.replace("_", "").title()}Base(models.Model):
    """مدل پایه برای {app_name}"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='{app_name}_created')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='{app_name}_updated')
    
    class Meta:
        abstract = True

# مدل‌های اصلی اپلیکیشن اینجا تعریف شوند
'''
        (app_path / "models.py").write_text(models_content, encoding='utf-8')
        
        # ایجاد فایل views.py
        views_content = f'''from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def {app_name}_overview(request):
    """نمای کلی {app_name}"""
    try:
        return Response({{
            'app_name': '{app_name}',
            'description': '{description}',
            'status': 'active',
            'timestamp': timezone.now().isoformat()
        }})
    except Exception as e:
        logger.error(f"خطا در {app_name}_overview: {{str(e)}}")
        return Response(
            {{'error': 'خطای داخلی سرور'}},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ViewSets و Views اصلی اینجا تعریف شوند
'''
        (app_path / "views.py").write_text(views_content, encoding='utf-8')
        
        # ایجاد فایل urls.py
        urls_content = f'''from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = '{app_name}'

router = DefaultRouter()
# router.register(r'models', views.ModelViewSet)

urlpatterns = [
    path('', views.{app_name}_overview, name='overview'),
    path('api/', include(router.urls)),
]
'''
        (app_path / "urls.py").write_text(urls_content, encoding='utf-8')
        
        # ایجاد فایل admin.py
        admin_content = f'''from django.contrib import admin
from .models import *

# مدل‌های ادمین اینجا تعریف شوند
# admin.site.register(YourModel)
'''
        (app_path / "admin.py").write_text(admin_content, encoding='utf-8')
        
        # ایجاد فایل serializers.py
        serializers_content = f'''from rest_framework import serializers
from .models import *

# سریالایزرها اینجا تعریف شوند
'''
        (app_path / "serializers.py").write_text(serializers_content, encoding='utf-8')
        
        # ایجاد فایل services.py
        services_content = f'''import logging
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

class {app_name.replace("_", "").title()}Service:
    """سرویس اصلی {app_name}"""
    
    def __init__(self):
        self.logger = logger
    
    def process_request(self, data):
        """پردازش درخواست"""
        try:
            # منطق پردازش اینجا
            return {{'status': 'success', 'data': data}}
        except Exception as e:
            self.logger.error(f"خطا در پردازش: {{str(e)}}")
            raise ValidationError(f"خطا در پردازش: {{str(e)}}")
'''
        (app_path / "services.py").write_text(services_content, encoding='utf-8')
    
    def _create_folder_structure(self, app_path: Path):
        """ایجاد ساختار پوشه‌ها"""
        logger.info("ایجاد ساختار پوشه‌ها...")
        
        folders = [
            "tests",
            "docs",
            "templates",
            "static",
            "migrations",
            "fixtures"
        ]
        
        for folder in folders:
            folder_path = app_path / folder
            folder_path.mkdir(exist_ok=True)
            
            # ایجاد فایل __init__.py در پوشه tests
            if folder == "tests":
                (folder_path / "__init__.py").write_text("# Tests package\n", encoding='utf-8')
    
    def _create_test_files(self, app_path: Path, app_name: str):
        """ایجاد فایل‌های تست"""
        logger.info("ایجاد فایل‌های تست...")
        
        tests_path = app_path / "tests"
        
        # تست مدل‌ها
        test_models_content = f'''from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class {app_name.replace("_", "").title()}ModelTests(TestCase):
    """تست‌های مدل‌های {app_name}"""
    
    def setUp(self):
        """تنظیمات اولیه"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_model_creation(self):
        """تست ایجاد مدل"""
        # تست‌های مدل اینجا
        pass
    
    def test_model_validation(self):
        """تست اعتبارسنجی مدل"""
        # تست‌های اعتبارسنجی اینجا
        pass
'''
        (tests_path / "test_models.py").write_text(test_models_content, encoding='utf-8')
        
        # تست view ها
        test_views_content = f'''from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class {app_name.replace("_", "").title()}ViewTests(TestCase):
    """تست‌های view های {app_name}"""
    
    def setUp(self):
        """تنظیمات اولیه"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_overview_endpoint(self):
        """تست endpoint نمای کلی"""
        url = reverse('{app_name}:overview')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('app_name', response.data)
'''
        (tests_path / "test_views.py").write_text(test_views_content, encoding='utf-8')
        
        # تست سرویس‌ها
        test_services_content = f'''from django.test import TestCase
from django.core.exceptions import ValidationError
from ..services import {app_name.replace("_", "").title()}Service

class {app_name.replace("_", "").title()}ServiceTests(TestCase):
    """تست‌های سرویس {app_name}"""
    
    def setUp(self):
        """تنظیمات اولیه"""
        self.service = {app_name.replace("_", "").title()}Service()
    
    def test_process_request(self):
        """تست پردازش درخواست"""
        data = {{'test': 'data'}}
        result = self.service.process_request(data)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['data'], data)
'''
        (tests_path / "test_services.py").write_text(test_services_content, encoding='utf-8')
    
    def _create_documentation(self, app_path: Path, app_name: str, description: str):
        """ایجاد مستندات"""
        logger.info("ایجاد مستندات...")
        
        docs_path = app_path / "docs"
        
        # مستندات API
        api_docs_content = f'''# 📚 مستندات API - {app_name}

## نمای کلی

{description}

## Endpoints

### GET /{app_name}/
نمای کلی اپلیکیشن

**پاسخ:**
```json
{{
    "app_name": "{app_name}",
    "description": "{description}",
    "status": "active",
    "timestamp": "2024-01-01T00:00:00Z"
}}
```

## احراز هویت

تمام endpoints نیاز به احراز هویت دارند. از header زیر استفاده کنید:

```
Authorization: Bearer <token>
```

## کدهای خطا

- `400`: درخواست نامعتبر
- `401`: عدم احراز هویت
- `403`: عدم دسترسی
- `500`: خطای داخلی سرور
'''
        (docs_path / "API.md").write_text(api_docs_content, encoding='utf-8')
        
        # راهنمای کاربر
        user_guide_content = f'''# 👥 راهنمای کاربر - {app_name}

## شروع کار

{description}

## ویژگی‌های اصلی

- ویژگی 1
- ویژگی 2
- ویژگی 3

## نحوه استفاده

### مرحله 1: ورود
ابتدا وارد سیستم شوید

### مرحله 2: انتخاب اپلیکیشن
اپلیکیشن {app_name} را انتخاب کنید

### مرحله 3: استفاده
از ویژگی‌های اپلیکیشن استفاده کنید

## پشتیبانی

برای سوالات و مشکلات، با تیم پشتیبانی تماس بگیرید.
'''
        (docs_path / "USER_GUIDE.md").write_text(user_guide_content, encoding='utf-8')
        
        # مستندات فنی
        technical_docs_content = f'''# 🔧 مستندات فنی - {app_name}

## معماری

این اپلیکیشن بر اساس معماری چهار هسته‌ای هلسا طراحی شده است:

### هسته‌های فعال
- API Ingress Core
- Text Processing Core (در صورت نیاز)
- Speech Processing Core (در صورت نیاز)
- Orchestration Core

## تکنولوژی‌ها

- **Backend**: Django 4.2+
- **Database**: PostgreSQL
- **API**: Django REST Framework
- **Authentication**: JWT
- **Testing**: pytest-django

## ساختار کد

```
{app_name}/
├── models.py          # مدل‌های داده
├── views.py           # View های API
├── serializers.py     # سریالایزرها
├── services.py        # منطق کسب و کار
├── urls.py            # مسیریابی
└── tests/             # تست‌ها
```

## نصب و راه‌اندازی

1. نصب dependencies
2. اجرای migrations
3. اجرای تست‌ها
4. راه‌اندازی سرور

## تست‌ها

```bash
python manage.py test {app_name}
```
'''
        (docs_path / "TECHNICAL.md").write_text(technical_docs_content, encoding='utf-8')
    
    def _create_django_files(self, app_path: Path, app_name: str):
        """ایجاد فایل‌های Django"""
        logger.info("ایجاد فایل‌های Django...")
        
        # ایجاد فایل permissions.py
        permissions_content = f'''from rest_framework import permissions

class {app_name.replace("_", "").title()}Permission(permissions.BasePermission):
    """دسترسی‌های {app_name}"""
    
    def has_permission(self, request, view):
        """بررسی دسترسی"""
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """بررسی دسترسی به شیء"""
        return request.user.is_authenticated
'''
        (app_path / "permissions.py").write_text(permissions_content, encoding='utf-8')
        
        # ایجاد فایل tasks.py
        tasks_content = f'''from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def {app_name}_background_task(data):
    """تسک پس‌زمینه {app_name}"""
    try:
        logger.info(f"شروع تسک پس‌زمینه برای {{data}}")
        # منطق تسک اینجا
        return {{'status': 'success', 'result': 'task completed'}}
    except Exception as e:
        logger.error(f"خطا در تسک پس‌زمینه: {{str(e)}}")
        raise
'''
        (app_path / "tasks.py").write_text(tasks_content, encoding='utf-8')
        
        # ایجاد فایل signals.py
        signals_content = f'''from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)

# سیگنال‌های {app_name} اینجا تعریف شوند
'''
        (app_path / "signals.py").write_text(signals_content, encoding='utf-8')
        
        # ایجاد فایل migrations/__init__.py
        migrations_path = app_path / "migrations"
        (migrations_path / "__init__.py").write_text("# Migrations package\n", encoding='utf-8')
    
    def _update_config_files(self, app_name: str, config: dict = None):
        """به‌روزرسانی فایل‌های پیکربندی"""
        logger.info("به‌روزرسانی فایل‌های پیکربندی...")
        
        # به‌روزرسانی فایل اصلی URLs
        main_urls_path = self.base_path / "project_settings" / "urls.py"
        if main_urls_path.exists():
            # اینجا می‌توان URL های جدید را اضافه کرد
            pass
    
    def _print_summary(self, app_name: str, app_path: Path):
        """نمایش خلاصه ایجاد شده"""
        print("\n" + "="*60)
        print(f"🎉 ایجنت برای {app_name} با موفقیت ایجاد شد!")
        print("="*60)
        print(f"📁 مسیر: {app_path}")
        print(f"📅 تاریخ ایجاد: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n📋 فایل‌های ایجاد شده:")
        
        for file_path in app_path.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(app_path)
                print(f"   ✅ {relative_path}")
        
        print("\n🚀 مراحل بعدی:")
        print("   1. بررسی و تکمیل PLAN.md")
        print("   2. پیاده‌سازی مدل‌ها")
        print("   3. ایجاد API endpoints")
        print("   4. نوشتن تست‌ها")
        print("   5. تکمیل مستندات")
        print("\n📚 مستندات:")
        print(f"   📖 {app_path}/README.md")
        print(f"   🔧 {app_path}/docs/TECHNICAL.md")
        print(f"   👥 {app_path}/docs/USER_GUIDE.md")
        print("="*60)

def main():
    """تابع اصلی"""
    parser = argparse.ArgumentParser(description='ایجاد ایجنت جدید برای پلتفرم هلسا')
    parser.add_argument('--app_name', required=True, help='نام اپلیکیشن')
    parser.add_argument('--description', required=True, help='توضیحات اپلیکیشن')
    parser.add_argument('--config', help='فایل پیکربندی JSON')
    
    args = parser.parse_args()
    
    # خواندن پیکربندی
    config = None
    if args.config:
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            logger.error(f"خطا در خواندن فایل پیکربندی: {str(e)}")
            return
    
    # ایجاد ایجنت
    creator = AgentCreator()
    creator.create_agent(args.app_name, args.description, config)

if __name__ == "__main__":
    main()