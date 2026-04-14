import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from products.models import Product
from products.services.keyword_search import keyword_search
from products.services.vector_service import generate_embedding


def hybrid_search(
    query_text: str,
    filters: dict = None,
    top_n: int = 5,
    candidate_pool: int = 50,
) -> list[dict]:
    """
    Hybrid search engine combining keyword matching with semantic re-ranking.

    Based on the RAG_ARCHITECTURE_DOCUMENTATION.md System Flow:
      Step 1 — keyword_search() fetches top candidates (fast, filtered)
      Step 2 — generate_embedding() encodes the user query into 384 floats
      Step 3 — cosine_similarity() re-ranks candidates by semantic closeness
      Step 4 — return top_n results sorted by similarity score

    This is effective because:
      - Keyword search handles filters and typos efficiently via Elasticsearch
      - Cosine re-ranking promotes semantically relevant results even when
        the exact words don't appear in the product name
        e.g. "luxury flooring" finds "Premium Marble Tile" correctly

    Args:
        query_text:     The user's natural language query
        filters:        Optional dict of hard filters (category, brand, color, material)
        top_n:          Number of final results to return (default 5)
        candidate_pool: How many keyword results to pull before re-ranking (default 50)

    Returns:
        List of product dicts sorted by cosine similarity score (highest first),
        each containing all product fields plus '_similarity_score'.
    """

    # --- Step 1: Keyword search to get candidate pool ---
    # We fetch up to `candidate_pool` results from ES.
    # These are pre-filtered (category, brand, price) and keyword-matched.
    keyword_results = keyword_search(
        query_text=query_text,
        filters=filters,
        page=0,
        page_size=candidate_pool,
    )

    candidates = keyword_results.get("products", [])

    if not candidates:
        print("[HybridEngine] No keyword candidates found.")
        return []

    # --- Step 2: Generate query embedding ---
    query_embedding = generate_embedding(query_text)
    query_vec = np.array(query_embedding).reshape(1, -1)

    # --- Step 3: Compute cosine similarity for each candidate ---
    scored = []
    for product in candidates:
        variant = product.get("variant_handle")

        # Fetch the product from the database to get its embedding
        try:
            db_product = Product.objects.get(variant_handle=variant)
            stored_embedding = db_product.embedding
        except Product.DoesNotExist:
            print(f"[HybridEngine] Product not found for variant {variant}.")
            continue

        # Skip products that have no embedding yet
        if not stored_embedding or len(stored_embedding) == 0:
            print(f"[HybridEngine] Skipping {product.get('name')} — no embedding stored.")
            continue

        product_vec = np.array(stored_embedding).reshape(1, -1)
        similarity  = cosine_similarity(query_vec, product_vec)[0][0]

        product["_similarity_score"] = round(float(similarity), 4)
        scored.append(product)

    if not scored:
        print("[HybridEngine] No products with embeddings found in candidates.")
        return []

    # --- Step 4: Sort by similarity and return top_n ---
    scored.sort(key=lambda p: p["_similarity_score"], reverse=True)
    return scored[:top_n]