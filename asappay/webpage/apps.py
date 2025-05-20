from django.apps import AppConfig


class WebpageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'webpage'

    def ready(self):
        print(f"{self.name} is initialized")
