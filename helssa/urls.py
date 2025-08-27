"""
پیکربندی URL های پروژه هلسا
Helssa Project URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # مدیریت Django
    path('admin/', admin.site.urls),
    
    # اپ احراز هویت OTP
    path('auth/', include('auth_otp.urls')),
    
    # اپ چت‌بات
    path('chatbot/', include('chatbot.urls')),
    
    # API Root
    path('api/v1/auth/', include('auth_otp.urls')),
    path('api/v1/chatbot/', include('chatbot.urls')),
]

# در حالت development فایل‌های media و static را سرو کن
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
