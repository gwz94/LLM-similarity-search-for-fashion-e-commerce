from app.database.vector_db import VectorDatabase
from app.ai_utils.embeddings import get_embedding
from dotenv import load_dotenv

from app.config.settings import Settings

settings = Settings()

load_dotenv()

if __name__ == "__main__":
    embedded_query = get_embedding("I need an outfit to go to the beach this summer")
    # Create VectorDatabase instance
    db = VectorDatabase(
        connection_params={
            "host": settings.DB_HOST,
            "port": settings.DB_PORT,
            "user": settings.DB_USER,
            "password": settings.DB_PASSWORD,
            "dbname": settings.DB_NAME,
        }
    )
    # Connect to database
    db.connect()
    # Search products
    result = db.search_products(
        query_embedding=embedded_query, table_name="in_stock_products"
    )
    result_not_in_stock = db.search_products(
        query_embedding=embedded_query, table_name="out_of_stock_products"
    )
    print(result)
    # Disconnect from database
    db.disconnect()
