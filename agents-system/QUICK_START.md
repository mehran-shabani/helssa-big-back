# 🚀 راهنمای شروع سریع - سیستم ایجنت‌های هلسا

## ⚡ شروع در 5 دقیقه

### مرحله 1: بررسی ساختار سیستم
```bash
cd agents-system
ls -la
```

### مرحله 2: ایجاد اولین اپلیکیشن
```bash
cd WORKFLOW_ENGINE
python create_agent.py --app_name "patient_chatbot" --description "چت‌بات هوشمند بیماران"
```

### مرحله 3: اجرای ایجنت
```bash
python run_agent.py --app_name "patient_chatbot" --mode "full"
```

### مرحله 4: بررسی نتیجه
```bash
cd ../AGENT_APPS/patient_chatbot
ls -la
```

## 📁 ساختار سیستم

```
agents-system/
├── 📁 AGENT_TEMPLATES/           # قالب‌های استاندارد
├── 📁 HELSSA_DOCS/              # مستندات کامل هلسا
├── 📁 CORE_ARCHITECTURE/        # معماری چهار هسته‌ای
├── 📁 WORKFLOW_ENGINE/          # موتور اجرای فرآیندها
├── 📁 AGENT_APPS/               # اپلیکیشن‌های ایجاد شده
└── 📁 DEPLOYMENT/               # استقرار و DevOps
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

## 🔧 دستورات کلیدی

### ایجاد ایجنت جدید
```bash
python create_agent.py --app_name "نام_اپ" --description "توضیحات"
```

### اجرای کامل ایجنت
```bash
python run_agent.py --app_name "نام_اپ" --mode "full"
```

### اجرای مرحله به مرحله
```bash
python run_agent.py --app_name "نام_اپ" --mode "step_by_step"
```

## 📚 مستندات کلیدی

- **README.md** - راهنمای اصلی سیستم
- **AGENT_INSTRUCTIONS.md** - دستورالعمل‌های جامع
- **PROJECT_TREE.md** - نمودار درختی کامل
- **EXAMPLE_USAGE.md** - مثال‌های استفاده
- **FINAL_SUMMARY.md** - خلاصه نهایی

## 🏗️ معماری چهار هسته‌ای

1. **API Ingress Core** - مدیریت HTTP requests
2. **Text Processing Core** - پردازش زبان طبیعی
3. **Speech Processing Core** - پردازش صوت
4. **Orchestration Core** - هماهنگی و مدیریت

## 🔗 یکپارچه‌سازی

- **unified_auth** - احراز هویت یکپارچه
- **unified_billing** - سیستم مالی یکپارچه
- **unified_ai** - هوش مصنوعی مرکزی
- **unified_access** - کنترل دسترسی یکپارچه

## 🧪 تست‌ها

هر اپلیکیشن شامل:
- Unit Tests
- Integration Tests
- API Tests
- Security Tests

## 📊 نظارت

- متریک‌های عملکرد
- گزارش‌های خودکار
- لاگ‌های امنیتی
- نظارت بر منابع

## 🚨 نکات مهم

1. **هر ایجنت فقط یک اپلیکیشن ایجاد می‌کند**
2. **تمام قوانین امنیتی باید رعایت شوند**
3. **تست‌ها باید کامل و قابل اجرا باشند**
4. **مستندات باید به زبان فارسی و انگلیسی باشند**

## 🎉 نتیجه

با استفاده از این سیستم، هر ایجنت می‌تواند در کمتر از 10 دقیقه یک اپلیکیشن کامل و آماده برای تولید ایجاد کند.

---

**برای اطلاعات بیشتر**: مطالعه AGENT_INSTRUCTIONS.md و EXAMPLE_USAGE.md