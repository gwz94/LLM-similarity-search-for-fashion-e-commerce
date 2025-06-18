import json
import logging
import os

import pandas as pd
from dotenv import load_dotenv

from app.database.vector_db import VectorDatabase
from app.preprocessing.preprocess_pipeline import preprocess_data
from app.config.settings import Settings
from app.utils.logger import setup_logger

load_dotenv()
settings = Settings()

# Set up specific loggers
loggers = {
    "data_loader": setup_logger("data_loader"),
    "dataset_preprocessing": setup_logger("dataset_preprocessing"),
    "vector_database": setup_logger("vector_database"),
}

def init_database() -> VectorDatabase:
    """
    Initialize the vector database connection and database tables.

    Returns:
        VectorDatabase: Initialized vector database instance
    """

    loggers["vector_database"].info("Initializing database...")

    # Parse connection parameters
    connection_params = {
        "host": settings.DB_HOST,
        "port": settings.DB_PORT,
        "user": settings.DB_USER,
        "password": settings.DB_PASSWORD,
        "dbname": settings.DB_NAME,
    }

    loggers["vector_database"].info("Connection parameters", extra={"params": connection_params})

    # Initialize vector database
    vector_db = VectorDatabase(connection_params)
    vector_db.connect()

    # Initialize database tables
    vector_db.initialize_database()

    return vector_db


def main():
    try:
        # Initialize database
        vector_db = init_database()

        # Load products information from file
        loggers["data_loader"].info("Loading products information from file...", 
                                    extra={"file_path": settings.PRODUCT_DATA_PATH})
        data = []
        with open(settings.PRODUCT_DATA_PATH, "r") as f:
            for line in f:
                item = json.loads(line)
                data.append(item)

        # Use DATA_LOAD_FRACTION to control how much data to load
        data = data[:len(data) // settings.DATA_LOAD_FRACTION]
        loggers["data_loader"].info(f"Loading 1/{settings.DATA_LOAD_FRACTION} of the data ({len(data)} products)")

        # Process data in smaller batches
        BATCH_SIZE = len(data) // 20
        for i in range(0, len(data), BATCH_SIZE):
            batch = data[i : i + BATCH_SIZE]
            df = pd.DataFrame(batch)
            loggers["data_loader"].info(
                f"Processing batch {i // BATCH_SIZE + 1}, {len(df)} products"
            )

            # Preprocess the batch
            df = preprocess_data(df)

            # Split into in-stock and out-of-stock products
            in_stock_df = df[df["inventory_status"] == "in_stock"]
            out_of_stock_df = df[df["inventory_status"] == "out_of_stock"]

            # Insert in-stock products
            if not in_stock_df.empty:
                vector_db.insert_products_information(in_stock_df)

            # Insert out-of-stock products
            if not out_of_stock_df.empty:
                vector_db.insert_products_information(out_of_stock_df)

            loggers["data_loader"].info(
                f"Successfully processed batch {i // BATCH_SIZE + 1}"
            )

        loggers["data_loader"].info("Data loading completed successfully!")

    except Exception as e:
        loggers["data_loader"].error(f"Error during data loading: {str(e)}")
        raise
    finally:
        if "vector_db" in locals():
            vector_db.disconnect()


if __name__ == "__main__":
    main()
