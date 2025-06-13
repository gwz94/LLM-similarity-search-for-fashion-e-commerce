import os
import logging
import json

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

from dotenv import load_dotenv
from app.ai_utils import embedding
from typing import List, Dict, Tuple, Any, Optional

from app.config.settings import IN_STOCK_PRODUCTS_TABLE_NAME, OUT_OF_STOCK_PRODUCTS_TABLE_NAME, PRODUCT_DB_COLUMNS, PRODUCT_BATCH_SIZE
from app.config.settings import SEARCH_SIMILARITY_THRESHOLD

load_dotenv()

class VectorDatabase:
    """
    Vector database class for storing and searching products.
    Postgresql and pgvector are used to store embeddings and perform similarity search.

    Attributes:
        connection_params: Dictionary containing database connection parameters
    """

    def __init__(self, connection_params: Dict[str, Any]):
        """
        Constructor for VectorDatabase class.

        Args:
            connection_params:
                - host: Database host
                - port: Database port
                - user: Database username
                - password: Database password
                - database: Database name
        """

        # Initialize logger
        self.logger = logging.getLogger("vector_database")
        self.logger.setLevel(logging.INFO)

        # Initialize connection parameters
        self.connection_params = connection_params
        self.conn = None
        self.embedding_dimension = os.getenv("EMBEDDING_DIMENSION")
    
    def connect(self) -> None:
        """
        Connect to the database.

        Raises:
            Exception: If failed to connect to the database
        """
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.logger.info("Connected to the database")
        except Exception as e:
            self.logger.error(f"Failed to connect to the database: {e}")
            raise
    
    def disconnect(self) -> None:
        """
        Disconnect from the database.

        Raises:
            Exception: If failed to disconnect from the database
        """

        if self.conn:
            self.conn.close()
            self.conn = None
            self.logger.info("Disconnected from the database")
    
    def initialize_database(self) -> None:
        """
        Initialize the database.

        Raises:
            Exception: if failed to initialize the database
        """

        try:
            if not self.conn:
                self.conn()

            cursor = self.conn.cursor()

            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")

            cursor.execute("DROP TABLE IF EXISTS in_stock_products")
            cursor.execute("DROP TABLE IF EXISTS out_of_stock_products")

            cursor.execute("""
                            CREATE TABLE IF NOT EXISTS in_stock_products (
                                id SERIAL PRIMARY KEY,
                                title TEXT,
                                average_rating FLOAT,
                                rating_number INT,
                                features TEXT[]
                                description TEXT,
                                price BIGINT,
                                images TEXT[],
                                store TEXT,
                                categories TEXT[],
                                details JSONB,
                                embedding VECTOR({self.embedding_dimension}) -- embedding vector dimension
                                UNIQUE(title, description, store) -- prevent duplicate items based on title, description, and store                           )
                           """
                         )

            cursor.execute("""
                            CREATE TABLE IF NOT EXISTS out_of_stock_products (
                                id SERIAL PRIMARY KEY,
                                title TEXT,
                                average_rating FLOAT,
                                rating_number INT,
                                features TEXT[]
                                description TEXT,
                                price BIGINT,
                                images TEXT[],
                                store TEXT,
                                categories TEXT[],
                                details JSONB,
                                embedding VECTOR({self.embedding_dimension}) -- embedding vector dimension
                                UNIQUE(title, description, store) -- prevent duplicate items based on title, description, and store                           )
                           """
                         )
            
            cursor.execute("""
                           CREATE INDEX IF NOT EXISTS avail_emb_cos_idx
                           ON in_stock_products USING ivfflat (embedding vector_cosine_ops)
                           """)
            
            cursor.execute("""
                           CREATE INDEX IF NOT EXISTS out_emb_cos_idx
                           ON out_of_stock_products USING ivfflat (embedding vector_cosine_ops)
                           """)
            
            self.conn.commit()
            self.logger.info("Database initialized successfully")
        
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            self.logger.error(f"Failed to initialize database: {e}")
            raise

        finally:
            if "cursor" in locals():
                cursor.close()

    def batch_insert_product(self, products_tuple: Tuple, table_name: str, batch_size: int = PRODUCT_BATCH_SIZE) -> None:
        """
        Insert products into the database.

        Args:
            products_tuple: Tuple of products to insert
            table_name: Name of the table to insert products into
            batch_size: Number of products to insert in each batch
        
        Raises:
            Exception: If failed to insert product
        """

        if not products_tuple:
            self.logger.warning("No products to insert")
            return
        
        try:
            if not self.conn:
                self.connect()

            cursor = self.conn.cursor()

            # On assumption that no product will have the same title, description, and store
            sql = f"""
                INSERT INTO {table_name} 
                    (title, average_rating, rating_number, features, 
                description, price, images, store, categories, details, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (title, description, store) DO NOTHING
            """

            for i in range(0, len(products_tuple), batch_size):
                chunk = products_tuple[i: i + batch_size]
                execute_values(cursor, sql, chunk)

            self.conn.commit()
            self.logger.info(f"Inserted {len(products_tuple)} products into {table_name}")

        except Exception as e:
            if self.conn:
                self.conn.rollback()
            self.logger.error(f"Failed to insert products: {e}")
            raise

        finally:
            if "cursor" in locals():
                cursor.close()

    def search_products(self, query_embedding: list[float], table_name: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for products in the database.

        Args:
            query_embedding: Embedding of the query
            table_name: Name of the table to search for products
            top_k: Number of products to return
        
        Returns:
            results: List of products that meet the similarity threshold

        Raises:
            Exception: If failed to search for products
        """
        try:
            if not self.conn:
                self.connect()

            cursor = self.conn.cursor()

            embedding_str = str(query_embedding)
            embedding_array = f"ARRAY{embedding_str}::vector({self.embedding_dimension})"

            sql = f"""
                SELECT
                    title,
                    average_rating,
                    rating_number,
                    features,
                    description,
                    price,
                    images,
                    store,
                    categories,
                    details,
                    1 - (embedding <=> {embedding_array}) AS similarity
                FROM 
                    {table_name}
                ORDER BY
                    embedding <=> {embedding_array}
                LIMIT 
                    {top_k};
            """

            cursor.execute(sql)

            results = []
            for row in cursor.fetchall():
                title, average_rating, rating_number, features, description, price, images, store, categories, details_json, similarity = row

                if details_json:
                    if isinstance(details_json, str):
                        details = json.loads(details_json)
                    else:
                        details = {}
                else:
                    details = {}

                # Only append results that meet the similarity threshold
                if similarity > SEARCH_SIMILARITY_THRESHOLD:
                    results.append({
                        "title": title,
                        "average_rating": average_rating,
                        "rating_number": rating_number,
                        "features": features,
                        "description": description,
                        "price": price,
                        "images": images,
                        "store": store,
                        "categories": categories,
                        "details": details,
                        "similarity": similarity
                    })

                self.logger.info(f"{len(results)} products found.")
                return results
    

        except Exception as e:
            self.logger.error(f"Failed to search products: {e}")
            raise

        finally:
            if "cursor" in locals():
                cursor.close()
    

    def load_products(self, df_product: pd.DataFrame, table_name: str) -> None:
        """
        Load products into the database.

        Args:
            df_product: DataFrame containing products
            table_name: Name of the table to insert products into
            vector_db: VectorDatabase instance for database operations

        Raises:
            Exception: If failed to load products
        """
        try:
            if not df_product:
                self.logger.warning("No products to insert")
                return

            insert_columns = PRODUCT_DB_COLUMNS
            assert all(col in df_product.columns for col in insert_columns), "Missing required columns"

            df_product["embedding"] = df_product.apply(lambda x: embedding(
                f"Title: {x['title']}, Description: {x['description']}, Details: {x['details']}"), axis=1)
            
            df_product_available = df_product[df_product["status"] == "in_stock"]
            df_product_unavailable = df_product[df_product["status"] == "out_of_stock"]

            # Convert the available products dataframe to a list of tuples for insertion
            insertion_rows_available = [
                tuple(row[col] for col in insert_columns)
                for _, row in df_product_available.iterrows()
            ]

            # Convert the unavailable products dataframe to a list of tuples for insertion
            insertion_rows_unavailable = [
                tuple(row[col] for col in insert_columns)
                for _, row in df_product_unavailable.iterrows()
            ]

            if not df_product_available.empty:
                self.logger.info(f"Inserting {len(insertion_rows_available)} in stock products into {IN_STOCK_PRODUCTS_TABLE_NAME}")
                self.batch_insert_product(insertion_rows_available, IN_STOCK_PRODUCTS_TABLE_NAME, PRODUCT_BATCH_SIZE)

            if not df_product_unavailable.empty:
                self.logger.info(f"Inserting {len(insertion_rows_unavailable)} out of stock products into {OUT_OF_STOCK_PRODUCTS_TABLE_NAME}")
                self.batch_insert_product(insertion_rows_unavailable, OUT_OF_STOCK_PRODUCTS_TABLE_NAME, PRODUCT_BATCH_SIZE)
            
            self.logger.info(f"Inserted {len(df_product)} products into {table_name}")

        except Exception as e:
            self.logger.error(f"Failed to load products: {e}")
            raise    

            






