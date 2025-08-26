# 🌳 ساختار کامل پروژه HELSSA برای ایجنت‌ها

## 📋 نمای کلی

این سند ساختار کامل پروژه HELSSA را برای ایجنت‌هایی که اپلیکیشن‌ها را می‌سازند تعریف می‌کند.

## 🏗️ ساختار درختی کامل

```
HELSSA_AGENTS/
├── 📁 HELSSA_DOCS/                     # مستندات اصلی HELSSA
│   ├── 01-system-overview.md
│   ├── 02-centralized-architecture.md
│   ├── 03-project-tree.md
│   ├── 04-technology-stack.md
│   ├── 05-authentication.md
│   ├── 06-ai-systems.md
│   ├── 07-billing-system.md
│   ├── 08-visits-encounters.md
│   ├── 09-doctor-access.md
│   ├── 10-chatbot-system.md
│   ├── 11-audio-processing.md
│   ├── 12-output-generation.md
│   ├── 13-infrastructure.md
│   ├── 14-api-reference.md
│   ├── 15-security-compliance.md
│   ├── 16-deployment-guide.md
│   ├── 17-quick-start.md
│   └── 18-examples.md
│
├── 📄 INDEX.md                        # راهنمای کلی ایجنت‌ها
├── 📄 README.md                       # راهنمای اجرا
├── 📄 AGENT_INSTRUCTIONS.md           # دستورالعمل‌های ایجنت
├── 📄 CORE_ARCHITECTURE.md            # معماری چهار هسته‌ای
├── 📄 ARCHITECTURE_CONVENTIONS.md     # قراردادهای معماری
├── 📄 SECURITY_POLICIES.md            # سیاست‌های امنیتی
├── 📄 QA_AGENT_INSTRUCTIONS.md        # دستورالعمل ایجنت QA
├── 📄 FINAL_CHECKLIST.json            # چک‌لیست نهایی
├── 📄 FINAL_REPORT.md                 # گزارش نهایی
├── 📄 FINAL_SUMMARY.md                # خلاصه نهایی
├── 📄 progress_chart_generator.py     # تولید نمودارهای پیشرفت
│
├── 📁 TEMPLATES/                      # قالب‌های استاندارد
│   ├── app_template/                  # قالب کلی اپلیکیشن
│   ├── plan_template.md               # قالب PLAN.md
│   ├── checklist_template.json        # قالب CHECKLIST.json
│   ├── progress_template.json         # قالب PROGRESS.json
│   ├── readme_template.md             # قالب README.md
│   └── log_template.md                # قالب LOG.md
│
├── 📁 charts-all/                     # نمودارهای کلی پروژه
│   └── overall_progress.svg
│
│ ╔══════════════════════════════════════════════════════════════════════════════╗
│ ║                          PATIENT APPLICATIONS (Medogram)                      ║
│ ╚══════════════════════════════════════════════════════════════════════════════╝
│
├── 📁 patient_chatbot/               # چت‌بات بیمار
│   ├── PLAN.md                       # برنامه تفصیلی
│   ├── CHECKLIST.json                # چک‌لیست اجرا
│   ├── PROGRESS.json                 # گزارش پیشرفت
│   ├── LOG.md                        # لاگ تصمیم‌ها
│   ├── README.md                     # مستندات اپ
│   ├── charts/
│   │   └── progress_doughnut.svg
│   ├── app_code/                     # کد اپلیکیشن
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py                 # ChatSession, ChatMessage, PatientProfile
│   │   ├── admin.py
│   │   ├── serializers.py            # ChatMessageSerializer, SessionSerializer
│   │   ├── views.py                  # chat_endpoint, get_history
│   │   ├── urls.py
│   │   ├── permissions.py            # PatientOnlyPermission
│   │   ├── cores/                    # چهار هسته
│   │   │   ├── __init__.py
│   │   │   ├── api_ingress.py        # API validation و authentication
│   │   │   ├── text_processor.py     # Medical AI processing
│   │   │   ├── speech_processor.py   # STT integration
│   │   │   └── orchestrator.py       # Business logic
│   │   ├── migrations/
│   │   └── tests/
│   ├── deployment/
│   │   ├── settings_additions.py
│   │   ├── urls_additions.py
│   │   └── requirements_additions.txt
│   └── docs/
│       ├── api_spec.yaml
│       ├── user_manual.md
│       └── admin_guide.md
│
├── 📁 patient_records/               # مدیریت پرونده بیمار
│   ├── PLAN.md
│   ├── CHECKLIST.json
│   ├── PROGRESS.json
│   ├── LOG.md
│   ├── README.md
│   ├── charts/
│   ├── app_code/
│   │   ├── models.py                 # PatientRecord, MedicalHistory, Allergies
│   │   ├── views.py                  # get_records, update_record
│   │   ├── serializers.py
│   │   └── cores/
│   ├── deployment/
│   └── docs/
│
├── 📁 appointment_scheduler/         # زمان‌بندی قرارها
│   ├── PLAN.md
│   ├── CHECKLIST.json
│   ├── PROGRESS.json
│   ├── LOG.md
│   ├── README.md
│   ├── charts/
│   ├── app_code/
│   │   ├── models.py                 # Appointment, DoctorSchedule, TimeSlot
│   │   ├── views.py                  # book_appointment, get_available_slots
│   │   ├── serializers.py
│   │   └── cores/
│   ├── deployment/
│   └── docs/
│
├── 📁 telemedicine_core/            # هسته طب از راه دور
│   ├── PLAN.md
│   ├── CHECKLIST.json
│   ├── PROGRESS.json
│   ├── LOG.md
│   ├── README.md
│   ├── charts/
│   ├── app_code/
│   │   ├── models.py                 # VideoCall, CallSession, CallRecord
│   │   ├── views.py                  # start_call, join_call, end_call
│   │   ├── serializers.py
│   │   └── cores/
│   ├── deployment/
│   └── docs/
│
│ ╔══════════════════════════════════════════════════════════════════════════════╗
│ ║                          DOCTOR APPLICATIONS (SOAPify)                        ║
│ ╚══════════════════════════════════════════════════════════════════════════════╝
│
├── 📁 doctor-chatbot-a/             # چت‌بات پزشک (موجود)
│   ├── PLAN.md
│   ├── CHECKLIST.json
│   ├── PROGRESS.json
│   ├── LOG.md
│   ├── README.md
│   ├── charts/
│   ├── app_code/
│   │   ├── models.py                 # DoctorChat, MedicalQuery, DiagnosisAssist
│   │   ├── views.py                  # medical_consultation, get_diagnosis_help
│   │   ├── serializers.py
│   │   └── cores/
│   ├── deployment/
│   └── docs/
│
├── 📁 doctor-dashboard/             # داشبورد پزشک (موجود)
│   ├── PLAN.md
│   ├── CHECKLIST.json
│   ├── PROGRESS.json
│   ├── LOG.md
│   ├── README.md
│   ├── charts/
│   ├── app_code/
│   │   ├── models.py                 # DoctorProfile, DashboardMetrics, Analytics
│   │   ├── views.py                  # get_dashboard, get_analytics
│   │   ├── serializers.py
│   │   └── cores/
│   ├── deployment/
│   └── docs/
│
├── 📁 soapify/                      # تولید گزارش‌های SOAP (موجود)
│   ├── PLAN.md
│   ├── CHECKLIST.json
│   ├── PROGRESS.json
│   ├── LOG.md
│   ├── README.md
│   ├── charts/
│   ├── app_code/
│   │   ├── models.py                 # SOAPNote, EncounterRecord, AudioTranscript
│   │   ├── views.py                  # generate_soap, process_audio
│   │   ├── serializers.py
│   │   └── cores/
│   ├── deployment/
│   └── docs/
│
├── 📁 prescription_system/          # سیستم نسخه‌نویسی
│   ├── PLAN.md
│   ├── CHECKLIST.json
│   ├── PROGRESS.json
│   ├── LOG.md
│   ├── README.md
│   ├── charts/
│   ├── app_code/
│   │   ├── models.py                 # Prescription, Medication, Dosage
│   │   ├── views.py                  # create_prescription, verify_prescription
│   │   ├── serializers.py
│   │   └── cores/
│   ├── deployment/
│   └── docs/
│
├── 📁 visit_management/             # مدیریت ویزیت‌ها
│   ├── PLAN.md
│   ├── CHECKLIST.json
│   ├── PROGRESS.json
│   ├── LOG.md
│   ├── README.md
│   ├── charts/
│   ├── app_code/
│   │   ├── models.py                 # Visit, VisitSession, VisitNotes
│   │   ├── views.py                  # start_visit, end_visit, take_notes
│   │   ├── serializers.py
│   │   └── cores/
│   ├── deployment/
│   └── docs/
│
│ ╔══════════════════════════════════════════════════════════════════════════════╗
│ ║                              SHARED SERVICES                                  ║
│ ╚══════════════════════════════════════════════════════════════════════════════╝
│
├── 📁 unified_auth_integration/     # یکپارچه‌سازی احراز هویت
│   ├── PLAN.md
│   ├── CHECKLIST.json
│   ├── PROGRESS.json
│   ├── LOG.md
│   ├── README.md
│   ├── charts/
│   ├── app_code/
│   │   ├── models.py                 # UserProfile, OTPSession, LoginAttempt
│   │   ├── views.py                  # unified_login, send_otp, verify_otp
│   │   ├── serializers.py
│   │   └── cores/
│   ├── deployment/
│   └── docs/
│
├── 📁 unified_billing_integration/  # یکپارچه‌سازی سیستم مالی
│   ├── PLAN.md
│   ├── CHECKLIST.json
│   ├── PROGRESS.json
│   ├── LOG.md
│   ├── README.md
│   ├── charts/
│   ├── app_code/
│   │   ├── models.py                 # BillingSession, PaymentRecord, Subscription
│   │   ├── views.py                  # charge_service, check_balance
│   │   ├── serializers.py
│   │   └── cores/
│   ├── deployment/
│   └── docs/
│
├── 📁 unified_ai_integration/       # یکپارچه‌سازی هوش مصنوعی
│   ├── PLAN.md
│   ├── CHECKLIST.json
│   ├── PROGRESS.json
│   ├── LOG.md
│   ├── README.md
│   ├── charts/
│   ├── app_code/
│   │   ├── models.py                 # AIRequest, AIResponse, UsageLog
│   │   ├── views.py                  # process_ai_request, get_ai_response
│   │   ├── serializers.py
│   │   └── cores/
│   ├── deployment/
│   └── docs/
│
│ ╔══════════════════════════════════════════════════════════════════════════════╗
│ ║                              ADMIN & MONITORING                               ║
│ ╚══════════════════════════════════════════════════════════════════════════════╝
│
├── 📁 admin_dashboard/              # پنل ادمین
│   ├── PLAN.md
│   ├── CHECKLIST.json
│   ├── PROGRESS.json
│   ├── LOG.md
│   ├── README.md
│   ├── charts/
│   ├── app_code/
│   │   ├── models.py                 # AdminAction, SystemMetrics, UserAnalytics
│   │   ├── views.py                  # admin_dashboard, system_health
│   │   ├── serializers.py
│   │   └── cores/
│   ├── deployment/
│   └── docs/
│
├── 📁 analytics_system/             # سیستم تحلیل‌ها
│   ├── PLAN.md
│   ├── CHECKLIST.json
│   ├── PROGRESS.json
│   ├── LOG.md
│   ├── README.md
│   ├── charts/
│   ├── app_code/
│   │   ├── models.py                 # UserBehavior, AppUsage, PerformanceMetric
│   │   ├── views.py                  # get_analytics, generate_reports
│   │   ├── serializers.py
│   │   └── cores/
│   ├── deployment/
│   └── docs/
│
└── 📁 notification_system/         # سیستم اطلاع‌رسانی
    ├── PLAN.md
    ├── CHECKLIST.json
    ├── PROGRESS.json
    ├── LOG.md
    ├── README.md
    ├── charts/
    ├── app_code/
    │   ├── models.py                 # Notification, NotificationTemplate, SMSLog
    │   ├── views.py                  # send_notification, get_notifications
    │   ├── serializers.py
    │   └── cores/
    ├── deployment/
    └── docs/
```

