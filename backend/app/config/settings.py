import os
from pathlib import Path
from dotenv import load_dotenv

# Get the root directory of the project
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

# Product columns to be inserted into the database
PRODUCT_DB_COLUMNS = ["title", "average_rating", "rating_number", "features", "description", 
                      "price", "images", "store", "categories", "details", "embedding"]
PRODUCT_BATCH_SIZE = 1_000
SEARCH_SIMILARITY_THRESHOLD = 0.5

IN_STOCK_PRODUCTS_TABLE_NAME = "instock_products"
OUT_OF_STOCK_PRODUCTS_TABLE_NAME = "out_of_stock_products"