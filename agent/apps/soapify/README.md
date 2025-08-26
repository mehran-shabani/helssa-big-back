# 🤖 Patient Chatbot - دستورالعمل اجرایی

## 📋 خلاصه

این دستورالعمل برای ایجنتی است که مسئول ساخت چت‌بات بیمار HELSSA است. تمام جزئیات لازم برای پیاده‌سازی در این پوشه موجود است.

## 🎯 مأموریت شما

شما باید:
1. `PLAN.md` را به دقت مطالعه کنید
2. طبق `CHECKLIST.json` پیش بروید
3. هر تغییر را در `LOG.md` ثبت کنید
4. پیشرفت را در `PROGRESS.json` به‌روزرسانی کنید

## 📁 فایل‌های راهنما

- **PLAN.md**: طرح کامل توسعه با جزئیات فنی
- **CHECKLIST.json**: لیست دقیق کارها با اولویت‌بندی
- **PROGRESS.json**: وضعیت پیشرفت (باید به‌روزرسانی کنید)
- **LOG.md**: ثبت تصمیمات و تغییرات
- **charts/**: نمودارهای پیشرفت (بعداً تولید می‌شود)

## 🏗️ ساختار خروجی مورد انتظار

```
agent/patient_chatbot/
├── src/                    # کد منبع اپ
│   ├── models/
│   ├── services/
│   ├── api/
│   ├── agents/            # OpenAI Agents
│   ├── utils/
│   └── tests/
├── docs/                   # مستندات تکمیلی
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── TROUBLESHOOTING.md
├── configs/                # تنظیمات نمونه
│   ├── settings_snippet.py
│   └── urls_snippet.py
└── requirements.txt        # وابستگی‌های اپ
```

## ⚠️ نکات حیاتی

### 1. رعایت دقیق معماری

```python
# اتصال به هسته‌ها فقط از طریق interfaces تعریف شده
from core.api_ingress import validate_request
from core.text_processing import process_medical_text
from core.speech_processing import convert_speech_to_text
from core.orchestration import get_conversation_flow
```

### 2. احراز هویت OTP

```python
# همیشه بررسی کنید کاربر از طریق OTP وارد شده
@require_otp_session
@require_role('patient')
def chat_message_view(request):
    pass
```

### 3. OpenAI Agents

```python
# استفاده از کتابخانه OpenAI Agents
from openai import Agent

medical_agent = Agent(
    name="medical_consultant",
    instructions=MEDICAL_PROMPT,
    tools=[symptom_checker, drug_info, doctor_finder]
)
```

### 4. تست‌نویسی

```python
# تست‌ها را بنویسید اما اجرا نکنید
class TestConversationService(TestCase):
    """تست‌های سرویس مکالمه"""
    
    def test_create_conversation(self):
        """تست ایجاد مکالمه جدید"""
        # کد تست را بنویسید
        # اما pytest را اجرا نکنید
```

## 🚀 مراحل اجرا

### مرحله 1: آماده‌سازی
1. [ ] مطالعه کامل PLAN.md
2. [ ] بررسی ARCHITECTURE_CONVENTIONS.md از پوشه والد
3. [ ] درک کامل نیازمندی‌ها

### مرحله 2: پیاده‌سازی
1. [ ] ایجاد ساختار پوشه‌ها
2. [ ] نوشتن مدل‌ها
3. [ ] پیاده‌سازی سرویس‌ها
4. [ ] ساخت OpenAI Agents
5. [ ] ایجاد API endpoints

### مرحله 3: یکپارچه‌سازی
1. [ ] اتصال به هسته‌های مرکزی
2. [ ] تنظیم احراز هویت
3. [ ] پیکربندی billing check

### مرحله 4: تکمیل
1. [ ] نوشتن تست‌ها (بدون اجرا)
2. [ ] تکمیل مستندات
3. [ ] ایجاد نمونه تنظیمات

## 📊 معیارهای موفقیت

- [ ] تمام آیتم‌های CHECKLIST.json تکمیل شده
- [ ] کد طبق استانداردهای HELSSA
- [ ] مستندات کامل و واضح
- [ ] تست‌ها نوشته شده (حداقل 80% coverage)
- [ ] آماده برای انتقال به helssa-big_back

## 🆘 در صورت مواجه با مشکل

1. مشکل را در LOG.md ثبت کنید
2. اگر نیاز به تصمیم معماری دارید، آن را مستند کنید
3. از الگوهای موجود در HELSSA-MAIN استفاده کنید
4. هرگز تصمیم سلیقه‌ای نگیرید

---

**یادآوری**: شما یک ایجنت اجرایی هستید. وظیفه شما اجرای دقیق این دستورالعمل است، نه تغییر یا بهبود آن.