## 🎯 اپلیکیشن‌های اولویت‌دار برای ایجنت‌ها

### اولویت بالا (شروع فوری)
1. **patient_chatbot** - چت‌بات بیمار
2. **doctor-chatbot-a** - چت‌بات پزشک (تکمیل)
3. **soapify** - تولید گزارش‌های SOAP (تکمیل)
4. **prescription_system** - سیستم نسخه‌نویسی

### اولویت متوسط
5. **doctor-dashboard** - داشبورد پزشک (تکمیل)
6. **patient_records** - مدیریت پرونده بیمار
7. **visit_management** - مدیریت ویزیت‌ها
8. **appointment_scheduler** - زمان‌بندی قرارها

### اولویت پایین
9. **telemedicine_core** - هسته طب از راه دور
10. **unified_auth_integration** - یکپارچه‌سازی احراز هویت
11. **unified_billing_integration** - یکپارچه‌سازی مالی
12. **unified_ai_integration** - یکپارچه‌سازی AI
13. **admin_dashboard** - پنل ادمین
14. **analytics_system** - سیستم تحلیل‌ها
15. **notification_system** - سیستم اطلاع‌رسانی

## 🔌 API Endpoints مورد نیاز

### Patient APIs
- `POST /api/patient_chatbot/chat/` - شروع چت با بیمار
- `GET /api/patient_chatbot/history/` - تاریخچه چت‌ها
- `POST /api/patient_records/create/` - ایجاد پرونده
- `GET /api/patient_records/get/{id}/` - دریافت پرونده
- `POST /api/appointment_scheduler/book/` - رزرو قرار
- `GET /api/appointment_scheduler/available/` - نوبت‌های آزاد
- `POST /api/telemedicine_core/start_call/` - شروع تماس ویدئویی

