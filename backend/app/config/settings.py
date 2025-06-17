import os
from pathlib import Path


from pydantic_settings import BaseSettings
from functools import lru_cache

# # Get the root directory of the project
ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # Common settings
    APP_NAME: str = "Fashion E-commerce Search API"
    APP_VERSION: str = "v1"

    # Controls how much data to load (1 = 25% of data, 2 = 50%, 4 = 100%)
    DATA_LOAD_FRACTION: int = 2

    # Database settings
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # OpenAI settings
    OPENAI_API_KEY: str
    EMBEDDING_MODEL_NAME: str = "text-embedding-3-small"
    IMAGE_FEATURE_EXTRACTION_MODEL: str = "gpt-4.1-mini"

    RERANKER_MODEL_NAME: str = "gpt-4.1-nano"    
    LLM_RERANKER_TEMPERATURE: float = 0.1
    LLM_RERANKER_TOP_P: float = 1.0

    # Vector settings
    EMBEDDING_DIMENSION: int = 1536

    # Product settings
    PRODUCT_BATCH_SIZE: int = 1_000
    PRODUCT_EMBEDDING_BATCH_SIZE: int = 2_000
    PRODUCT_RECOMMENDATION_BATCH_SIZE: int = 100
    PRODUCT_RECOMMENDATION_TOP_K: int = 5
    PRODUCT_RECOMMENDATION_TEMPERATURE: float = 0.1
    PRODUCT_RECOMMENDATION_TOP_P: float = 1.0
  
    # Product data path
    PRODUCT_DATA_PATH: str = "/app/raw_data/meta_Amazon_Fashion.jsonl"

    PRODUCT_DB_COLUMNS: list[str] = [
        "title",
        "average_rating",
        "rating_number",
        "features",
        "description",
        "price",
        "images",
        "store",
        "categories",
        "details",
        "embedding",
    ]

    # Table names for in stock and out of stock products
    IN_STOCK_PRODUCTS_TABLE_NAME: str = "in_stock_products"
    OUT_OF_STOCK_PRODUCTS_TABLE_NAME: str = "out_of_stock_products"

    # Environment specific settings
    ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env.development"

class DevSettings(Settings):
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"

class ProdSettings(Settings):
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

@lru_cache
def get_settings() -> Settings:
    if os.getenv("ENV") == "production":
        return ProdSettings()
    return DevSettings()