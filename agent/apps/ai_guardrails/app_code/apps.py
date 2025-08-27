"""
Ai Guardrails Application
"""

from django.apps import AppConfig


class AiGuardrailsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_guardrails'
    verbose_name = 'Ai Guardrails'
    
    def ready(self):
        """آماده‌سازی اپلیکیشن"""
        pass
