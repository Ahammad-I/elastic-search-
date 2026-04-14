from products.infrastructure.elastic_client import elastic
from products.services.vector_service import generate_embedding, build_product_text

INDEX_NAME = "products"


def product_to_dict(product) -> dict:
    """
    Converts a Django Product instance into a flat dictionary
    suitable for Elasticsearch indexing.
    Mirrors the logic from the original opensearch_client.py upsertItem,
    but cleanly — no raw HTTP, no hardcoded credentials.
    """
    return {
        "variant_handle": product.variant_handle,
        "name":           product.name,
        "description":    product.description,
        "brand":          product.brand,
        "category":       product.category,
        "price":          float(product.price),
        "color":          product.color,
        "material":       product.material,
        "is_active":      product.is_active,
        "image_url":      product.image_url,
      
    }


def index_product(product) -> dict:
    """
    Indexes (creates or updates) a single Product in Elasticsearch.
    Uses variant_handle as the document ID — same pattern as
    the production bulkUpsertItemsNewElastic which used variant_id.
    Returns a status dict.
    """
    es = elastic.get_client()
    try:
        text = build_product_text(product)
        embedding = generate_embedding(text)

        # Save embedding back to Django DB (update_fields avoids re-triggering signals)
        product.embedding = embedding
        Product.objects.filter(id=product.id).update(embedding=embedding)
        doc = product_to_dict(product)
        response = es.index(
            index=INDEX_NAME,
            id=str(product.variant_handle),
            body=doc,
        )

        return {"status": True, "result": response["result"]}
    except Exception as e:
        print(f"[Indexer] Failed to index product {product.variant_handle}: {e} ")
        return {"status": False, "error": str(e)}


def delete_product(variant_handle: str) -> dict:
    """
    Removes a product document from Elasticsearch by its variant_handle.
    """
    es = elastic.get_client()
    try:
        response = es.delete(index=INDEX_NAME, id=str(variant_handle))
        return {"status": True, "result": response["result"]}
    except Exception as e:
        print(f"[Indexer] Failed to delete {variant_handle}: {e}")
        return {"status": False, "error": str(e)}