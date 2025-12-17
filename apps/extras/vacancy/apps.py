from django.apps import AppConfig


class VacancyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.extras.vacancy'
    label = 'vacancy'  # Explicitly set the app label
    verbose_name = 'Vacancy'
