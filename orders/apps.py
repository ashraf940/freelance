from django.apps import AppConfig

class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'

    def ready(self):
        """
        Register signals for orders app
        This will be called when Django starts
        """
        import orders.signals