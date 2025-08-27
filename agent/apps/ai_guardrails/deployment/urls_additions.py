"""
URL additions for ai_guardrails
"""

from django.urls import path, include

urlpatterns += [
    path('api/ai_guardrails/', include('ai_guardrails.urls')),
]
