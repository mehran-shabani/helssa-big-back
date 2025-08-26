# 🤖 دستورالعمل‌های جامع برای ایجنت‌های هلسا

## 📋 نمای کلی

این سند دستورالعمل‌های کامل برای ایجنت‌هایی است که اپلیکیشن‌های مختلف پلتفرم هلسا را بر اساس معماری چهار هسته‌ای می‌سازند.

## 🎯 هدف سیستم

سیستم ایجنت‌های هلسا برای ایجاد خودکار اپلیکیشن‌های کامل طراحی شده است. هر ایجنت:

- ✅ **یک اپلیکیشن کامل** ایجاد می‌کند
- ✅ **تمام فایل‌های مورد نیاز** را می‌سازد
- ✅ **تست‌های جامع** می‌نویسد
- ✅ **مستندات کامل** تولید می‌کند
- ✅ **یکپارچه‌سازی** با سرویس‌های موجود انجام می‌دهد
- ✅ **قوانین امنیتی** را رعایت می‌کند

## 🚀 شروع کار

### 1. راه‌اندازی ایجنت جدید

```bash
# ایجاد ایجنت جدید
cd agents-system/WORKFLOW_ENGINE
python create_agent.py --app_name "patient_chatbot" --description "چت‌بات هوشمند بیماران"

# یا با استفاده از فایل پیکربندی
python create_agent.py --config agent_config.json
```

### 2. اجرای ایجنت

```bash
# اجرای کامل
python run_agent.py --app_name "patient_chatbot" --mode "full"

# اجرای مرحله به مرحله
python run_agent.py --app_name "patient_chatbot" --mode "step_by_step"
```

## 🏗️ معماری چهار هسته‌ای

### هسته 1: API Ingress Core
**مسئولیت**: مدیریت HTTP requests و responses
**ویژگی‌ها**:
- اعتبارسنجی ورودی‌ها
- احراز هویت و authorization
- Rate limiting و throttling
- CORS و security headers
- API versioning
- Request/Response logging

### هسته 2: Text Processing Core
**مسئولیت**: پردازش زبان طبیعی و تولید متن
**ویژگی‌ها**:
- NLP processing
- Text generation
- Conversation summarization
- Entity extraction
- Sentiment analysis

### هسته 3: Speech Processing Core
**مسئولیت**: پردازش صوت و تبدیل گفتار به متن
**ویژگی‌ها**:
- Speech-to-Text (STT)
- Text-to-Speech (TTS)
- Audio analysis
- Voice recognition

### هسته 4: Orchestration Core
**مسئولیت**: هماهنگی بین هسته‌ها و مدیریت فرآیندها
**ویژگی‌ها**:
- Workflow management
- Service coordination
- Error handling
- Performance monitoring

## 📱 اپلیکیشن‌های هدف

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

## 🔄 فرآیند توسعه

### مرحله 1: آماده‌سازی
1. **خواندن مستندات**: مطالعه کامل CORE_ARCHITECTURE.md
2. **بررسی امنیت**: مطالعه SECURITY_POLICIES.md
3. **تعیین وابستگی‌ها**: شناسایی سرویس‌های مورد نیاز
4. **ایجاد پوشه**: ساختار پوشه‌های اپلیکیشن

### مرحله 2: طراحی
1. **تکمیل PLAN.md**: برنامه‌ریزی تفصیلی
2. **تعریف API**: تعیین endpoints و ساختار
3. **طراحی مدل‌ها**: طراحی مدل‌های داده
4. **تعیین dependencies**: لیست وابستگی‌ها

### مرحله 3: پیاده‌سازی
1. **ایجاد Django app**: ساختار اصلی اپلیکیشن
2. **نوشتن models**: مدل‌های داده و migrations
3. **پیاده‌سازی هسته‌ها**: چهار هسته اصلی
4. **ایجاد views**: API views و serializers
5. **پیکربندی URLs**: مسیریابی اپلیکیشن

### مرحله 4: یکپارچه‌سازی
1. **unified_auth**: احراز هویت یکپارچه
2. **unified_billing**: سیستم مالی یکپارچه
3. **unified_ai**: هوش مصنوعی مرکزی
4. **unified_access**: کنترل دسترسی یکپارچه

