from django.apps import AppConfig

class YourAppConfig(AppConfig):
    name = 'api'

    def ready(self):
        from .models import Product, Stock
        from django.db.utils import OperationalError
        try:
            for product in Product.objects.all():
                Stock.objects.get_or_create(product=product)
        except OperationalError:
            pass  # avoid errors during migrations
