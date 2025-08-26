# 🤖 راهنمای کامل ایجنت‌های HELSSA

## 📋 نمای کلی

این مجموعه شامل تمام ابزارها، قالب‌ها و دستورالعمل‌های لازم برای ایجنت‌هایی است که اپلیکیشن‌های مختلف پلتفرم HELSSA را بر اساس معماری چهار هسته‌ای می‌سازند.

## 🎯 نحوه استفاده برای ایجنت‌ها

### گام 1: انتخاب اپلیکیشن
ایجنت باید یکی از اپلیکیشن‌های زیر را انتخاب کند:

#### 🔥 اولویت بالا (شروع فوری)
1. **patient_chatbot** - چت‌بات بیمار
2. **prescription_system** - سیستم نسخه‌نویسی  
3. **soapify** - تولید گزارش‌های SOAP (تکمیل)
4. **doctor-chatbot-a** - چت‌بات پزشک (تکمیل)

#### ⚡ اولویت متوسط
5. **patient_records** - مدیریت پرونده بیمار
6. **visit_management** - مدیریت ویزیت‌ها
7. **appointment_scheduler** - زمان‌بندی قرارها
8. **doctor-dashboard** - داشبورد پزشک (تکمیل)

#### 📈 اولویت پایین
9. **telemedicine_core** - هسته طب از راه دور
10. **unified_auth_integration** - یکپارچه‌سازی احراز هویت
11. **unified_billing_integration** - یکپارچه‌سازی مالی
12. **unified_ai_integration** - یکپارچه‌سازی AI
13. **admin_dashboard** - پنل ادمین
14. **analytics_system** - سیستم تحلیل‌ها
15. **notification_system** - سیستم اطلاع‌رسانی

### گام 2: مطالعه مستندات
```bash
# خواندن دستورالعمل‌های کلی
cat AGENT_INSTRUCTIONS.md

# مطالعه معماری چهار هسته‌ای  
cat CORE_ARCHITECTURE.md

# بررسی سیاست‌های امنیتی
cat SECURITY_POLICIES.md

# مطالعه مستندات HELSSA اصلی
ls HELSSA_DOCS/
```

### گام 3: بررسی اپلیکیشن انتخابی
```bash
cd {APP_NAME}/

# اگر PLAN.md وجود دارد، مطالعه کنید
cat PLAN.md

# اگر وجود ندارد، از template استفاده کنید
cp ../TEMPLATES/plan_template.md PLAN.md

# CHECKLIST.json را بررسی کنید
cat CHECKLIST.json
```

### گام 4: تکمیل برنامه تفصیلی
```bash
# PLAN.md را ویرایش کنید و placeholder های زیر را جایگزین کنید:
# - {APP_NAME}
# - {APP_DESCRIPTION}  
# - {MainModel}
# - {PRIMARY_WORKFLOW}
# - {API_ENDPOINTS}
# - سایر متغیرها
```

### گام 5: پیاده‌سازی کد
```bash
cd app_code/

# فایل‌های اصلی را کامل کنید:
# - models.py (مدل‌های داده)
# - serializers.py (DRF serializers)
# - views.py (API endpoints)
# - cores/ (چهار هسته)

# فایل‌های cores:
# - api_ingress.py (مدیریت API)
# - text_processor.py (پردازش متن/AI)
# - speech_processor.py (پردازش صوت)
# - orchestrator.py (منطق کسب و کار)
```

### گام 6: پیکربندی deployment
```bash
cd deployment/

# تنظیمات Django
vi settings_additions.py

# پیکربندی URLs  
vi urls_additions.py

# کتابخانه‌های مورد نیاز
vi requirements_additions.txt
```

### گام 7: نوشتن تست‌ها
```bash
cd app_code/tests/

# تست‌ها را بنویسید اما اجرا نکنید:
# - test_models.py
# - test_views.py
# - test_serializers.py
# - test_integration.py
```

### گام 8: تکمیل مستندات
```bash
# README.md اپلیکیشن
vi README.md

# API specification
vi docs/api_spec.yaml

# راهنمای کاربر
vi docs/user_manual.md
```

### گام 9: به‌روزرسانی پیشرفت
```bash
# PROGRESS.json را به‌روزرسانی کنید
vi PROGRESS.json

# تصمیمات و تغییرات را در LOG.md ثبت کنید
vi LOG.md
```

## 📁 ساختار استاندارد هر اپلیکیشن

```
{APP_NAME}/
├── 📄 PLAN.md                    # برنامه تفصیلی (اجباری)
├── 📄 CHECKLIST.json             # چک‌لیست اجرا (اجباری)
├── 📄 PROGRESS.json              # گزارش پیشرفت (اجباری)
├── 📄 LOG.md                     # لاگ تصمیم‌ها (اجباری)
├── 📄 README.md                  # مستندات اپ (اجباری)
│
├── 📁 app_code/                  # کد اپلیکیشن (اجباری)
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py                 # مدل‌های Django
│   ├── admin.py                  # پنل ادمین
│   ├── serializers.py            # DRF serializers
│   ├── views.py                  # API views
│   ├── urls.py                   # URL routing
│   ├── permissions.py            # مجوزها
│   │
│   ├── 📁 cores/                 # چهار هسته (اجباری)
│   │   ├── __init__.py
│   │   ├── api_ingress.py        # هسته ورودی API
│   │   ├── text_processor.py     # هسته پردازش متن
│   │   ├── speech_processor.py   # هسته پردازش صوت
│   │   └── orchestrator.py       # هسته ارکستراسیون
│   │
│   ├── 📁 migrations/            # Django migrations
│   │   └── __init__.py
│   │
│   └── 📁 tests/                 # تست‌ها (نوشته شده، اجرا نشده)
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_views.py
│       ├── test_serializers.py
│       └── test_integration.py
│
├── 📁 deployment/                # پیکربندی استقرار (اجباری)
│   ├── settings_additions.py    # تنظیمات Django
│   ├── urls_additions.py        # اضافات URL
│   └── requirements_additions.txt # کتابخانه‌های مورد نیاز
│
├── 📁 docs/                      # مستندات
│   ├── api_spec.yaml            # OpenAPI spec
│   ├── user_manual.md           # راهنمای کاربر
│   └── admin_guide.md           # راهنمای مدیر
│
└── 📁 charts/                    # نمودارهای پیشرفت
    └── progress_doughnut.svg
```

