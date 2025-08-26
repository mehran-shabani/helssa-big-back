# 🤖 سیستم ایجنت‌های هوشمند هلسا

## 📋 نمای کلی

این سیستم برای ایجاد خودکار اپلیکیشن‌های پلتفرم هلسا توسط ایجنت‌های هوشمند طراحی شده است. هر ایجنت می‌تواند یک اپلیکیشن کامل را با تمام ویژگی‌ها، تست‌ها و مستندات ایجاد کند.

## 🏗️ ساختار سیستم

```
agents-system/
├── 📁 AGENT_TEMPLATES/           # قالب‌های استاندارد برای ایجنت‌ها
├── 📁 HELSSA_DOCS/              # مستندات کامل پلتفرم هلسا
├── 📁 CORE_ARCHITECTURE/        # معماری چهار هسته‌ای
├── 📁 AGENT_APPS/               # اپلیکیشن‌های ایجاد شده توسط ایجنت‌ها
├── 📁 WORKFLOW_ENGINE/          # موتور اجرای فرآیندها
└── 📁 DEPLOYMENT/               # استقرار و DevOps
```

## 🚀 نحوه استفاده

### 1. راه‌اندازی ایجنت جدید

```bash
# ایجاد ایجنت جدید
python create_agent.py --app_name "patient_chatbot" --description "چت‌بات هوشمند بیماران"

# یا با استفاده از فایل پیکربندی
python create_agent.py --config agent_config.json
```

### 2. پیکربندی ایجنت

```json
{
  "app_name": "patient_chatbot",
  "description": "چت‌بات هوشمند بیماران",
  "core_modules": ["api_ingress", "text_processing", "orchestration"],
  "dependencies": ["unified_auth", "unified_ai"],
  "features": ["chat", "medical_qa", "appointment_booking"],
  "target_framework": "django",
  "database": "postgresql"
}
```

### 3. اجرای ایجنت

```bash
# اجرای کامل
python run_agent.py --app_name "patient_chatbot" --mode "full"

# اجرای مرحله به مرحله
python run_agent.py --app_name "patient_chatbot" --mode "step_by_step"
```

## 🎯 اپلیکیشن‌های هدف

### اولویت بالا
1. **patient_chatbot** - چت‌بات بیمار
2. **doctor_chatbot** - چت‌بات پزشک
3. **soapify_v2** - تولید گزارش‌های SOAP
4. **prescription_system** - سیستم نسخه‌نویسی
5. **patient_records** - مدیریت پرونده بیمار

### اولویت متوسط
6. **visit_management** - مدیریت ویزیت‌ها
7. **telemedicine_core** - هسته طب از راه دور
8. **appointment_scheduler** - زمان‌بندی قرارها

## 🔧 ویژگی‌های سیستم

- ✅ **ایجاد خودکار کد**: تمام فایل‌های مورد نیاز
- ✅ **تست‌های کامل**: Unit, Integration, E2E
- ✅ **مستندات جامع**: API, User Guide, Technical Docs
- ✅ **یکپارچه‌سازی**: با سرویس‌های موجود
- ✅ **امنیت**: رعایت تمام قوانین امنیتی
- ✅ **کیفیت کد**: Linting, Formatting, Best Practices
- ✅ **استقرار**: Docker, Kubernetes, CI/CD

## 📚 مستندات

- [معماری چهار هسته‌ای](./CORE_ARCHITECTURE/README.md)
- [دستورالعمل‌های ایجنت‌ها](./AGENT_TEMPLATES/README.md)
- [مستندات هلسا](./HELSSA_DOCS/README.md)
- [راهنمای استقرار](./DEPLOYMENT/README.md)

## 🚨 نکات مهم

1. **هر ایجنت فقط یک اپلیکیشن ایجاد می‌کند**
2. **تمام قوانین امنیتی باید رعایت شوند**
3. **تست‌ها باید کامل و قابل اجرا باشند**
4. **مستندات باید به زبان فارسی و انگلیسی باشند**
5. **کد باید استانداردهای Django را رعایت کند**

## 📞 پشتیبانی

برای سوالات و مشکلات، لطفاً به مستندات مربوطه مراجعه کنید یا issue جدید ایجاد کنید.