### مرحله 5: تست و مستندسازی
1. **نوشتن تست‌ها**: Unit, Integration, E2E
2. **تکمیل مستندات**: API, User Guide, Technical
3. **به‌روزرسانی پیشرفت**: ثبت در PROGRESS.json
4. **ثبت در لاگ**: ثبت تصمیم‌ها در LOG.md

## 📁 ساختار استاندارد اپلیکیشن

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
├── 📁 migrations/              # Database migrations
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
├── 📁 templates/               # HTML templates
├── 📁 static/                  # Static files
├── 📄 requirements.txt          # Dependencies
├── 📄 PLAN.md                  # Development plan
├── 📄 CHECKLIST.json           # Task checklist
├── 📄 PROGRESS.json            # Progress tracking
├── 📄 LOG.md                   # Decision log
└── 📄 README.md                # Application overview
```

## 🔌 API Endpoints استاندارد

### ساختار کلی
```
/api/v1/{app_name}/
├── /                           # نمای کلی اپلیکیشن
├── /models/                    # CRUD operations
├── /actions/                   # Custom actions
├── /reports/                   # گزارش‌گیری
└── /integrations/              # یکپارچه‌سازی
```

### مثال برای patient_chatbot
```
/api/v1/patient_chatbot/
├── /                           # نمای کلی
├── /chat/                      # مدیریت چت
├── /questions/                 # سوالات پزشکی
└── /appointments/              # رزرو نوبت
```

## 🧪 تست‌ها

### انواع تست‌های مورد نیاز
1. **Unit Tests**: تست توابع و کلاس‌های جداگانه
2. **Integration Tests**: تست تعامل بین کامپوننت‌ها
3. **API Tests**: تست endpoints و responses
4. **Security Tests**: تست امنیت و دسترسی

### پوشش تست
- **Models**: 100%
- **Views**: 100%
- **Services**: 100%
- **Serializers**: 100%

### ساختار تست‌ها
```python
# test_models.py
class AppNameModelTests(TestCase):
    def setUp(self):
        # تنظیمات اولیه
        pass
    
    def test_model_creation(self):
        # تست ایجاد مدل
        pass
    
    def test_model_validation(self):
        # تست اعتبارسنجی
        pass

# test_views.py
class AppNameViewTests(TestCase):
    def setUp(self):
        # تنظیمات اولیه
        pass
    
    def test_api_endpoints(self):
        # تست API endpoints
        pass

# test_services.py
class AppNameServiceTests(TestCase):
    def setUp(self):
        # تنظیمات اولیه
        pass
    
    def test_business_logic(self):
        # تست منطق کسب و کار
        pass
```

## 📚 مستندات

### فایل‌های مستندات مورد نیاز
1. **README.md**: نمای کلی اپلیکیشن
2. **API.md**: مستندات کامل API
3. **USER_GUIDE.md**: راهنمای کاربر
4. **TECHNICAL.md**: مستندات فنی

### محتوای هر فایل
- **README.md**: توضیحات، ویژگی‌ها، نصب، استفاده
- **API.md**: تمام endpoints، پارامترها، پاسخ‌ها
- **USER_GUIDE.md**: نحوه استفاده، مثال‌ها، عیب‌یابی
- **TECHNICAL.md**: معماری، تکنولوژی‌ها، استقرار

### زبان مستندات
- **فارسی**: برای کاربران فارسی‌زبان
- **انگلیسی**: برای توسعه‌دهندگان بین‌المللی

## 🔒 امنیت و انطباق

### قوانین امنیتی
1. **احراز هویت**: تمام endpoints باید احراز هویت شوند
2. **دسترسی**: کنترل دسترسی بر اساس نقش کاربر
3. **اعتبارسنجی**: تمام ورودی‌ها باید اعتبارسنجی شوند
4. **لاگ**: ثبت تمام عملیات برای audit
5. **رمزگذاری**: رمزگذاری داده‌های حساس

### استانداردهای انطباق
- **HIPAA**: برای داده‌های پزشکی
- **GDPR**: برای حریم خصوصی
- **ISO 27001**: برای امنیت اطلاعات
- **WCAG**: برای دسترسی‌پذیری

## 🔗 یکپارچه‌سازی

### سرویس‌های یکپارچه
1. **unified_auth**: احراز هویت و دسترسی
2. **unified_billing**: صورتحساب و پرداخت
3. **unified_ai**: هوش مصنوعی مرکزی
4. **unified_access**: کنترل دسترسی

### نحوه یکپارچه‌سازی
```python
# Import سرویس‌های یکپارچه
from unified_auth.permissions import HasRole
from unified_billing.models import Billing
from unified_ai.services import UnifiedAIService