### Doctor APIs
- `POST /api/doctor-chatbot-a/consultation/` - مشاوره پزشکی
- `POST /api/soapify/generate/` - تولید گزارش SOAP
- `POST /api/soapify/process_audio/` - پردازش فایل صوتی
- `POST /api/prescription_system/create/` - ایجاد نسخه
- `GET /api/doctor-dashboard/analytics/` - آمار داشبورد
- `POST /api/visit_management/start/` - شروع ویزیت
- `POST /api/visit_management/notes/` - ثبت یادداشت

### Shared APIs
- `POST /api/unified_auth/login/` - ورود یکپارچه
- `POST /api/unified_auth/send_otp/` - ارسال کد تایید
- `POST /api/unified_billing/charge/` - پرداخت خدمات
- `POST /api/unified_ai/process/` - پردازش با AI
- `GET /api/analytics_system/reports/` - گزارش‌های آماری
- `POST /api/notification_system/send/` - ارسال اطلاع‌رسانی

## 📝 نکات مهم برای ایجنت‌ها

1. **ساختار یکپارچه**: همه اپلیکیشن‌ها باید از معماری چهار هسته‌ای پیروی کنند
2. **امنیت محور**: احراز هویت OTP و رمزنگاری در همه جا
3. **یکپارچگی**: استفاده از unified services برای auth، billing و AI
4. **مستندسازی**: هر اپ باید README، API spec و راهنمای کاربر داشته باشد
5. **تست‌پذیری**: تست‌های واحد و یکپارچگی برای همه اپ‌ها
6. **قابلیت نگهداری**: کد تمیز، استاندارد و قابل توسعه

## 🚀 دستورالعمل اجرا برای ایجنت‌ها

1. ایجنت هر اپ را انتخاب می‌کند
2. PLAN.md را مطالعه می‌کند (یا ایجاد می‌کند)
3. طبق CHECKLIST.json پیش می‌رود
4. کد را در app_code/ می‌نویسد
5. PROGRESS.json را به‌روزرسانی می‌کند
6. تغییرات را در LOG.md ثبت می‌کند
7. مستندات را تکمیل می‌کند

این ساختار تضمین می‌کند که هر ایجنت بتواند مستقلاً کار کند و در نهایت یک سیستم یکپارچه و کامل تحویل دهد.