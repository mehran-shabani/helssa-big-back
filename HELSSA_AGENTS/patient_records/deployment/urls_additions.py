"""
{APP_NAME} URLs Additions
Part of HELSSA Platform

URL patterns to be added to the main Django project's URL configuration
"""

from django.urls import path, include

# Add these to your main urlpatterns
urlpatterns += [
    # {APP_NAME} API endpoints
    path('api/{app_name}/', include('{app_name}.urls')),
    
    # {APP_NAME} admin endpoints (if needed)
    path('admin/{app_name}/', include('{app_name}.admin_urls')),  # Optional
]

# API versioning (if needed)
urlpatterns += [
    path('api/v1/{app_name}/', include('{app_name}.urls')),
    path('api/v2/{app_name}/', include('{app_name}.v2.urls')),  # Future version
]

# WebSocket URLs (if needed for real-time features)
websocket_urlpatterns = [
    path('ws/{app_name}/', include('{app_name}.websocket_urls')),  # Optional
]