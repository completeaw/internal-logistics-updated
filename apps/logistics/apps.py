from django.apps import AppConfig

class LogisticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.logistics'
    
    def ready(self):
        import apps.logistics.signals  # Import signals when app is ready 