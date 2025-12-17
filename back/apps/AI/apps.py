from django.apps import AppConfig


class AiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.AI'
    def ready(self):
        import apps.AI.signals.signal_case_free