import os
import logging

from dotenv import load_dotenv
from app.clients.openai_client import get_openai_client

load_dotenv()

logger = logging.getLogger(__name__)

def rerank_search_results(
        in_stock_search_results: list[dict],
        out_of_stock_search_results: list[dict],
        query: str, 
        out_of_stock_products_recommendation: bool
        ) -> list[dict]:
    
    system_prompt = """
        You are a helpful assistant that reranks search results based on the user's query.
    """

    input_prompt = f"""
        ## USER QUERY

        {query}

        ## USER PREFERENCE ABOUT OUT-OF-STOCK ITEMS
        {out_of_stock_products_recommendation}

        ## CANDIDATE PRODUCTS

        Top 10 in-stock items:
        {in_stock_search_results}

        Top 10 out-of-stock items:
        {out_of_stock_search_results}

        ## TASK
        1. Re-rank the candidates in order of relevance to the user's query.
        2. If the user wants out-of-stock items, merge both lists before ranking;
        otherwise rank only the in-stock list.
        3. Rank 1 = most relevant. Use ties only if scores are identical.

        ## OUTPUT FORMAT  (return **exactly** this JSON structure)
        {{
        "reranked_results": [
            {{
            "rank": 1,                     // integer ≥ 1
            "stock_status": "in_stock",    // "in_stock" | "out_of_stock"
            "title": "Red T-Shirt, 100 % Cotton",
            "similarity": 0.87,            // original vector score (0–1)
            "rerank_score": 0.95,          // your relevance score (0–1)
            "reason": "Exact color + material match",
            "metadata": {{
                "average_rating": 4.6,
                "rating_number": 128,
                "features": ["breathable", "pre-shrunk"],
                "description": "Soft jersey knit …",
                "price": 2599,
                "images": ["https://…"],
                "store": "GiveGift",
                "categories": ["Apparel", "Tops"],
                "details": {{"Brand": "YUEDGE", "Size": "M"}}
            }}ß
            }}
            /* repeat for every product you return, in rank order */
        ],

        "query_understanding": "Brief summary of what the user is looking for and why do you recommend the products you recommend",
        "notes": "Any special considerations (e.g., why out-of-stock items were included)"
        }}

        Rules:
        - Do **not** add extra keys, comments, or trailing commas in the final JSON.
        - Keep the original `similarity`; choose `rerank_score` yourself (0–1).
        - If no product is relevant, return `"reranked_results": []`.
        """
    
    openai_client = get_openai_client()

    # NOTE: If previous response.id could be sent from frontend, we can use it to continue the conversation
    response = openai_client.responses.create(
        model=os.getenv("PRODUCT_RECOMMENDATION_RERANKER_MODEL"),
        input=input_prompt,
    )

    return response.output_text
