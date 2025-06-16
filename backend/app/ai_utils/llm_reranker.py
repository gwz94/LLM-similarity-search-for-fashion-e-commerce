import os
import logging
import json
from dotenv import load_dotenv
from app.clients.openai_client import get_openai_client
from app.config import LLM_RERANKER_TEMPERATURE, LLM_RERANKER_TOP_P

load_dotenv()
logger = logging.getLogger(__name__)


def summarize_products(products: list[dict], stock_status: str) -> list[dict]:
    return [
        {
            "id": p["id"],
            "stock_status": stock_status,
            "title": p["title"],
            "similarity": p.get("similarity", 0),
            "features": p.get("features", []),
            "details": p.get("details", []),
            "price": p["price"],
            "reason": p.get("reason", "")
        }
        for p in products
    ]


def build_rerank_prompt(
    query: str,
    summarized_in_stock: list[dict],
) -> str:
    return f"""
        ## USER QUERY
        {query}

        ## CANDIDATE PRODUCTS
        Top 10 in-stock items:
        {json.dumps(summarized_in_stock, indent=2)}

        ## TASK
        1. Re-rank the candidates in order of relevance to the user's query.
        2. If the user wants out-of-stock items, merge both lists before ranking; otherwise rank only the in-stock list.
        3. Rank 1 = most relevant. Use ties only if scores are identical.
        4. IMPORTANT: You MUST use the EXACT product IDs from the input data. Do not generate new IDs.

        ## OUTPUT FORMAT
        (return **exactly** this JSON structure)
        {{
        "reranked_results": [
            {{
            "id": "EXACT_ID_FROM_INPUT",  // Must match an ID from the input data
            "rank": 1,
            "stock_status": "in_stock",
            "rerank_score": 0.95,
            "reason": "Generate a reason for recommending this product to encourage the user to purchase it."
            }}
            /* repeat for each product */
        ],
        "query_understanding": "Summary of what the user is looking for",
        "notes": "Why out-of-stock items were included, if applicable"
        }}

        Rules:
        - Do **not** add extra keys, comments, or trailing commas in the final JSON.
        - You MUST use the EXACT product IDs from the input data. Do not generate new IDs.
        - The system will verify that all IDs match the input data.
    """


def merge_reranked_with_full_products(reranked_items: list[dict], full_products: list[dict]) -> list[dict]:
    # Create product map with both string and integer versions of IDs
    product_map = {}
    for p in full_products:
        id_value = p["id"]
        # Store both string and integer versions of the ID
        product_map[str(id_value)] = p
        if isinstance(id_value, (int, float)):
            product_map[int(id_value)] = p
        elif isinstance(id_value, str) and id_value.isdigit():
            product_map[int(id_value)] = p
    
    results = []

    # Create a mapping of reranked items by ID for quick lookup
    reranked_map = {str(item.get("id")): item for item in reranked_items}

    # Process items in the order they appear in reranked_items to maintain ranking
    for item in reranked_items:
        item_id = item.get("id")
        
        # Try to find the product using different ID formats
        full = None
        if item_id is not None:
            # Try string version
            full = product_map.get(str(item_id))
            if not full and isinstance(item_id, (int, float)):
                # Try integer version
                full = product_map.get(int(item_id))
            elif not full and isinstance(item_id, str) and item_id.isdigit():
                # Try converting string to integer
                full = product_map.get(int(item_id))
        
        if full:
            results.append({
                **full,
                "rank": item["rank"],
                "rerank_score": item["rerank_score"],
                "reason": item["reason"]
            })

    # Sort results by rank to ensure consistent ordering
    results.sort(key=lambda x: x["rank"])

    return results


def rerank_search_results(
    products_search_results: list[dict],
    stock_status: str,
    query: str
) -> list[dict]:
    openai_client = get_openai_client()

    summarized_product_details = summarize_products(products_search_results, stock_status)

    prompt = build_rerank_prompt(
        query,
        summarized_product_details
    )

    response = openai_client.responses.create(
        model=os.getenv("PRODUCT_RECOMMENDATION_RERANKER_MODEL"),
        input=prompt,
        temperature=LLM_RERANKER_TEMPERATURE,
        top_p=LLM_RERANKER_TOP_P
    )

    try:
        parsed_output = json.loads(response.output_text)
        reranked_items = parsed_output.get("reranked_results", [])
        
        # Create a mapping of all available product IDs
        available_ids = {str(p["id"]): p for p in products_search_results}
        
        # Filter reranked items to only include those with valid IDs
        valid_reranked_items = []
        for item in reranked_items:
            item_id = str(item.get("id"))
            if item_id in available_ids:
                valid_reranked_items.append(item)
        
        merged_results = merge_reranked_with_full_products(
            valid_reranked_items, products_search_results
        )
        return merged_results
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        logger.error(f"Raw response: {response.output_text}")
        return products_search_results
