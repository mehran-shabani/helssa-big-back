"""
{APP_NAME} Settings Additions
Part of HELSSA Platform

Additional Django settings for {APP_DESCRIPTION}
These settings should be added to the main Django settings file.
"""

# Add app to INSTALLED_APPS
INSTALLED_APPS += [
    '{app_name}.apps.{AppName}Config',
]

# {APP_NAME} specific settings
{APP_NAME_UPPER}_CONFIG = {
    # Rate limiting configuration
    'RATE_LIMITS': {
        'api_calls_per_minute': 100,
        'ai_requests_per_minute': 20,
        'audio_uploads_per_hour': 50,
    },
    
    # Processing limits
    'PROCESSING_LIMITS': {
        'max_text_length': 5000,
        'max_audio_file_size': 50 * 1024 * 1024,  # 50MB
        'max_audio_duration': 1800,  # 30 minutes
        'max_concurrent_requests': 10,
    },
    
    # AI processing configuration
    'AI_CONFIG': {
        'default_model': 'gpt-4',
        'temperature': 0.7,
        'max_tokens': 2000,
        'timeout': 30,
    },
    
    # Caching configuration
    'CACHE_CONFIG': {
        'default_timeout': 3600,  # 1 hour
        'max_entries': 1000,
        'key_prefix': '{app_name}_',
    },
    
    # File upload configuration
    'UPLOAD_CONFIG': {
        'allowed_audio_formats': ['.wav', '.mp3', '.m4a', '.ogg', '.flac'],
        'max_file_size': 50 * 1024 * 1024,  # 50MB
        'upload_path': 'uploads/{app_name}/',
    },
    
    # Billing configuration
    'BILLING_CONFIG': {
        'cost_per_text_request': 10,  # credits
        'cost_per_audio_request': 50,  # credits
        'cost_per_ai_request': 20,    # credits
        'free_tier_limits': {
            'daily_requests': 10,
            'monthly_requests': 100,
        }
    }
}

# Logging configuration for {APP_NAME}
LOGGING['loggers']['{app_name}'] = {
    'handlers': ['file', 'console'],
    'level': 'INFO',
    'propagate': False,
}

# Add specific log file for {APP_NAME}
LOGGING['handlers']['{app_name}_file'] = {
    'level': 'INFO',
    'class': 'logging.handlers.RotatingFileHandler',
    'filename': os.path.join(BASE_DIR, 'logs', '{app_name}.log'),
    'maxBytes': 10 * 1024 * 1024,  # 10MB
    'backupCount': 5,
    'formatter': 'verbose',
}

# Security settings specific to {APP_NAME}
{APP_NAME_UPPER}_SECURITY = {
    'require_otp_for_sensitive_operations': True,
    'max_failed_attempts': 5,
    'lockout_duration': 300,  # 5 minutes
    'require_https': True,
    'session_timeout': 3600,  # 1 hour
}

# Performance monitoring
{APP_NAME_UPPER}_MONITORING = {
    'enable_performance_tracking': True,
    'slow_request_threshold': 2.0,  # seconds
    'memory_usage_threshold': 100 * 1024 * 1024,  # 100MB
    'enable_profiling': False,  # Enable in development only
}

# Integration settings
{APP_NAME_UPPER}_INTEGRATIONS = {
    'unified_auth': {
        'enabled': True,
        'user_types': ['patient', 'doctor'],
        'otp_required_operations': ['{PRIMARY_WORKFLOW}', '{SENSITIVE_OPERATION}'],
    },
    'unified_billing': {
        'enabled': True,
        'billing_model': 'pay_per_use',
        'currency': 'IRR',
    },
    'unified_ai': {
        'enabled': True,
        'preferred_provider': 'openai',
        'fallback_providers': ['azure', 'local'],
    },
    'kavenegar': {
        'enabled': True,
        'sender': '10008663',
        'template_ids': {
            'otp_verification': 'verify',
            'welcome_message': 'welcome',
        }
    }
}

# Database configuration
DATABASES['default']['OPTIONS'].update({
    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
    'charset': 'utf8mb4',
})

# Cache configuration for {APP_NAME}
CACHES['{app_name}'] = {
    'BACKEND': 'django_redis.cache.RedisCache',
    'LOCATION': 'redis://127.0.0.1:6379/2',
    'OPTIONS': {
        'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        'KEY_PREFIX': '{app_name}_',
    }
}

# Celery configuration for {APP_NAME}
CELERY_ROUTES.update({
    '{app_name}.tasks.*': {'queue': '{app_name}_queue'},
})

# Add {APP_NAME} specific queues
CELERY_TASK_ROUTES['{app_name}.tasks.process_audio'] = {'queue': 'audio_processing'}
CELERY_TASK_ROUTES['{app_name}.tasks.process_text'] = {'queue': 'text_processing'}

# API throttling for {APP_NAME}
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'].update({
    '{app_name}_api': '100/hour',
    '{app_name}_ai': '20/hour',
    '{app_name}_upload': '50/hour',
})

# File storage configuration
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = f'helssa-{app_name}-files'
AWS_S3_REGION_NAME = 'us-east-1'
AWS_S3_FILE_OVERWRITE = False
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

# Email configuration for {APP_NAME}
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
{APP_NAME_UPPER}_EMAIL_CONFIG = {
    'from_email': f'noreply@{app_name}.helssa.com',
    'support_email': f'support@{app_name}.helssa.com',
    'templates': {
        'welcome': 'emails/{app_name}/welcome.html',
        'notification': 'emails/{app_name}/notification.html',
    }
}

# Internationalization
LOCALE_PATHS += [
    os.path.join(BASE_DIR, '{app_name}', 'locale'),
]

# Static files configuration
STATICFILES_DIRS += [
    os.path.join(BASE_DIR, '{app_name}', 'static'),
]

# Template configuration
TEMPLATES[0]['DIRS'].append(
    os.path.join(BASE_DIR, '{app_name}', 'templates')
)

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Development settings
if DEBUG:
    {APP_NAME_UPPER}_CONFIG['AI_CONFIG']['timeout'] = 60
    {APP_NAME_UPPER}_MONITORING['enable_profiling'] = True
    LOGGING['loggers']['{app_name}']['level'] = 'DEBUG'

# Production settings
if not DEBUG:
    {APP_NAME_UPPER}_SECURITY['require_https'] = True
    {APP_NAME_UPPER}_CONFIG['PROCESSING_LIMITS']['max_concurrent_requests'] = 50
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True