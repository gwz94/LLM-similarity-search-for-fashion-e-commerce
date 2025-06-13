import logging
import pandas as pd
from typing import Dict, Any

from app.database.vector_db import VectorDatabase
from OpenAI_assignment.backend.app.database.product_loader import load_products
from app.config.settings import (
    DATABASE_URL,
    IN_STOCK_PRODUCTS_TABLE_NAME,
    OUT_OF_STOCK_PRODUCTS_TABLE_NAME
)

# Set up logger
logger = logging.getLogger("data_loader")
logger.setLevel(logging.INFO)

def init_database() -> VectorDatabase:
    """
    Initialize the vector database connection.
    
    Returns:
        VectorDatabase: Initialized vector database instance
    """
    # Parse connection parameters from DATABASE_URL
    connection_params = {
        "host": "localhost",  # Update with your host
        "port": 5432,        # Update with your port
        "user": "postgres",  # Update with your username
        "password": "postgres",  # Update with your password
        "database": "amazon_fashion"  # Update with your database name
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
        logger.info("Initializing database...")
        vector_db = init_database()
        
        # Load your data into a DataFrame
        # Example: df = pd.read_csv("your_data.csv")
        df = pd.DataFrame()  # Replace with your actual data loading
        
        # Load products
        logger.info("Loading products...")
        load_products(df, IN_STOCK_PRODUCTS_TABLE_NAME)
        
        logger.info("Data loading completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during data loading: {str(e)}")
        raise
    finally:
        if 'vector_db' in locals():
            vector_db.disconnect()

if __name__ == "__main__":
    main() 