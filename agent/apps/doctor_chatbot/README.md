# 👨‍⚕️ Doctor Chatbot - دستورالعمل اجرایی

## 📋 خلاصه

این دستورالعمل برای ایجنتی است که مسئول ساخت چت‌بات پزشک HELSSA است. این سیستم یک دستیار بالینی هوشمند برای پزشکان است.

## 🎯 مأموریت شما

شما باید:
1. `PLAN.md` را به دقت مطالعه کنید
2. طبق `CHECKLIST.json` پیش بروید
3. هر تغییر را در `LOG.md` ثبت کنید
4. پیشرفت را در `PROGRESS.json` به‌روزرسانی کنید
5. **الزامات HIPAA و پزشکی را رعایت کنید**

## 📁 فایل‌های راهنما

- **PLAN.md**: طرح کامل توسعه با جزئیات فنی و بالینی
- **CHECKLIST.json**: لیست دقیق کارها با اولویت‌بندی
- **PROGRESS.json**: وضعیت پیشرفت (شامل متریک‌های بالینی)
- **LOG.md**: ثبت تصمیمات و تغییرات
- **charts/**: نمودارهای پیشرفت

## 🏗️ ساختار خروجی مورد انتظار

```
agent/doctor_chatbot/
├── src/                    # کد منبع اپ
│   ├── models/
│   ├── services/
│   ├── api/
│   ├── agents/            # OpenAI Agents برای تشخیص و درمان
│   ├── integrations/      # اتصال به Drug DB, Guidelines
│   ├── utils/
│   └── tests/
├── docs/                   # مستندات تکمیلی
│   ├── API.md
│   ├── CLINICAL_GUIDE.md
│   ├── HIPAA_COMPLIANCE.md
│   └── DEPLOYMENT.md
├── configs/                # تنظیمات نمونه
│   ├── settings_snippet.py
│   ├── urls_snippet.py
│   └── clinical_settings.py
├── templates/              # قالب‌های SOAP و گزارش
│   ├── soap_template.html
│   └── prescription_template.html
└── requirements.txt        # وابستگی‌های اپ
```

## ⚠️ نکات حیاتی پزشکی

### 1. دقت بالینی

```python
# همیشه disclaimer پزشکی اضافه کنید
MEDICAL_DISCLAIMER = """
این سیستم صرفاً جهت کمک به تصمیم‌گیری پزشک طراحی شده است.
تصمیمات نهایی باید توسط پزشک مجاز اتخاذ شود.
"""

# هر پیشنهاد باید confidence level داشته باشد
diagnosis_suggestion = {
    "condition": "Hypertension",
    "icd10": "I10",
    "confidence": 0.85,
    "evidence": ["BP: 150/95", "Family history"],
    "requires_confirmation": True
}
```

### 2. احراز هویت پزشک

```python
# بررسی مجوز پزشکی الزامی است
@require_medical_license
@require_role('doctor')
def clinical_session_view(request):
    # Medical license باید verify شده باشد
    if not request.user.doctor_profile.license_verified:
        raise PermissionDenied("Medical license not verified")
```

### 3. HIPAA Compliance

```python
# رمزنگاری داده‌های بیمار
from encryption import medical_encrypt, medical_decrypt

# هیچ PHI در لاگ‌ها
import logging
logging.getLogger().addFilter(PHIFilter())

# Audit trail برای همه دسترسی‌ها
@audit_medical_access
def access_patient_data(patient_id):
    pass
```

### 4. Drug Safety

```python
# بررسی اجباری تداخلات دارویی
class PrescriptionService:
    def check_interactions(self, medications):
        interactions = self.drug_db.check_interactions(medications)
        if interactions.severity == 'CRITICAL':
            return {
                'allowed': False,
                'warnings': interactions.warnings,
                'alternatives': interactions.alternatives
            }
```

### 5. OpenAI Agents پزشکی

```python
# Agent تشخیص با دقت بالا
diagnosis_agent = Agent(
    name="clinical_diagnosis_assistant",
    instructions="""You are an experienced physician assistant.
    Always:
    - Provide evidence-based suggestions
    - Include differential diagnoses
    - Cite medical guidelines
    - Never make definitive diagnoses
    - Include confidence levels
    """,
    tools=[icd10_search, symptom_checker, lab_interpreter]
)
```

## 🚀 مراحل اجرا

### مرحله 1: آماده‌سازی
1. [ ] مطالعه کامل PLAN.md
2. [ ] مرور الزامات HIPAA
3. [ ] درک clinical workflows

### مرحله 2: پیاده‌سازی پایه
1. [ ] مدل‌های بالینی
2. [ ] سرویس‌های اصلی
3. [ ] Clinical Agents

### مرحله 3: ایمنی و Compliance
1. [ ] HIPAA implementation
2. [ ] Drug safety checks
3. [ ] Audit system

### مرحله 4: یکپارچه‌سازی‌ها
1. [ ] Drug database
2. [ ] Clinical guidelines
3. [ ] EHR systems

### مرحله 5: تکمیل
1. [ ] Clinical validation tests
2. [ ] مستندات کامل
3. [ ] Deployment guide

## 📊 معیارهای موفقیت

- [ ] Diagnosis accuracy > 90%
- [ ] Drug interaction detection: 100%
- [ ] HIPAA compliance: Full
- [ ] Response time < 5s for SOAP
- [ ] Test coverage > 85%
- [ ] Clinical validation passed

## 🏥 Clinical Guidelines

### تشخیص
- همیشه differential diagnosis ارائه دهید
- Evidence-based medicine رعایت شود
- Confidence levels مشخص باشد

### تجویز دارو
- Contraindications چک شود
- Drug-drug interactions بررسی شود
- Dosage بر اساس وزن/سن/CrCl

### مستندسازی
- SOAP format استاندارد
- ICD-10/CPT codes دقیق
- Timestamp همه entries

## 🆘 در صورت مواجه با مشکل

1. مشکل را در LOG.md ثبت کنید
2. برای موارد بالینی، نیاز به "Clinical Review" را مشخص کنید
3. HIPAA violations فوراً گزارش شوند
4. Drug safety issues اولویت critical دارند

---

**هشدار قانونی**: این سیستم جایگزین قضاوت بالینی پزشک نیست. همه تصمیمات نهایی باید توسط پزشک مجاز اتخاذ شوند.