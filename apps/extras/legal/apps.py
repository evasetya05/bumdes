from django.apps import AppConfig


class LegalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.extras.legal'
    label = 'legal'  # Explicitly set the app label
    verbose_name = 'Legal'

    def ready(self):
        from . import signals
