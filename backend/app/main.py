from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import os

from app.schemas import QueryValidationBase
from dotenv import load_dotenv
from app.deps import DB
from app.ai_utils.llm_reranker import rerank_search_results
from app.ai_utils.embeddings import get_embedding
from app.utils.logger import setup_logger
from app.config.settings import get_settings

load_dotenv()

# Initialize settings
settings = get_settings()

logger = setup_logger("fashion_ecommerce")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

# Get CORS origins from environment variable or use defaults for development
cors_origins_env = os.getenv("CORS_ORIGINS", "")
origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

# Add default origins for development if none are specified
if not origins:
    origins = ["http://localhost:3000", "http://localhost:3001"]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Search products endpoint
@app.post("/search")
async def search_products(query: QueryValidationBase, db: DB):
    try:
        logger.info("Received search request", extra={
            "query": query.query,
            "top_k": query.top_k,
            "raw_request": query.model_dump()
        })
        print(f"Received query: {query.query}")

        # Get embedding for the query
        query_embedding = get_embedding(query.query)

        # Search in in_stock_products table
        in_stock_results = db.search_products(
            query_embedding=query_embedding,
            table_name=settings.IN_STOCK_PRODUCTS_TABLE_NAME,
            top_k=query.top_k,
        )
        logger.info(f"Found {len(in_stock_results)} in-stock products")

        # Search in out_of_stock_products table
        out_of_stock_results = db.search_products(
            query_embedding=query_embedding,
            table_name=settings.OUT_OF_STOCK_PRODUCTS_TABLE_NAME,
            top_k=query.top_k,
        )
        logger.info(f"Found {len(out_of_stock_results)} out-of-stock products")

        # Add stock status to results
        for result in in_stock_results:
            result["stock_status"] = "in_stock"
        for result in out_of_stock_results:
            result["stock_status"] = "out_of_stock"

        # Rerank search results using LLM
        reranked_in_stock_results = rerank_search_results(
            products_search_results=in_stock_results,
            stock_status="in_stock",
            query=query.query,
        )
        reranked_out_of_stock_results = rerank_search_results(
            products_search_results=out_of_stock_results,
            stock_status="out_of_stock",
            query=query.query,
        )

        return {
            "status": "success",
            "recommended_in_stock_products": reranked_in_stock_results,
            "recommended_out_of_stock_products": reranked_out_of_stock_results,
        }
    except ValueError as e:
        logger.error("Validation error", extra={"error": str(e)})
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error("Search error", extra={"error": str(e)})
        raise HTTPException(
            status_code=500, detail=f"Error processing search request: {str(e)}"
        )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error("Request validation error", extra={
        "error": str(exc),
        "body": await request.body()
    })
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
