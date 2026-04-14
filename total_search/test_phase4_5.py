import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "total_search.settings")
django.setup()

from products.services.vector_service import generate_embedding
from products.services.hybrid_engine import hybrid_search

print("=" * 55)
print("PHASE 4 — Embedding sanity check")
print("=" * 55)
emb = generate_embedding("white bathroom tiles")
print(f"Embedding dimensions : {len(emb)}")
print(f"First 5 values       : {[round(v, 4) for v in emb[:5]]}")
print(f"Value range          : {round(min(emb), 4)} to {round(max(emb), 4)}")


print("\n" + "=" * 55)
print("PHASE 5 — Hybrid search: 'luxury flooring'")
print("KEY TEST: finds 'Premium Marble Tile' even though")
print("the word 'luxury' is not in any product name")
print("=" * 55)
results = hybrid_search("luxury flooring", top_n=5)
for i, p in enumerate(results, 1):
    print(f"  {i}. {p['name']}")
    print(f"     Brand: {p['brand']} | Category: {p['category']}")
    print(f"     Similarity: {p['_similarity_score']}")


print("\n" + "=" * 55)
print("PHASE 5 — Hybrid search: 'elegant white wall tiles'")
print("=" * 55)
results2 = hybrid_search("elegant white wall tiles", top_n=5)
for i, p in enumerate(results2, 1):
    print(f"  {i}. {p['name']} — score: {p['_similarity_score']}")


print("\n" + "=" * 55)
print("PHASE 5 — Hybrid search with hard filter: category=Tiles")
print("Query: 'rustic natural material'")
print("=" * 55)
results3 = hybrid_search(
    "rustic natural material",
    filters={"category": "Tiles"},
    top_n=5,
)
for i, p in enumerate(results3, 1):
    print(f"  {i}. {p['name']} | {p['material']} — score: {p['_similarity_score']}")


print("\n" + "=" * 55)
print("PHASE 5 — Hybrid search: 'eco friendly sustainable floor'")
print("Should surface: Bamboo + Cork products")
print("=" * 55)
results4 = hybrid_search("eco friendly sustainable floor", top_n=3)
for i, p in enumerate(results4, 1):
    print(f"  {i}. {p['name']} | {p['material']} — score: {p['_similarity_score']}")