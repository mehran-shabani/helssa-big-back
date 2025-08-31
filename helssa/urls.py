"""
URL configuration for helssa project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/doctor/', include('doctor.urls')),
    path('api/auth/', include('auth_otp.urls')),
    path('api/triage/', include('triage.urls')),
    path('api/privacy/', include('privacy.urls')),
    path('api/patient/', include('patient.urls')),

]
