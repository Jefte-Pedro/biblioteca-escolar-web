from django.apps import AppConfig


class BibliotecaConfig(AppConfig):
    name = 'biblioteca'

    def ready(self):
        from .scheduler import iniciar_scheduler
        iniciar_scheduler()