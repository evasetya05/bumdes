from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.extras.blog'
    label = 'blog'  # Explicitly set the app label
    verbose_name = 'Blog'