## 🔧 الگوهای کدنویسی اجباری

### 1. Import Pattern
```python
# الگوی صحیح imports
from django.contrib.auth import get_user_model
from rest_framework import status, serializers, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

# Unified integrations
from unified_auth.models import UnifiedUser
from unified_billing.services import UnifiedBillingService
from unified_access.decorators import require_patient_access

User = get_user_model()
```

### 2. View Pattern
```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@unified_auth_required(user_types=['patient', 'doctor'])
def standard_endpoint(request):
    orchestrator = CentralOrchestrator()
    
    try:
        # 1. Validation
        serializer = RequestSerializer(data=request.data)
        if not serializer.is_valid():
            return orchestrator.api_ingress.create_error_response(
                "ورودی نامعتبر"
            )
        
        # 2. Execute through orchestrator
        result = orchestrator.execute_primary_workflow(
            request_data=serializer.validated_data,
            user=request.user
        )
        
        # 3. Return response
        return orchestrator.api_ingress.create_success_response(result)
        
    except Exception as e:
        logger.error(f"Endpoint error: {str(e)}")
        return orchestrator.api_ingress.create_error_response(
            "خطای داخلی سرور"
        )
```

### 3. Model Pattern
```python
class StandardModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
```

## ⚠️ نکات مهم و ممنوعیت‌ها

### 🚫 ممنوعیت‌ها
1. **تغییر معماری**: چهار هسته‌ای اجباری است
2. **User model جدید**: فقط از UnifiedUser استفاده کنید
3. **Raw SQL**: فقط Django ORM مجاز است
4. **Hard-coded values**: همه چیز configurable باشد
5. **عمل سلیقه‌ای**: فقط طبق دستورالعمل کار کنید

### ✅ الزامات
1. **ثبت همه تغییرات**: در LOG.md
2. **پیروی از الگوها**: در تمام کدها
3. **Error handling**: استاندارد و کامل
4. **Security first**: امنیت در اولویت اول
5. **Documentation**: کامل و دقیق

## 🔐 تنظیمات امنیتی اجباری

### احراز هویت
```python
# استفاده از unified_auth در همه endpoints
@unified_auth_required(user_types=['patient', 'doctor'])
def secure_endpoint(request):
    pass
```

### OTP و Kavenegar
```python
# ارسال کد تایید
from unified_auth.services import UnifiedOTPService
otp_service = UnifiedOTPService()
result = otp_service.send_otp(phone_number, purpose='verification')
```

### دسترسی بر اساس نوع کاربر
```python
if request.user.user_type == 'patient':
    # منطق بیمار
elif request.user.user_type == 'doctor':
    # منطق پزشک
```

## 📊 نظارت و گزارش‌دهی

### پیشرفت پروژه
```bash
# بررسی پیشرفت کلی
python progress_chart_generator.py

# بررسی وضعیت همه اپ‌ها
cat FINAL_CHECKLIST.json
```

### لاگ‌ها
```python
# الگوی لاگ‌گذاری
import logging
logger = logging.getLogger(__name__)

logger.info(f"Operation started for {APP_NAME}")
logger.error(f"Error in {operation}: {str(e)}")
```

## 🚀 فرایند تکمیل و تحویل

### 1. خودبررسی
```bash
# بررسی checklist
cat CHECKLIST.json | grep -c "completed"

# بررسی فایل‌های اجباری
ls app_code/cores/
ls deployment/
```

### 2. تست کیفیت
```bash
# بررسی syntax
python -m py_compile app_code/*.py

# بررسی imports
python -c "from app_code import models, views, serializers"
```

### 3. آماده‌سازی تحویل
```bash
# به‌روزرسانی نهایی PROGRESS.json
vi PROGRESS.json

# ثبت خلاصه در LOG.md
echo "## تکمیل نهایی - $(date)" >> LOG.md
```

## 📞 پشتیبانی و راهنمایی

### منابع
- **AGENT_INSTRUCTIONS.md**: دستورالعمل‌های کامل
- **CORE_ARCHITECTURE.md**: معماری چهار هسته‌ای
- **SECURITY_POLICIES.md**: سیاست‌های امنیتی
- **HELSSA_DOCS/**: مستندات کامل پروژه اصلی

### قوانین مهم
1. هرگز از دستورالعمل انحراف نکنید
2. همه تغییرات را در LOG.md ثبت کنید
3. امنیت و کیفیت را فدا نکنید
4. از الگوهای استاندارد پیروی کنید
5. مستندسازی را جدی بگیرید

---

**نکته نهایی**: هر ایجنت باید مستقلاً کار کند و در پایان یک اپلیکیشن کامل، تست شده و آماده برای ادغام با سیستم اصلی تحویل دهد.

موفق باشید! 🎯