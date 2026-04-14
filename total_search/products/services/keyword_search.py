from products.infrastructure.elastic_client import elastic

INDEX_NAME = "products"

FIELDS_WEIGHTAGE = [
    "name^10",        # name match is highest priority — same as production product_name^10
    "brand^8",        # brand match second — mirrors brand.brand_name^8
    "category^8",     # category match — mirrors category.category_name^8
    "description^3",  # description is useful but lower weight
    "color^5",        # color match — mirrors color.color_family^5
    "material^4",     # material match — new, not in production
]


def keyword_search(
    query_text: str = None,
    filters: dict = None,
    page: int = 0,
    page_size: int = 20,
    price_gte: float = None,
    price_lte: float = None,
) -> dict:
    """
    Performs a keyword search against Elasticsearch with optional filters
    and returns product results plus aggregation counts for sidebar filters.

    Based on fetchProductDataV2 from the production opensearch_client.py,
    simplified to the essential logic only:
      - query_string with field weightage (same concept as production)
      - keyword filters on brand and category (same as production .keyword terms)
      - price range filter (same range query pattern)
      - terms aggregations for brand and category (simplified from production global aggs)

    Args:
        query_text:  The user's search string, e.g. "blue marble"
        filters:     Dict of exact filters, e.g. {"category": "Tiles", "brand": "TileMax"}
        page:        Page number (0-indexed)
        page_size:   Results per page
        price_gte:   Minimum price filter (optional)
        price_lte:   Maximum price filter (optional)

    Returns:
        {
            "total":        int,
            "products":     [list of product dicts],
            "aggregations": {
                "brands":     [{"key": "TileMax", "count": 5}, ...],
                "categories": [{"key": "Tiles", "count": 12}, ...],
            }
        }
    """
    es = elastic.get_client()

    # --- Build the base request body ---
    body = {
        "size": page_size,
        "from": page * page_size,
        "track_total_hits": True,
        "query": {
            "bool": {
                "must":   [],
                "filter": [],
            }
        },
        "aggs": {
            "brands": {
                "terms": {
                    "field": "brand.keyword",
                    "size":  50,
                }
            },
            "categories": {
                "terms": {
                    "field": "category.keyword",
                    "size":  50,
                }
            },
            "price_min": {"min": {"field": "price"}},
            "price_max": {"max": {"field": "price"}},
        }
    }

    # --- Text search: query_string with field weights ---
    # Mirrors the production FIELDS_WEIGHTAGE pattern exactly.
    # Wildcards (*query*) allow partial matching — same as production "*" + searchText + "*"
    if query_text and query_text.strip():
        clean_query = query_text.strip().replace("-", " ").replace("/", " ")
        body["query"]["bool"]["must"].append({
            "query_string": {
                "query":       f"*{clean_query}*",
                "fields":      FIELDS_WEIGHTAGE,
                "phrase_slop": 2,
            }
        })

    # --- Keyword filters on brand and category ---
    # Production used {"terms": {"brand.brand_name.keyword": [value]}}
    # We use the same pattern mapped to our flat field names.
    if filters:
        if "category" in filters and filters["category"]:
            body["query"]["bool"]["filter"].append({
                "terms": {"category.keyword": [filters["category"]]}
            })
        if "brand" in filters and filters["brand"]:
            body["query"]["bool"]["filter"].append({
                "terms": {"brand.keyword": [filters["brand"]]}
            })
        if "color" in filters and filters["color"]:
            body["query"]["bool"]["filter"].append({
                "term": {"color": filters["color"]}
            })
        if "material" in filters and filters["material"]:
            body["query"]["bool"]["filter"].append({
                "term": {"material": filters["material"]}
            })

    # --- Price range filter ---
    # Same range query pattern as production.
    price_range = {}
    if price_gte is not None:
        price_range["gte"] = price_gte
    if price_lte is not None:
        price_range["lte"] = price_lte
    if price_range:
        body["query"]["bool"]["filter"].append({
            "range": {"price": price_range}
        })

    # Always filter to active products only
    body["query"]["bool"]["filter"].append({
        "term": {"is_active": True}
    })

    # --- Execute the search ---
    try:
        response = es.search(index=INDEX_NAME, body=body)
    except Exception as e:
        print(f"[KeywordSearch] Search failed: {e}")
        return {"total": 0, "products": [], "aggregations": {}}

    # --- Parse results ---
    hits = response.get("hits", {})
    total = hits.get("total", {}).get("value", 0)

    products = []
    for hit in hits.get("hits", []):
        doc = hit["_source"]
        doc["_score"] = hit["_score"]
        products.append(doc)

    # --- Parse aggregations (sidebar filter counts) ---
    raw_aggs = response.get("aggregations", {})
    aggregations = {
        "brands": [
            {"key": b["key"], "count": b["doc_count"]}
            for b in raw_aggs.get("brands", {}).get("buckets", [])
        ],
        "categories": [
            {"key": c["key"], "count": c["doc_count"]}
            for c in raw_aggs.get("categories", {}).get("buckets", [])
        ],
        "price_min": raw_aggs.get("price_min", {}).get("value"),
        "price_max": raw_aggs.get("price_max", {}).get("value"),
    }

    return {
        "total":        total,
        "products":     products,
        "aggregations": aggregations,
    }