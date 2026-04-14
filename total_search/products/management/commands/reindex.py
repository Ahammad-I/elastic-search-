from django.core.management.base import BaseCommand
from products.models import Product
from products.services.indexer import index_product


class Command(BaseCommand):
    help = "Re-index all products into Elasticsearch"

    def handle(self, *args, **kwargs):
        count = 0

        for product in Product.objects.all():
            result = index_product(product)

            if result["status"]:
                count += 1
                self.stdout.write(f"Indexed: {product.name}")
            else:
                self.stdout.write(f"FAILED: {product.name}")

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. Indexed {count} products."
        ))