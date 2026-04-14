import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "total_search.settings")
django.setup()

from products.services.keyword_search import keyword_search

print("\n" + "="*50)
print("TEST 1 — Search 'blue' (no filters)")
print("="*50)
result = keyword_search(query_text="blue")
print(f"Total results: {result['total']}")
for p in result["products"]:
    print(f"  - {p['name']} | {p['brand']} | Rs.{p['price']}")

print("\nAggregations (sidebar filters):")
print("  Brands:")
for b in result["aggregations"]["brands"]:
    print(f"    {b['key']}: {b['count']} products")
print("  Categories:")
for c in result["aggregations"]["categories"]:
    print(f"    {c['key']}: {c['count']} products")

print("\n" + "="*50)
print("TEST 2 — Search 'marble' + category filter 'Tiles'")
print("="*50)
result2 = keyword_search(query_text="marble", filters={"category": "Tiles"})
print(f"Total results: {result2['total']}")
for p in result2["products"]:
    print(f"  - {p['name']} | Rs.{p['price']}")

print("\n" + "="*50)
print("TEST 3 — Price filter Rs.500 to Rs.1000")
print("="*50)
result3 = keyword_search(price_gte=500, price_lte=1000)
print(f"Total results: {result3['total']}")
for p in result3["products"]:
    print(f"  - {p['name']} | Rs.{p['price']}")

print("\n" + "="*50)
print("TEST 4 — Search 'luxury floor' (semantic gap test for Phase 5)")
print("="*50)
result4 = keyword_search(query_text="luxury floor")
print(f"Total results: {result4['total']}")
for p in result4["products"]:
    print(f"  - {p['name']} (score: {p['_score']:.2f})")