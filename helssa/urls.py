"""
URL configuration for helssa project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    # path('api/auth/', include('auth_otp.urls')),  # موقتاً کامنت شده
    path('api/privacy/', include('privacy.urls')),
    path('api/patient/', include('patient.urls')),

]
