import json
import logging
import os

import pandas as pd
from dotenv import load_dotenv
from typing import Dict, Any

from app.database.vector_db import VectorDatabase
from app.preprocessing.preprocess_data import preprocess_data
from app.config.settings import (
    IN_STOCK_PRODUCTS_TABLE_NAME,
    OUT_OF_STOCK_PRODUCTS_TABLE_NAME,
    PRODUCT_DATA_PATH
)

load_dotenv()

# Set up specific loggers
loggers = {
    "data_loader": logging.getLogger("data_loader"),
    "dataset_preprocessing": logging.getLogger("dataset_preprocessing"),
    "vector_database": logging.getLogger("vector_database")
}

# Configure all loggers
# TODO: Refactor the logging and save the logs to a file
for logger in loggers.values():
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

def init_database() -> VectorDatabase:
    """
    Initialize the vector database connection and database tables.
    
    Returns:
        VectorDatabase: Initialized vector database instance
    """
    # Parse connection parameters
    connection_params = {
        "host": os.getenv("DB_HOST"),  
        "port": os.getenv("DB_PORT"),        
        "user": os.getenv("DB_USER"), 
        "password": os.getenv("DB_PASSWORD"),  
    }
    
    # Initialize vector database
    vector_db = VectorDatabase(connection_params)
    vector_db.connect()
    
    # Initialize database tables
    vector_db.initialize_database()
    
    return vector_db

def main():
    try:
        # Initialize database
        loggers["data_loader"].info("Initializing database...")
        vector_db = init_database()
        
        # Load products information from file
        data = []
        with open(PRODUCT_DATA_PATH, "r") as f:
            for line in f:
                item = json.loads(line)
                data.append(item)

        df = pd.DataFrame(data)[:1000]
        loggers["data_loader"].info(f"Loaded {len(df)} products from file")

        # Preprocess data
        df = preprocess_data(df)
        loggers["data_loader"].info(f"Preprocessing completed. {len(df)} products remaining")

        # Insert products information into database
        loggers["data_loader"].info("Loading products into database...")
        vector_db.insert_products_information(df, IN_STOCK_PRODUCTS_TABLE_NAME)

        loggers["data_loader"].info("Data loading completed successfully!")
        
    except Exception as e:
        loggers["data_loader"].error(f"Error during data loading: {str(e)}")
        raise
    finally:
        if 'vector_db' in locals():
            vector_db.disconnect()

if __name__ == "__main__":
    main() 