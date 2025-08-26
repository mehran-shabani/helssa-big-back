from django.apps import AppConfig


class {AppName}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '{app_name}'
    verbose_name = '{APP_VERBOSE_NAME}'
    
    def ready(self):
        """
        Application initialization
        """
        # Import signal handlers if any
        pass