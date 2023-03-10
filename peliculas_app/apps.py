from django.apps import AppConfig


class PeliculasAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "peliculas_app"

    def ready(self):
        import peliculas_app.custom_filters
