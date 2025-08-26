"""
{APP_NAME} URLs
Part of HELSSA Platform

URL configuration for {APP_DESCRIPTION}
"""

from django.urls import path
from . import views

app_name = '{app_name}'

urlpatterns = [
    # Primary endpoints
    path('process/', views.primary_endpoint, name='primary_endpoint'),
    path('text/', views.text_processing_endpoint, name='text_processing'),
    path('audio/', views.audio_processing_endpoint, name='audio_processing'),
    
    # Data management
    path('history/', views.get_history, name='get_history'),
    path('record/<str:record_id>/', views.get_record_detail, name='get_record_detail'),
    path('create/', views.create_record, name='create_record'),
    
    # Workflow management
    path('workflow/<str:workflow_id>/status/', views.get_workflow_status, name='get_workflow_status'),
    
    # Analytics (Doctor only)
    path('analytics/', views.get_analytics, name='get_analytics'),
    
    # Health check
    path('health/', views.health_check, name='health_check'),
]