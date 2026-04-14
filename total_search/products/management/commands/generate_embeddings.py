from django.core.management.base import BaseCommand
from products.models import Product
from products.services.indexer import index_product


class Command(BaseCommand):
    help = "Generates embeddings for all products and re-indexes them into Elasticsearch"

    def add_arguments(self, parser):
        parser.add_argument(
            "--stats",
            action="store_true",
            help="Show embedding coverage stats only, do not generate",
        )

    def handle(self, *args, **kwargs):
        if kwargs["stats"]:
            total   = Product.objects.count()
            with_emb = Product.objects.exclude(embedding=None).count()
            without  = total - with_emb
            self.stdout.write(f"Total products   : {total}")
            self.stdout.write(f"With embeddings  : {with_emb}")
            self.stdout.write(self.style.WARNING(f"Missing embeddings: {without}"))
            return

        products = Product.objects.filter(is_active=True)
        total = products.count()
        self.stdout.write(f"Generating embeddings for {total} products...\n")

        success = 0
        failed  = 0

        for i, product in enumerate(products, 1):
            result = index_product(product)
            if result["status"]:
                success += 1
                self.stdout.write(f"  [{i}/{total}] OK  — {product.name}")
            else:
                failed += 1
                self.stdout.write(
                    self.style.ERROR(f"  [{i}/{total}] FAIL — {product.name}: {result['error']}")
                )

        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS(f"Done. Success: {success}, Failed: {failed}"))