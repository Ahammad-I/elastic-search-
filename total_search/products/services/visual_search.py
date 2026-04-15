import numpy as np
from PIL import Image
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import io

from products.models import Product

# Singleton CLIP model — loads once (~350MB download on first run)
# CLIP understands BOTH images and text in the same 512-dim vector space.
# This means product text embeddings and image embeddings are directly comparable.
_clip_model = None


def _get_clip_model() -> SentenceTransformer:
    global _clip_model
    if _clip_model is None:
        print("[VisualSearch] Loading CLIP model clip-ViT-B-32 (first time only)...")
        _clip_model = SentenceTransformer("clip-ViT-B-32")
        print("[VisualSearch] CLIP model loaded.")
    return _clip_model


def generate_image_embedding(image_bytes: bytes) -> list[float]:
    """
    Converts raw image bytes into a 512-dimensional CLIP vector.
    Mirrors the production EmbeddingPredictionClient.get_embedding()
    but uses local CLIP instead of Google Vertex AI multimodalembedding@001.

    The key difference: production used 1408-dim Vertex embeddings,
    we use 512-dim CLIP — still highly effective for similarity matching.
    """
    model = _get_clip_model()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    embedding = model.encode(image, convert_to_numpy=True)
    return embedding.tolist()


def generate_text_image_embedding(text: str) -> list[float]:
    """
    Encodes a text description into the CLIP vector space.
    Used to build visual embeddings for products from their text descriptions
    since our sample products don't have real downloadable images.
    CLIP maps both images and text into the same space — so this works.
    """
    model = _get_clip_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def get_visual_results(image_bytes: bytes, top_n: int = 5) -> list[dict]:
    """
    Core visual search function.
    Mirrors the production SearchImage.get_results() logic:
      1. Generate query vector from uploaded image
      2. Compare against stored product visual embeddings
      3. Return top matches sorted by similarity

    Production used Vertex AI index_endpoint.find_neighbors() for ANN search.
    We use cosine_similarity() directly — identical results at our data scale.

    Args:
        image_bytes: Raw bytes of the uploaded image
        top_n:       Number of similar products to return

    Returns:
        List of dicts with product info and similarity score
    """
    # Step 1: Embed the uploaded image
    query_embedding = generate_image_embedding(image_bytes)
    query_vec = np.array(query_embedding).reshape(1, -1)

    # Step 2: Load all products that have a visual_embedding stored
    products = Product.objects.filter(
        is_active=True
    ).exclude(visual_embedding=None)

    if not products.exists():
        print("[VisualSearch] No products with visual embeddings found.")
        print("  Run: python manage.py generate_visual_embeddings")
        return []

    # Step 3: Compute cosine similarity against every product's visual embedding
    scored = []
    for product in products:
        stored = product.visual_embedding
        if not stored or len(stored) == 0:
            continue

        product_vec = np.array(stored).reshape(1, -1)
        similarity  = cosine_similarity(query_vec, product_vec)[0][0]

        scored.append({
            "variant_handle":    product.variant_handle,
            "name":              product.name,
            "brand":             product.brand,
            "category":          product.category,
            "color":             product.color,
            "material":          product.material,
            "price":             float(product.price),
            "image_url":         product.image_url,
            "_visual_similarity": round(float(similarity), 4),
        })

    # Step 4: Sort by similarity and return top_n
    scored.sort(key=lambda p: p["_visual_similarity"], reverse=True)
    return scored[:top_n]