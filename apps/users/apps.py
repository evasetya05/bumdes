from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'  # Updated to use full Python path
    label = 'users'  # This will be used as the app_label

    def ready(self):
        import apps.users.signals  # noqa
