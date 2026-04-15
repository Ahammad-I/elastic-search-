import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "total_search.settings")
django.setup()
from dotenv import load_dotenv
load_dotenv() 
print("\n" + "="*55)
print("PHASE 6 — Visual Search test")
print("="*55)

from products.services.visual_search import (
    get_visual_results,
    generate_text_image_embedding,
)

# Simulate an uploaded image by encoding a query description into CLIP
# (In real use this would be image bytes from request.FILES)
query_text = "grey stone floor outdoor"
query_embedding = generate_text_image_embedding(query_text)

print(f"CLIP embedding dimensions : {len(query_embedding)}")
print(f"Simulating image upload   : '{query_text}'")

# To test with real image bytes, convert the embedding back to bytes for demo
import numpy as np
from PIL import Image
import io

# Create a simple grey test image (simulates a grey stone photo)
img_array = np.full((100, 100, 3), 128, dtype=np.uint8)
img       = Image.fromarray(img_array)
buf       = io.BytesIO()
img.save(buf, format="JPEG")
image_bytes = buf.getvalue()

results = get_visual_results(image_bytes, top_n=5)
print(f"\nTop visual matches for uploaded image:")
for i, r in enumerate(results, 1):
    print(f"  {i}. {r['name']}")
    print(f"     Color: {r['color']} | Material: {r['material']}")
    print(f"     Visual similarity: {r['_visual_similarity']}")


print("\n" + "="*55)
print("PHASE 7 — RAG Orchestrator test")
print("="*55)

from products.services.rag_orchestrator import get_rag_recommendation, build_recommendation_prompt
from products.services.hybrid_engine import hybrid_search

# First print the prompt so you can see exactly what goes to the LLM
query = "I need durable flooring for my bathroom that looks premium"
products = hybrid_search(query, top_n=5)
prompt = build_recommendation_prompt(products, query)

print("PROMPT SENT TO LLM:")
print("-" * 50)
print(prompt)
print("-" * 50)

# Now run the full RAG pipeline
print("\nFull RAG response:")
result = get_rag_recommendation(query, top_n=5)
print(f"\nQuery    : {result['query']}")
print(f"Products : {len(result['products'])} retrieved")
print(f"\nLLM Recommendation:\n{result['recommendation']}")


print("\n" + "="*55)
print("PHASE 7 — RAG with category filter")
print("="*55)
result2 = get_rag_recommendation(
    "outdoor area tiles that are safe and weather resistant",
    filters={"category": "Tiles"},
    top_n=3,
)
print(f"\nQuery: {result2['query']}")
print(f"\nRecommendation:\n{result2['recommendation']}")