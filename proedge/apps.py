from django.apps import AppConfig


class ProedgeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'proedge'

    def ready(self):
        import proedge.signals