# استفاده در views
class AppViewSet(viewsets.ModelViewSet):
    permission_classes = [HasRole]
    
    def perform_create(self, serializer):
        # ایجاد صورتحساب
        billing = Billing.objects.create(...)
        serializer.save(billing=billing)
```

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

## 🚨 نکات مهم

### قوانین کلی
1. **هر ایجنت فقط یک اپلیکیشن ایجاد می‌کند**
2. **تمام قوانین امنیتی باید رعایت شوند**
3. **تست‌ها باید کامل و قابل اجرا باشند**
4. **مستندات باید به زبان فارسی و انگلیسی باشند**
5. **کد باید استانداردهای Django را رعایت کند**

### محدودیت‌ها
- **پیشنهاد نده**: فقط آنچه درخواست شده را انجام دهید
- **غیره**: از ایجاد اپلیکیشن‌های اضافی خودداری کنید
- **تست نکن**: تست‌ها را بنویسید اما اجرا نکنید
- **فرم پر نکن**: فرم‌ها را ایجاد کنید اما پر نکنید

### کیفیت کد
- **PEP 8**: رعایت استانداردهای Python
- **Django Best Practices**: رعایت بهترین شیوه‌های Django
- **Error Handling**: مدیریت مناسب خطاها
- **Logging**: ثبت مناسب لاگ‌ها

## 📞 پشتیبانی

### منابع کمک
1. **مستندات معماری**: CORE_ARCHITECTURE.md
2. **مستندات هلسا**: HELSSA_DOCS/
3. **قالب‌ها**: AGENT_TEMPLATES/
4. **پیکربندی**: agent_config.json

### سوالات متداول
- **Q**: چگونه می‌توانم اپلیکیشن جدید ایجاد کنم؟
- **A**: از `create_agent.py` استفاده کنید

- **Q**: چگونه ایجنت را اجرا کنم؟
- **A**: از `run_agent.py` استفاده کنید

- **Q**: کدام هسته‌ها را باید پیاده‌سازی کنم؟
- **A**: بر اساس نوع اپلیکیشن و agent_config.json

## 🎯 معیارهای موفقیت

### موفقیت اپلیکیشن
- ✅ تمام فایل‌های مورد نیاز ایجاد شده
- ✅ تست‌ها با پوشش حداقل 80% نوشته شده
- ✅ مستندات کامل و به دو زبان
- ✅ یکپارچه‌سازی با سرویس‌های موجود
- ✅ رعایت تمام قوانین امنیتی
- ✅ آماده برای استقرار

### موفقیت ایجنت
- ✅ اپلیکیشن کامل و قابل استفاده
- ✅ کد تمیز و استاندارد
- ✅ تست‌های جامع
- ✅ مستندات کامل
- ✅ یکپارچه‌سازی موفق
- ✅ آماده برای تولید

---

## 📝 خلاصه

سیستم ایجنت‌های هلسا ابزاری قدرتمند برای ایجاد خودکار اپلیکیشن‌های کامل است. هر ایجنت با پیروی از این دستورالعمل‌ها می‌تواند اپلیکیشن‌های با کیفیت بالا، امن و قابل نگهداری ایجاد کند.

**یادآوری**: هدف اصلی ایجاد اپلیکیشن‌های کامل و آماده برای استفاده است. کیفیت و کامل بودن مهم‌تر از سرعت است.