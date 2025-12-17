from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    label = 'core'  # Explicitly set the app label
    verbose_name = 'Core'

    def ready(self):
        from . import signals
