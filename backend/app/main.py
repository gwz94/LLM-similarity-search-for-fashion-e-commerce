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

class Message(BaseModel):
    role: str
    query: str

    @field_validator("query")
    @classmethod
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError("Message cannot be empty or only spaces.")
        if len(v) > 500:
            raise ValueError("Message cannot be longer than 500 characters.")
        if re.search(r"(bomb|kill|attack|gun)", v, re.IGNORECASE):
            raise ValueError("Message contain inappropriate words.")
        if re.search(r"[<>{}[\]\\]", v):  # Prevent HTML/script injection
            raise ValueError("Query contains invalid characters.")
        return v

class ChatMessage(BaseModel):
    messages: list[Message]

class SearchQuery(BaseModel):
    query: str
    limit: Optional[int] = 5
    out_of_stock_products_recommendation: Optional[bool] = True

    @field_validator("query")
    @classmethod
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError("Query cannot be empty or only spaces.")
        if len(v) > 500:
            raise ValueError("Query cannot be longer than 500 characters.")
        if re.search(r"[<>{}[\]\\]", v):  # Prevent HTML/script injection
            raise ValueError("Query contains invalid characters.")
        return v

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v):
        if v is not None and (v < 1 or v > 100):
            raise ValueError("Limit must be between 1 and 100.")
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
        "host": "localhost",
        "port": 5432,
        "user": "postgres",
        "password": "postgres",
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
        
        # Search in both tables
        in_stock_results = db.search_products(
            query_embedding=query_embedding,
            table_name="in_stock_products",
            top_k=query.limit
        )
        
        out_of_stock_results = db.search_products(
            query_embedding=query_embedding,
            table_name="out_of_stock_products",
            top_k=query.limit
        )
        
        # Add stock status to results
        for result in in_stock_results:
            result["stock_status"] = "in_stock"
        for result in out_of_stock_results:
            result["stock_status"] = "out_of_stock"
        
        reranked_results = rerank_search_results(
            in_stock_search_results=in_stock_results,
            out_of_stock_search_results=out_of_stock_results,
            query=query.query,
            out_of_stock_products_recommendation=query.out_of_stock_products_recommendation
        )

        return {
            "status": "success",
            "recommended_products": reranked_results
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


        


