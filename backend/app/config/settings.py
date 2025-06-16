import os
from pathlib import Path
from dotenv import load_dotenv

# Get the root directory of the project
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

# Path to the raw data
PRODUCT_DATA_PATH = os.path.join(ROOT_DIR, "raw_data", "meta_amazon_fashion.jsonl")

# Product columns to be inserted into the database
PRODUCT_DB_COLUMNS = ["title", "average_rating", "rating_number", "features", "description", 
                      "price", "images", "store", "categories", "details", "embedding"]

# Batch size for inserting products into the database
PRODUCT_BATCH_SIZE = 1_000

# Similarity threshold for search
SEARCH_SIMILARITY_THRESHOLD = 0.0

# Table names for in stock and out of stock products
IN_STOCK_PRODUCTS_TABLE_NAME = "in_stock_products"
OUT_OF_STOCK_PRODUCTS_TABLE_NAME = "out_of_stock_products"

# Model for image feature extraction
IMAGE_FEATURE_EXTRACTION_MODEL = "gpt-4.1-mini"

# Model for reranking search results
RERANKER_MODEL_NAME = "gpt-4"  # or any other model you prefer for reranking

# Batch size for embedding products description
PRODUCT_EMBEDDING_BATCH_SIZE = 2000

# Temperature set for consistency
LLM_RERANKER_TEMPERATURE = 0.1

# Top P set for consistency
LLM_RERANKER_TOP_P = 1