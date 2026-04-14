from sentence_transformers import SentenceTransformer
import numpy as np

# Singleton — model loads once, reused across all calls (~80MB download on first run)
_model = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print("[VectorService] Loading all-MiniLM-L6-v2 model (first time only)...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        print("[VectorService] Model loaded.")
    return _model


def generate_embedding(text: str) -> list[float]:
    """
    Converts any text string into a 384-dimensional vector.
    Same model as production RAG_ARCHITECTURE_DOCUMENTATION.md.

    Returns a plain Python list of 384 floats — ready to store
    in Product.embedding (JSONField) or index into Elasticsearch.
    """
    model = _get_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def build_product_text(product) -> str:
    """
    Combines all meaningful product fields into one string for embedding.
    This is the text the model 'reads' to understand what the product is.
    Richer text = better semantic search results.
    """
    parts = [
        product.name,
        product.description,
        product.brand,
        product.category,
        product.color,
        product.material,
    ]
    return " ".join(p for p in parts if p)