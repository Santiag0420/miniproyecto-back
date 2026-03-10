from django.apps import AppConfig


class UsersConfig(AppConfig):
    # Ruta completa del módulo necesaria porque la app vive dentro de apps/.
    name = 'backend.apps.users'

    def ready(self):
        import backend.apps.users.signals  # noqa: F401 — registra el signal post_save
