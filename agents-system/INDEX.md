# 🗂️ فهرست دستورالعمل‌های ایجنت‌های HELSSA

## 📋 نمای کلی

این پوشه حاوی دستورالعمل‌های کامل برای ایجنت‌هایی است که مسئول توسعه اپ‌های مختلف پلتفرم HELSSA هستند.

## 📁 ساختار پوشه

```
AGENT/
├── INDEX.md                      # این فایل
├── README.md                     # راهنمای کلی
├── ARCHITECTURE_CONVENTIONS.md   # قراردادهای معماری
├── FINAL_CHECKLIST.json         # چک‌لیست نهایی QA
├── FINAL_REPORT.md              # گزارش نهایی
├── overall_progress.svg         # نمودار پیشرفت کلی
│
├── patient_chatbot/             # دستورالعمل چت‌بات بیمار
│   ├── PLAN.md
│   ├── CHECKLIST.json
│   ├── PROGRESS.json
│   ├── LOG.md
│   ├── README.md
│   └── charts/
│       └── progress_doughnut.svg
│
├── doctor_chatbot/              # دستورالعمل چت‌بات پزشک
│   ├── PLAN.md
│   ├── CHECKLIST.json
│   ├── PROGRESS.json
│   ├── LOG.md
│   ├── README.md
│   └── charts/
│       └── progress_doughnut.svg
│
├── soapify/                     # دستورالعمل SOAPify
│   ├── PLAN.md
│   ├── CHECKLIST.json
│   ├── PROGRESS.json
│   ├── LOG.md
│   ├── README.md
│   └── charts/
│       └── progress_doughnut.svg
│
└── doctor_dashboard/            # دستورالعمل داشبورد پزشک
    ├── PLAN.md
    ├── CHECKLIST.json
    ├── PROGRESS.json
    ├── LOG.md
    ├── README.md
    └── charts/
        └── progress_doughnut.svg
```

## 🎯 نحوه استفاده

### برای ایجنت‌های فرعی

1. **انتخاب اپ**: به پوشه مربوط به اپ خود بروید
2. **مطالعه README.md**: ابتدا فایل README.md را بخوانید
3. **بررسی PLAN.md**: جزئیات فنی و معماری را مطالعه کنید
4. **پیروی از CHECKLIST.json**: گام به گام طبق چک‌لیست پیش بروید
5. **به‌روزرسانی PROGRESS.json**: پیشرفت خود را ثبت کنید
6. **ثبت در LOG.md**: همه تصمیمات و تغییرات را لاگ کنید

### برای مدیران پروژه

1. **FINAL_REPORT.md**: خلاصه وضعیت کل پروژه
2. **FINAL_CHECKLIST.json**: وضعیت آماده‌سازی همه اپ‌ها
3. **overall_progress.svg**: نمایش گرافیکی پیشرفت

## 🔑 نکات کلیدی

### قواعد اجرا
- ✅ هیچ تغییری در دستورالعمل‌ها ایجاد نکنید
- ✅ دقیقاً طبق PLAN.md عمل کنید
- ✅ هرگونه انحراف را در LOG.md ثبت کنید
- ✅ از قراردادهای ARCHITECTURE_CONVENTIONS.md پیروی کنید

### اولویت‌ها
1. **امنیت**: احراز هویت OTP، رمزنگاری، HIPAA
2. **کیفیت**: کد تمیز، تست‌ها، مستندات
3. **عملکرد**: رعایت محدودیت‌های زمانی
4. **یکپارچگی**: هماهنگی با هسته‌های مرکزی

## 📞 ارتباط

در صورت نیاز به توضیحات بیشتر:
- مستندات HELSSA-MAIN را مطالعه کنید
- انحرافات و مشکلات را در LOG.md ثبت کنید
- از الگوهای موجود در پروژه اصلی استفاده کنید

---

**آخرین به‌روزرسانی**: 2024-01-20
**وضعیت**: آماده برای اجرا توسط ایجنت‌های فرعی