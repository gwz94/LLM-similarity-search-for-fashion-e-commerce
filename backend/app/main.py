import os
import re
from typing import Annotated, List, Optional
import atexit
import multiprocessing
import signal
import json
import asyncio
from fastapi.responses import StreamingResponse

from pydantic import BaseModel, field_validator
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.database.vector_db import VectorDatabase
from dotenv import load_dotenv
from app.ai_utils.llm_reranker import rerank_search_results
from app.ai_utils.embeddings import get_embedding
from app.config.settings import IN_STOCK_PRODUCTS_TABLE_NAME, OUT_OF_STOCK_PRODUCTS_TABLE_NAME

load_dotenv()

class QueryValidationBase(BaseModel):
    query: str

    @field_validator("query")
    @classmethod
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError("Query cannot be empty or only spaces.")
        if len(v) < 5:
            raise ValueError("Query cannot be shorter than 5 characters.")
        if len(v) > 500:
            raise ValueError("Query cannot be longer than 500 characters.")
        if re.search(r"""\b(gun|bomb|kill|murder|shoot|attack|weapon|explosive|bullet|acid|sniper|grenade|terror|
                            assault|execute|behead|poison|cyanide|sarin|anthrax|suicide\s*bomber|arson|sabotage|
                            molotov|lynch|genocide|riot|vandalism|rape|slaughter|firearm|extremist|burn\s*down|
                            hate\s*crime|abuse|threaten)\b""", v, re.IGNORECASE):
            raise ValueError("Query contains inappropriate words.")
        if re.search(r"[<>{}[\]\\]", v):
            raise ValueError("Query contains invalid characters.")
        return v

class Message(QueryValidationBase):
    role: str

class ChatMessage(BaseModel):
    messages: list[Message]

class SearchQuery(QueryValidationBase):
    top_k: Optional[int] = 5

    @field_validator("top_k")
    @classmethod
    def validate_top_k(cls, v):
        if v is not None and (v < 1 or v > 10):
            raise ValueError("top_k must be between 1 and 10.")
        return v


app = FastAPI(title="Fashion E-commerce Search")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def get_db():
    """Dependency to get database connection"""
    connection_params = {
        "host": os.getenv("POSTGRES_HOST", "127.0.0.1"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
    }
    db = VectorDatabase(connection_params)
    try:
        db.connect()
        yield db
    finally:
        db.disconnect()

# Type alias for dependency injection
DB = Annotated[VectorDatabase, Depends(get_db)]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/search")
async def search_products(query: SearchQuery, db: DB):
    try:
        # Validate query
        if not query.query.strip():
            raise HTTPException(
                status_code=422,
                detail="Query cannot be empty or only spaces."
            )
        
        # Get embedding for the query
        query_embedding = get_embedding(query.query)

        print(f"query: {query}")
        
        # Search in both tables
        in_stock_results = db.search_products(
            query_embedding=query_embedding,
            table_name="in_stock_products",
            top_k=query.top_k
        )
        
        out_of_stock_results = db.search_products(
            query_embedding=query_embedding,
            table_name="out_of_stock_products",
            top_k=query.top_k
        )
        
        # Add stock status to results
        for result in in_stock_results:
            result["stock_status"] = "in_stock"
        for result in out_of_stock_results:
            result["stock_status"] = "out_of_stock"
        
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
        
        print(f"reranked_in_stock_results: {reranked_in_stock_results}")
        print(f"reranked_out_of_stock_results: {reranked_out_of_stock_results}")

        return {
            "status": "success",
            "recommended_in_stock_products": reranked_in_stock_results,
            "recommended_out_of_stock_products": reranked_out_of_stock_results
        }
    except ValueError as e:
        # Handle validation errors
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error in search_products: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=500,
            detail=f"Error processing search request: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


        


