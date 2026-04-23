from django.apps import AppConfig


class TherapyPlansConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'therapy_plans'
    verbose_name = 'Therapy Plans'

    def ready(self):
        """Import signals when app is ready"""
        import therapy_plans.signals
