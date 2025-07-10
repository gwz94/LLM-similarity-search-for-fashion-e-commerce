import os
import json
from dotenv import load_dotenv
from app.clients.openai_client import get_openai_client
from app.config.settings import Settings
from app.utils.logger import setup_logger

logger = setup_logger("llm_reranker")

load_dotenv()

settings = Settings()


def build_rerank_prompt(
    query: str,
    summarized_product_details: list[dict],
) -> str:
    """
    Build the prompt for the LLM to rerank the products.

    Args:
        query (str): The user's query.
        summarized_product_details (list[dict]): The summarized product details.

    Returns:
        str: The prompt for the LLM to rerank the products.
    """
    
    logger.info("Building rerank prompt", extra={
        "query": query,
        "num_products": len(summarized_product_details)
    })
    return f"""
        ## USER QUERY
        {query}

        ## CANDIDATE PRODUCTS
        Top 10 relevant items:
        {summarized_product_details}

        ## TASK
        1. Re-rank the candidates in order of relevance to the user's query.
        2. Prioritize products with high average rating and high rating number.
        3. Rank 1 = most relevant. Use ties only if scores are identical.
        4. IMPORTANT: You MUST use the EXACT product IDs from the input data. Do not generate new IDs.
        5. Generate a reason for recommending this product to encourage the user to purchase it.
    
        ## OUTPUT FORMAT
        (return **exactly** this JSON structure)
        {{
        "reranked_results": [
            {{
            "id": "EXACT_ID_FROM_INPUT",  // Must match an ID from the input data
            "rank": 1,
            "rerank_score": 0.95,
            "reason": "Reason for recommending this product to encourage the user to purchase it."
            }}
            /* repeat for each product */
        ],
        "query_understanding": "Summary of what the user is looking for",
        }}

        Rules:
        - Do **not** add extra keys, comments, or trailing commas in the final JSON.
        - You MUST use the EXACT product IDs from the input data. Do not generate new IDs.
        - The system will verify that all IDs match the input data.
    """


def merge_reranked_with_all_relevant_products(
    reranked_items: list[dict], all_relevant_products: list[dict]
) -> list[dict]:
    """
    Merge the reranked items with the all relevant products.

    Args:
        reranked_items (list[dict]): The list of reranked items.
        all_relevant_products (list[dict]): The list of all products.
    """
    logger.info("Starting product merge", extra={
        "reranked_items_count": len(reranked_items),
        "all_products_count": len(all_relevant_products)
    })

    def to_int_id(value):
        """ Function to convert the id to an integer """
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    # Build product map with int IDs
    product_map = {}
    for p in all_relevant_products:
        int_id = to_int_id(p.get("id"))
        if int_id is not None:
            product_map[int_id] = p

    results = []
    skipped_items = 0

    print(reranked_items)
    # Process reranked items in order
    for item in reranked_items:
        int_id = to_int_id(item.get("id"))
        if int_id is not None:
            full_product = product_map.get(int_id)
            if full_product:
                # Preserve the reason and rank from the reranked item
                merged = {
                    **full_product,
                    "reason": item.get("reason", ""),
                    "rank": item.get("rank", 0),
                    "rerank_score": item.get("rerank_score", 0)
                }
                results.append(merged)
            else:
                skipped_items += 1

    # Sort results by rank
    results.sort(key=lambda x: x.get("rank", 0))

    logger.info("Product merge completed", extra={
        "merged_count": len(results),
        "skipped_items": skipped_items
    })

    return results


def rerank_search_results(
    products_search_results: list[dict], stock_status: str, query: str
) -> list[dict]:
    """
    Rerank the search results based on the user's query.

    Args:
        products_search_results (list[dict]): The list of products to rerank.
        stock_status (str): The stock status of the products.
        query (str): The user's query.

    Returns:
        list[dict]: The reranked products.
    """
    try:
        logger.info("Starting search results reranking", extra={
            "query": query,
            "stock_status": stock_status,
            "num_products": len(products_search_results)
        })

        openai_client = get_openai_client()

        # Extract important product details for the LLM to rerank the products
        summarized_product_details = [
            {
                "id": p["id"],
                "title": p["title"],
                "similarity": p.get("similarity", 0),
                "features": p.get("features", []),
                "details": p.get("details", []),
                "average_rating": p.get("average_rating", 0),
                "rating_number": p.get("rating_number", 0),
                "price": float(p.get("price", 0.0)) if p.get("price") is not None else 0.0,
                "reason": p.get("reason", "")
            }
            for p in products_search_results
        ]

        logger.info("Product details summarized", extra={
            "summarized_count": len(summarized_product_details)
        })


        # Build the prompt for the LLM to rerank the products
        prompt = build_rerank_prompt(query, summarized_product_details)

        # Call the LLM to rerank the products
        logger.info("Sending request to LLM", extra={
            "model": os.getenv("PRODUCT_RECOMMENDATION_RERANKER_MODEL"),
            "temperature": settings.LLM_RERANKER_TEMPERATURE,
            "top_p": settings.LLM_RERANKER_TOP_P
        })

        response = openai_client.responses.create(
            model=settings.IMAGE_FEATURE_EXTRACTION_MODEL,
            input=prompt,
            temperature=settings.LLM_RERANKER_TEMPERATURE,
            top_p=settings.LLM_RERANKER_TOP_P,
        )

        try:
            parsed_output = json.loads(response.output_text)
            reranked_items = parsed_output.get("reranked_results", [])

            logger.info("LLM response parsed successfully", extra={
                "reranked_items_count": len(reranked_items)
            })

            # Merged reranked items with their products metadata
            merged_results = merge_reranked_with_all_relevant_products(
                reranked_items, products_search_results
            )

            logger.info("Reranking completed successfully", extra={
                "final_results_count": len(merged_results)
            })

            return merged_results

        except json.JSONDecodeError as e:
            logger.error("Failed to parse LLM response", extra={
                "error": str(e),
                "error_type": "JSONDecodeError",
                "raw_response": response.output_text[:200] 
            })
            return products_search_results

    except Exception as e:
        logger.error("Reranking failed", extra={
            "error": str(e),
            "error_type": type(e).__name__,
            "query": query,
            "stock_status": stock_status
        })
        return products_search_results
