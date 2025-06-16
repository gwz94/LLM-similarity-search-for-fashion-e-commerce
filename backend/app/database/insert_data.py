import json
import logging
import os

import pandas as pd
from dotenv import load_dotenv
from typing import Dict, Any

from app.database.vector_db import VectorDatabase
from app.preprocessing.preprocess_data import preprocess_data
from app.config.settings import PRODUCT_DATA_PATH


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
        "port": int(os.getenv("DB_PORT")),        
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

        # NOTE:Use only half of the data because of limited memory on my computer
        data = data[ : len(data) // 2]
        
        # Process data in smaller batches
        BATCH_SIZE = len(data) // 2
        for i in range(0, len(data), BATCH_SIZE):
            batch = data[i:i + BATCH_SIZE]
            df = pd.DataFrame(batch)
            loggers["data_loader"].info(f"Processing batch {i//BATCH_SIZE + 1}, {len(df)} products")
            
            # Preprocess the batch
            df = preprocess_data(df)
            
            # Split into in-stock and out-of-stock products
            in_stock_df = df[df['inventory_status'] == "in_stock"]
            out_of_stock_df = df[df['inventory_status'] == "out_of_stock"]
            
            # Insert in-stock products
            if not in_stock_df.empty:
                vector_db.insert_products_information(in_stock_df)
            
            # Insert out-of-stock products
            if not out_of_stock_df.empty:
                vector_db.insert_products_information(out_of_stock_df)
            
            loggers["data_loader"].info(f"Successfully processed batch {i//BATCH_SIZE + 1}")

        loggers["data_loader"].info("Data loading completed successfully!")
        
    except Exception as e:
        loggers["data_loader"].error(f"Error during data loading: {str(e)}")
        raise
    finally:
        if 'vector_db' in locals():
            vector_db.disconnect()

if __name__ == "__main__":
    main() 