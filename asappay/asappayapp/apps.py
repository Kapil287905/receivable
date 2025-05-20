from django.apps import AppConfig


class AsappayappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'asappayapp'

    def ready(self):
        print(f"{self.name} is initialized")