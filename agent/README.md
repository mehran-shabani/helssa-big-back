# 📚 دستورالعمل‌های ایجنت‌های HELSSA

## 🎯 هدف

این پوشه حاوی دستورالعمل‌های کامل و دقیق برای ایجنت‌های فرعی است که مسئول ساخت اپ‌های مختلف پلتفرم HELSSA هستند.

## 📋 محتویات

```
agent/
├── README.md                      # این فایل
├── ARCHITECTURE_CONVENTIONS.md    # قراردادهای معماری
├── CORE_ARCHITECTURE.md           # هسته‌های مرکزی
├── SECURITY_POLICIES.md           # سیاست‌های امنیتی
├── AGENT_INSTRUCTIONS.md          # دستورالعمل ایجنت‌ها
├── QA_AGENT_INSTRUCTIONS.md       # دستورالعمل QA
├── FINAL_CHECKLIST.json           # چک‌لیست نهایی QA
├── FINAL_REPORT.md                # گزارش نهایی
├── FINAL_SUMMARY.md               # خلاصه نهایی
├── progress_chart_generator.py    # تولید نمودارهای پیشرفت
├── TEMPLATES/                     # تمپلیت‌های اسناد و چک‌لیست
├── docs/                          # مستندات HELSSA-MAIN منتقل‌شده
│   ├── 03-project-tree.md         # ساختار پروژه مرجع
│   └── ...
└── apps/                          # همه اپ‌ها
    ├── patient_chatbot/
    ├── doctor_chatbot/
    ├── doctor_dashboard/
    └── soapify/
```

## 🏗️ معماری کلی

### هسته‌های اصلی (Core Services)

1. **API Ingress Core** - مدیریت ورودی‌ها و اعتبارسنجی
2. **Text Processing Core** - منطق متنی و پردازش زبان طبیعی  
3. **Speech Processing Core** - STT/TTS و مدیریت صوت
4. **Central Orchestration Core** - مدیریت جریان‌ها و سیاست‌ها

### قواعد اساسی

1. **احراز هویت**: همه دسترسی‌ها بر مبنای OTP و کاوه‌نگار
2. **تفکیک نقش‌ها**: مسیرهای جداگانه برای patient و doctor
3. **استانداردها**: رعایت دقیق قراردادهای موجود در HELSSA-MAIN
4. **بدون استثناء**: هیچ اقدام سلیقه‌ای مجاز نیست

## 🚀 نحوه استفاده

هر ایجنت فرعی باید:

1. دستورالعمل مربوط به خود را از پوشه مخصوص بخواند (زیر `agent/apps/<app>`)
2. دقیقاً طبق PLAN.md و CHECKLIST.json عمل کند
3. هرگونه مشکل یا ابهام را در LOG.md ثبت کند
4. پیشرفت خود را در PROGRESS.json به‌روزرسانی کند

## ⚠️ نکات مهم

- تمام خروجی‌ها باید در پوشه `agent/apps/<app_name>/` ذخیره شوند
- هیچ فایلی در خارج از پوشه agent نباید ایجاد یا تغییر کند
- تست‌ها نوشته شوند اما اجرا نشوند
- مستندسازی کامل و دقیق الزامی است

---

تولید شده توسط: ایجنت مادر HELSSA
تاریخ: ${new Date().toISOString()}