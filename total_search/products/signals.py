from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from products.models import Product
from products.services.indexer import index_product, delete_product


@receiver(post_save, sender=Product)
def sync_product_to_elasticsearch(sender, instance, **kwargs):
    """
    Fires automatically every time a Product is saved (created or updated).
    Mirrors the intention of the production pattern where upsertItem was called
    after any database write.
    """
    result = index_product(instance)
    if result["status"]:
        print(f"[Signal] Indexed product: {instance.variant_handle} → {result['result']}")
    else:
        print(f"[Signal] Index FAILED for: {instance.variant_handle} → {result['error']}")


@receiver(post_delete, sender=Product)
def remove_product_from_elasticsearch(sender, instance, **kwargs):
    """
    Fires automatically when a Product is deleted from Django.
    Keeps Elasticsearch in sync.
    """
    result = delete_product(instance.variant_handle)
    if result["status"]:
        print(f"[Signal] Deleted from ES: {instance.variant_handle}")
    else:
        print(f"[Signal] Delete FAILED for: {instance.variant_handle}")