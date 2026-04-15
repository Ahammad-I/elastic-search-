from django.db import models

from django.db import models

class Product(models.Model):
    # Text Fields
    name        = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    brand       = models.CharField(max_length=100, blank=True)
    category    = models.CharField(max_length=100, blank=True)

    # Filter Fields
    price    = models.DecimalField(max_digits=10, decimal_places=2)
    color    = models.CharField(max_length=50, blank=True)
    material = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    # AI Field — stores 384 floats from sentence-transformers
    embedding = models.JSONField(null=True, blank=True)

    # Visual Fields
    image_url= models.ImageField(upload_to="products/", blank=True, null=True)
    variant_handle = models.CharField(max_length=255, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    visual_embedding = models.JSONField(null=True, blank=True)
    image_url = models.URLField(blank=True, default="")
    def __str__(self):
        return self.name
