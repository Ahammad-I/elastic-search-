from django.core.management.base import BaseCommand
from products.models import Product
from products.services.visual_search import generate_text_image_embedding
from products.services.visual_search import generate_image_embedding

import requests   # ✅ ADD THIS LINE

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        products = Product.objects.filter(is_active=True)
        sucess=0
        for product in products:
           if product.visual_embedding:
                print(f"product has {product.visual_embedding}")