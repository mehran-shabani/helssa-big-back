# 🌳 نمودار درختی کامل پروژه HELSSA + سیستم ایجنت‌ها

## 📋 فهرست مطالب

- [ساختار کلی پروژه](#ساختار-کلی-پروژه)
- [سیستم ایجنت‌ها](#سیستم-ایجنت‌ها)
- [اپلیکیشن‌های هدف](#اپلیکیشن‌های-هدف)
- [نقشه‌برداری API ها](#نقشه‌برداری-api-ها)
- [ساختار فایل‌ها](#ساختار-فایل‌ها)

---

## 🏗️ ساختار کلی پروژه

```
HELSSA-PLATFORM/
├── 📁 unified_services/          # سرویس‌های یکپارچه و مشترک
│   ├── unified_auth/            # احراز هویت یکپارچه
│   │   ├── models.py            # UnifiedUser, UserRole, UserSession
│   │   ├── views.py             # Authentication views
│   │   ├── serializers.py       # User serializers
│   │   └── permissions.py       # Custom permissions
│   │
│   ├── unified_billing/         # سیستم مالی یکپارچه
│   │   ├── models.py            # Billing, Subscription, Payment
│   │   ├── views.py             # Billing views
│   │   └── services.py          # Payment processing
│   │
│   ├── unified_ai/              # هوش مصنوعی مرکزی
│   │   ├── services.py          # AI service integration
│   │   ├── models.py            # AI models and results
│   │   └── processors.py        # Text/Speech processors
│   │
│   └── unified_access/          # دسترسی یکپارچه
│       ├── models.py            # Access control
│       ├── middleware.py        # Access middleware
│       └── decorators.py        # Access decorators
│
├── 📁 agent_apps/               # اپلیکیشن‌های ایجاد شده توسط ایجنت‌ها
│   ├── patient_chatbot/         # چت‌بات بیمار (اولویت: بالا)
│   │   ├── models.py            # Chat, Message, Session
│   │   ├── views.py             # Chat views
│   │   ├── services.py          # Chat processing
│   │   ├── tests/               # Complete test suite
│   │   └── docs/                # API documentation
│   │
│   ├── doctor_chatbot/          # چت‌بات پزشک (اولویت: بالا)
│   │   ├── models.py            # DoctorChat, MedicalQA
│   │   ├── views.py             # Doctor chat views
│   │   ├── services.py          # Medical AI integration
│   │   ├── tests/               # Complete test suite
│   │   └── docs/                # API documentation
│   │
│   ├── soapify_v2/              # تولید گزارش‌های SOAP (اولویت: بالا)
│   │   ├── models.py            # SOAPReport, MedicalNote
│   │   ├── views.py             # Report generation
│   │   ├── services.py          # SOAP processor
│   │   ├── tests/               # Complete test suite
│   │   └── docs/                # API documentation
│   │
│   ├── prescription_system/      # سیستم نسخه‌نویسی (اولویت: بالا)
│   │   ├── models.py            # Prescription, Medication
│   │   ├── views.py             # Prescription views
│   │   ├── services.py          # Prescription logic
│   │   ├── tests/               # Complete test suite
│   │   └── docs/                # API documentation
│   │
│   ├── patient_records/          # مدیریت پرونده بیمار (اولویت: بالا)
│   │   ├── models.py            # PatientRecord, MedicalHistory
│   │   ├── views.py             # Record management
│   │   ├── services.py          # Record processing
│   │   ├── tests/               # Complete test suite
│   │   └── docs/                # API documentation
│   │
│   ├── visit_management/         # مدیریت ویزیت‌ها (اولویت: متوسط)
│   │   ├── models.py            # Visit, Appointment
│   │   ├── views.py             # Visit management
│   │   ├── services.py          # Scheduling logic
│   │   ├── tests/               # Complete test suite
│   │   └── docs/                # API documentation
│   │
│   ├── telemedicine_core/        # هسته طب از راه دور (اولویت: متوسط)
│   │   ├── models.py            # VideoCall, AudioSession
│   │   ├── views.py             # Telemedicine views
│   │   ├── services.py          # Video/audio processing
│   │   ├── tests/               # Complete test suite
│   │   └── docs/                # API documentation
│   │
│   └── appointment_scheduler/    # زمان‌بندی قرارها (اولویت: متوسط)
│       ├── models.py            # Schedule, TimeSlot
│       ├── views.py             # Scheduling views
│       ├── services.py          # Calendar logic
│       ├── tests/               # Complete test suite
│       └── docs/                # API documentation
│
├── 📁 core_infrastructure/      # زیرساخت اصلی
│   ├── adminplus/               # پنل ادمین پیشرفته
│   ├── analytics/               # تحلیل‌های آماری
│   ├── billing/                 # صورتحساب (Legacy)
│   ├── infra/                   # ابزارهای زیرساختی
│   ├── uploads/                 # مدیریت فایل‌ها
│   └── worker/                  # Celery Workers
│
├── 📁 integrations/             # یکپارچه‌سازی‌ها
│   ├── clients/                 # کلاینت‌های API
│   │   ├── gpt_client.py        # OpenAI/GapGPT
│   │   ├── sms_client.py        # Kavenegar
│   │   └── payment_clients.py   # BitPay/ZarinPal
│   └── webhooks/                # Webhook handlers
│
├── 📁 project_settings/         # تنظیمات پروژه‌ها
│   ├── medogram/                # تنظیمات Medogram
│   │   ├── settings/            # Django settings
│   │   └── urls.py              # URL routing
│   └── soapify/                 # تنظیمات SOAPify
│       ├── settings/            # Django settings
│       └── urls.py              # URL routing
│
├── 📁 deployment/               # استقرار و DevOps
│   ├── docker/                  # Docker configs
│   ├── kubernetes/              # K8s manifests
│   ├── nginx/                   # Nginx configs
│   └── scripts/                 # Deployment scripts
│
├── 📁 documentation/            # مستندات
│   ├── api/                     # API docs
│   ├── architecture/            # معماری
│   ├── guides/                  # راهنماها
│   └── examples/                # نمونه کدها
│
├── 📁 tests/                    # تست‌ها
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   ├── e2e/                     # End-to-end tests
│   └── fixtures/                # Test data
│
├── 📁 static/                   # فایل‌های استاتیک
├── 📁 media/                    # فایل‌های آپلود شده
├── 📁 templates/                # قالب‌های Django
├── 📁 locale/                   # فایل‌های ترجمه
│
├── 📄 docker-compose.yml        # Docker Compose config
├── 📄 Dockerfile                # Docker image
├── 📄 requirements.txt          # Python dependencies
├── 📄 package.json              # Frontend dependencies
├── 📄 manage.py                 # Django management
├── 📄 Makefile                  # Build automation
├── 📄 .env.example              # Environment template
└── 📄 README.md                 # Project documentation
```

---

## 🤖 سیستم ایجنت‌ها

```
agents-system/
├── 📁 AGENT_TEMPLATES/           # قالب‌های استاندارد برای ایجنت‌ها
│   ├── PLAN.md.template         # قالب برنامه‌ریزی
│   ├── CHECKLIST.json.template  # قالب چک‌لیست
│   ├── PROGRESS.json.template   # قالب پیشرفت
│   ├── LOG.md.template          # قالب لاگ
│   └── README.md.template       # قالب مستندات
│
├── 📁 HELSSA_DOCS/              # مستندات کامل پلتفرم هلسا
│   ├── 01-system-overview.md    # نمای کلی سیستم
│   ├── 02-centralized-architecture.md # معماری متمرکز
│   ├── 03-project-tree.md       # نمودار درختی پروژه
│   ├── 04-technology-stack.md   # پشته تکنولوژی
│   ├── 05-authentication.md     # احراز هویت
│   ├── 06-ai-systems.md         # سیستم‌های هوش مصنوعی
│   ├── 07-billing-system.md     # سیستم صورتحساب
│   ├── 08-visits-encounters.md  # ویزیت‌ها و ملاقات‌ها
│   ├── 09-doctor-access.md      # دسترسی پزشکان
│   ├── 10-chatbot-system.md     # سیستم چت‌بات
│   ├── 11-audio-processing.md   # پردازش صوتی
│   ├── 12-output-generation.md  # تولید خروجی
│   ├── 13-infrastructure.md     # زیرساخت
│   ├── 14-api-reference.md      # مرجع API
│   ├── 15-security-compliance.md # امنیت و انطباق
│   ├── 16-deployment-guide.md   # راهنمای استقرار
│   ├── 17-quick-start.md        # شروع سریع
│   └── 18-examples.md           # نمونه‌ها
│
├── 📁 CORE_ARCHITECTURE/        # معماری چهار هسته‌ای
│   ├── README.md                 # راهنمای معماری
│   ├── CORE_ARCHITECTURE.md     # معماری چهار هسته‌ای
│   ├── ARCHITECTURE_CONVENTIONS.md # قراردادهای معماری
│   ├── SECURITY_POLICIES.md     # سیاست‌های امنیتی
│   └── FINAL_CHECKLIST.json     # چک‌لیست نهایی
│
├── 📁 WORKFLOW_ENGINE/          # موتور اجرای فرآیندها
│   ├── create_agent.py          # ایجاد ایجنت جدید
│   ├── run_agent.py             # اجرای ایجنت
│   ├── agent_config.json        # پیکربندی ایجنت
│   └── workflow_templates/      # قالب‌های فرآیند
│
└── 📁 DEPLOYMENT/               # استقرار و DevOps
    ├── docker/                  # Docker configs
    ├── kubernetes/              # K8s manifests
    └── scripts/                 # Deployment scripts
```

---

## 🎯 اپلیکیشن‌های هدف

### اولویت بالا (High Priority)

#### 1. **patient_chatbot** - چت‌بات بیمار
- **هدف**: سیستم چت هوشمند برای بیماران
- **هسته‌های فعال**: API Ingress + Text Processing + Orchestration
- **ویژگی‌ها**: چت، سوالات پزشکی، رزرو نوبت
- **وابستگی‌ها**: unified_auth, unified_ai

#### 2. **doctor_chatbot** - چت‌بات پزشک
- **هدف**: ابزار کمک تشخیص برای پزشکان
- **هسته‌های فعال**: API Ingress + Text Processing + Orchestration
- **ویژگی‌ها**: کمک تشخیص، سوالات پزشکی، منابع
- **وابستگی‌ها**: unified_auth, unified_ai

#### 3. **soapify_v2** - تولید گزارش‌های SOAP
- **هدف**: تولید خودکار گزارش‌های پزشکی استاندارد
- **هسته‌های فعال**: همه چهار هسته
- **ویژگی‌ها**: تولید SOAP، پردازش صوتی، خروجی
- **وابستگی‌ها**: unified_auth, unified_ai, unified_billing

#### 4. **prescription_system** - سیستم نسخه‌نویسی
- **هدف**: ایجاد و مدیریت نسخه‌های دیجیتال
- **هسته‌های فعال**: API Ingress + Text Processing + Orchestration
- **ویژگی‌ها**: نسخه‌نویسی، داروها، دوزها
- **وابستگی‌ها**: unified_auth, unified_billing

#### 5. **patient_records** - مدیریت پرونده بیمار
- **هدف**: سیستم جامع پرونده‌های پزشکی
- **هسته‌های فعال**: API Ingress + Orchestration
- **ویژگی‌ها**: پرونده‌ها، تاریخچه، فایل‌ها
- **وابستگی‌ها**: unified_auth, unified_billing

### اولویت متوسط (Medium Priority)

#### 6. **visit_management** - مدیریت ویزیت‌ها
- **هدف**: سیستم رزرو و مدیریت ویزیت‌های آنلاین
- **هسته‌های فعال**: API Ingress + Orchestration
- **ویژگی‌ها**: رزرو، مدیریت، گزارش‌گیری
- **وابستگی‌ها**: unified_auth, unified_billing

#### 7. **telemedicine_core** - هسته طب از راه دور
- **هدف**: ارتباط ویدئویی و صوتی بین بیمار و پزشک
- **هسته‌های فعال**: API Ingress + Speech Processing + Orchestration
- **ویژگی‌ها**: ویدئو، صدا، چت
- **وابستگی‌ها**: unified_auth, unified_billing

#### 8. **appointment_scheduler** - زمان‌بندی قرارها
- **هدف**: سیستم رزرو نوبت پیشرفته
- **هسته‌های فعال**: API Ingress + Orchestration
- **ویژگی‌ها**: تقویم، زمان‌بندی، یادآوری
- **وابستگی‌ها**: unified_auth, unified_billing

---

## 🔌 نقشه‌برداری API ها

### API Endpoints مشترک

```
/api/v1/
├── auth/                        # احراز هویت
│   ├── login/                   # ورود
│   ├── logout/                  # خروج
│   ├── register/                # ثبت‌نام
│   └── refresh/                 # تمدید توکن
│
├── users/                       # مدیریت کاربران
│   ├── profile/                 # پروفایل
│   ├── settings/                # تنظیمات
│   └── permissions/             # دسترسی‌ها
│
├── billing/                     # صورتحساب
│   ├── invoices/                # فاکتورها
│   ├── payments/                # پرداخت‌ها
│   └── subscriptions/           # اشتراک‌ها
│
└── ai/                          # هوش مصنوعی
    ├── text/                    # پردازش متن
    ├── speech/                  # پردازش صوتی
    └── chat/                    # چت هوشمند
```

### API Endpoints هر اپلیکیشن

هر اپلیکیشن باید API endpoints زیر را داشته باشد:

```
/api/v1/{app_name}/
├── models/                      # CRUD operations
├── actions/                     # Custom actions
├── reports/                     # گزارش‌گیری
└── integrations/                # یکپارچه‌سازی
```

---

## 📁 ساختار فایل‌ها

### ساختار استاندارد هر اپلیکیشن

```
agent_apps/{app_name}/
├── 📄 __init__.py              # Django app initialization
├── 📄 apps.py                  # App configuration
├── 📄 models.py                # Database models
├── 📄 views.py                 # API views
├── 📄 serializers.py           # Data serializers
├── 📄 urls.py                  # URL routing
├── 📄 admin.py                 # Admin interface
├── 📄 permissions.py           # Custom permissions
├── 📄 services.py              # Business logic
├── 📄 tasks.py                 # Celery tasks
├── 📄 signals.py               # Django signals
├── 📄 migrations/              # Database migrations
├── 📁 tests/                   # Test suite
│   ├── 📄 test_models.py       # Model tests
│   ├── 📄 test_views.py        # View tests
│   ├── 📄 test_services.py     # Service tests
│   ├── 📄 test_integrations.py # Integration tests
│   └── 📄 fixtures/            # Test data
├── 📁 docs/                    # Documentation
│   ├── 📄 API.md               # API documentation
│   ├── 📄 USER_GUIDE.md        # User guide
│   └── 📄 TECHNICAL.md         # Technical docs
└── 📁 templates/               # HTML templates
    ├── 📄 base.html            # Base template
    └── 📄 {app_name}/          # App-specific templates
```

### فایل‌های پیکربندی

```
project_settings/
├── 📄 settings.py              # Django settings
├── 📄 urls.py                  # Main URL routing
├── 📄 wsgi.py                  # WSGI configuration
├── 📄 asgi.py                  # ASGI configuration
├── 📄 celery.py                # Celery configuration
└── 📄 requirements.txt          # Dependencies
```

---

## 🚀 مراحل توسعه

### مرحله 1: آماده‌سازی
1. خواندن کامل مستندات معماری
2. بررسی قوانین امنیتی
3. تعیین وابستگی‌ها
4. ایجاد پوشه اپلیکیشن

### مرحله 2: طراحی
1. تکمیل PLAN.md
2. تعریف API endpoints
3. طراحی مدل‌های داده
4. تعیین dependencies

### مرحله 3: پیاده‌سازی
1. ایجاد Django app
2. نوشتن models و migrations
3. پیاده‌سازی چهار هسته
4. ایجاد serializers و views
5. پیکربندی URLs

### مرحله 4: یکپارچه‌سازی
1. ادغام با unified_auth
2. ادغام با unified_billing
3. ادغام با unified_access
4. پیکربندی Kavenegar

### مرحله 5: تست و مستندسازی
1. نوشتن تست‌ها
2. تکمیل مستندات
3. به‌روزرسانی پیشرفت
4. ثبت در لاگ

---

## 🔒 امنیت و انطباق

### قوانین امنیتی
- تمام API endpoints باید احراز هویت شوند
- دسترسی بر اساس نقش کاربر کنترل شود
- تمام ورودی‌ها اعتبارسنجی شوند
- لاگ تمام عملیات ثبت شود
- رمزگذاری داده‌های حساس

### انطباق با استانداردها
- HIPAA برای داده‌های پزشکی
- GDPR برای حریم خصوصی
- ISO 27001 برای امنیت اطلاعات
- WCAG برای دسترسی‌پذیری

---

## 📊 نظارت و گزارش‌گیری

### متریک‌های کلیدی
- تعداد درخواست‌های API
- زمان پاسخ‌دهی
- نرخ خطا
- استفاده از منابع
- فعالیت کاربران

### گزارش‌های خودکار
- گزارش‌های روزانه
- گزارش‌های ماهانه
- گزارش‌های سالانه
- گزارش‌های امنیتی
- گزارش‌های عملکردی