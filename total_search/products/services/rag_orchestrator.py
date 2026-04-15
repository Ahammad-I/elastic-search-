import os
from openai import OpenAI

from products.services.hybrid_engine import hybrid_search


def build_recommendation_prompt(products: list[dict], user_query: str) -> str:
    """
    Builds structured prompt using retrieved products (RAG augmentation)
    """
    if not products:
        return f"No products found matching: {user_query}"

    product_lines = []
    for i, p in enumerate(products, 1):
        block = (
            f"{i}. {p['name']}\n"
            f"   Brand    : {p.get('brand', 'N/A')}\n"
            f"   Category : {p.get('category', 'N/A')}\n"
            f"   Material : {p.get('material', 'N/A')}\n"
            f"   Color    : {p.get('color', 'N/A')}\n"
            f"   Price    : Rs. {p.get('price', 'N/A')}\n"
            f"   Match    : {p.get('_similarity_score', 'N/A')}"
        )
        product_lines.append(block)

    products_context = "\n\n".join(product_lines)

    prompt = f"""You are an expert interior designer specializing in tiles, flooring, and construction materials for Indian homes.

A customer has asked: "{user_query}"

Based on a semantic search of our product catalog, here are the most relevant products:

{products_context}

Please provide:
1. A brief recommendation of the best product(s) and why
2. Practical tips (installation, maintenance)
3. If multiple products fit, suggest use cases (bathroom, kitchen, etc.)

Rules:
- Keep response under 200 words
- DO NOT invent products or prices
- Use only provided data
- Be friendly and helpful
"""

    return prompt


def get_rag_recommendation(
    user_query: str,
    filters: dict = None,
    top_n: int = 5,
) -> dict:

    print(f"[RAG] Retrieving products for: '{user_query}'")

    # 🔹 Step 1: Retrieval
    products = hybrid_search(
        query_text=user_query,
        filters=filters,
        top_n=top_n,
    )

    print(f"[RAG] Retrieved {len(products)} products.")

    # 🔹 Step 2: Augmentation
    prompt = build_recommendation_prompt(products, user_query)

    # 🔹 Step 3: OpenAI Generation
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return {
            "query": user_query,
            "products": products,
            "prompt": prompt,
            "recommendation": "ERROR: OPENAI_API_KEY not set in .env",
        }

    try:
        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini",   # 💰 cheap + fast (best choice)
            messages=[
                {"role": "system", "content": "You are a helpful interior design expert."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
            temperature=0.7,
        )

        recommendation = response.choices[0].message.content

    except Exception as e:
        recommendation = f"LLM generation failed: {str(e)}"

    return {
        "query": user_query,
        "products": products,
        "prompt": prompt,
        "recommendation": recommendation,
    }