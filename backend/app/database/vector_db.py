import os
import logging
import json
import math

import pandas as pd
import psycopg

from dotenv import load_dotenv
from app.ai_utils import get_embedding
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
            self.conn = psycopg.connect(**self.connection_params)
            self.conn.cursor()
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
                self.connect()

            cursor = self.conn.cursor()

            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")

            cursor.execute("DROP TABLE IF EXISTS in_stock_products")
            cursor.execute("DROP TABLE IF EXISTS out_of_stock_products")

            cursor.execute(f"""
                            CREATE TABLE IF NOT EXISTS in_stock_products (
                                id              BIGSERIAL PRIMARY KEY,          
                                title           TEXT        NOT NULL,
                                average_rating  REAL,
                                rating_number   INTEGER,
                                features        JSONB,                          
                                description     TEXT,
                                price           NUMERIC,                        
                                images          JSONB,                          
                                store           TEXT,
                                categories      TEXT,                          
                                details         JSONB,                          
                                embedding       VECTOR({self.embedding_dimension}),  -- pgvector column
                                unique_hash     TEXT GENERATED ALWAYS AS (MD5(title || description || store)) STORED,
                                UNIQUE (unique_hash) -- Use unique_hash to prevent duplicate products
                            );
                           """
                         )

            cursor.execute(f"""
                            CREATE TABLE IF NOT EXISTS out_of_stock_products (
                                id              BIGSERIAL PRIMARY KEY,          
                                title           TEXT        NOT NULL,
                                average_rating  REAL,
                                rating_number   INTEGER,
                                features        JSONB,                          
                                description     TEXT,
                                price           NUMERIC,                        
                                images          JSONB,                          
                                store           TEXT,
                                categories      TEXT,                          
                                details         JSONB,                          
                                embedding       VECTOR({self.embedding_dimension}),  -- pgvector column
                                unique_hash     TEXT GENERATED ALWAYS AS (MD5(title || description || store)) STORED,
                                UNIQUE (unique_hash) -- Use unique_hash to prevent duplicate products
                            );
                           """
                         )
            
            # Create indexes using ivfflat index to speed up cosine similarity search
            cursor.execute("""
                           CREATE INDEX IF NOT EXISTS in_stock_emb_cos_idx
                           ON in_stock_products USING ivfflat (embedding vector_cosine_ops)
                           """)

            # Create indexes using ivfflat index to speed up cosine similarity search
            cursor.execute("""
                           CREATE INDEX IF NOT EXISTS out_of_stock_emb_cos_idx
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
            sql = """
                INSERT INTO {table}
                    (title, average_rating, rating_number, features,
                    description, price, images, store, categories,
                    details, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (unique_hash) DO NOTHING
            """.format(table=table_name)

            for i in range(0, len(products_tuple), batch_size):
                chunk = products_tuple[i: i + batch_size]
                cursor.executemany(sql, chunk)
                self.conn.commit()
                self.logger.info(f"Inserted batch of {len(chunk)} products into {table_name}")

            self.logger.info(f"Successfully inserted {len(products_tuple)} products into {table_name}")

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
                    id,
                    title,
                    average_rating,
                    rating_number,
                    features,
                    description,
                    price::float,  -- Convert price to float
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
                id, title, average_rating, rating_number, features, description, price, images, store, categories, details_json, similarity = row

                if details_json:
                    if isinstance(details_json, str):
                        details = json.loads(details_json)
                    else:
                        details = {}
                else:
                    details = {}

                # Handle NaN values by converting them to None
                def safe_float(value):
                    try:
                        if value is None or (isinstance(value, float) and math.isnan(value)):
                            return None
                        return float(value)
                    except (ValueError, TypeError):
                        return None

                def safe_int(value):
                    try:
                        if value is None or (isinstance(value, float) and math.isnan(value)):
                            return None
                        return int(value)
                    except (ValueError, TypeError):
                        return None

                results.append({
                    "id": id,
                    "title": title,
                    "average_rating": safe_float(average_rating),
                    "rating_number": safe_int(rating_number),
                    "features": features,
                    "description": description,
                    "price": safe_float(price),
                    "images": images,
                    "store": store,
                    "categories": categories,
                    "details": details,
                    "similarity": safe_float(similarity)
                })

            self.logger.info(f"{len(results)} products found from {table_name}.")
            return results
    

        except Exception as e:
            self.logger.error(f"Failed to search products: {e}")
            raise

        finally:
            if "cursor" in locals():
                cursor.close()
    

    def insert_products_information(self, df_product: pd.DataFrame) -> None:
        """
        insert products information into the database.

        Args:
            df_product: DataFrame containing products

        Raises:
            Exception: If failed to load products
        """
        try:
            if df_product.empty:
                self.logger.warning("No products information to insert")
                return

            insert_columns = PRODUCT_DB_COLUMNS
            self.logger.info(f"Checking required columns: {insert_columns}")
            self.logger.info(f"Available columns: {df_product.columns.tolist()}")
            
            missing_columns = [col for col in insert_columns if col not in df_product.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            df_product_available = df_product[df_product["inventory_status"] == "in_stock"]
            df_product_unavailable = df_product[df_product["inventory_status"] == "out_of_stock"]

            insertion_rows_available = []
            for _, row in df_product_available.iterrows():
                insertion_rows_available.append(tuple(
                    json.dumps(row[col]) if isinstance(row[col], (dict, list)) else row[col]
                    for col in insert_columns
                ))
            
            insertion_rows_unavailable = []
            for _, row in df_product_unavailable.iterrows():
                insertion_rows_unavailable.append(tuple(
                    json.dumps(row[col]) if isinstance(row[col], (dict, list)) else row[col]
                    for col in insert_columns
                ))
                
            if not df_product_available.empty:
                self.logger.info(f"Inserting {len(insertion_rows_available)} in stock products into {IN_STOCK_PRODUCTS_TABLE_NAME}")
                self.batch_insert_product(insertion_rows_available, IN_STOCK_PRODUCTS_TABLE_NAME, PRODUCT_BATCH_SIZE)

            if not df_product_unavailable.empty:
                self.logger.info(f"Inserting {len(insertion_rows_unavailable)} out of stock products into {OUT_OF_STOCK_PRODUCTS_TABLE_NAME}")
                self.batch_insert_product(insertion_rows_unavailable, OUT_OF_STOCK_PRODUCTS_TABLE_NAME, PRODUCT_BATCH_SIZE)
            
            self.logger.info(f"Successfully inserted {len(df_product)} products into database")

        except Exception as e:
            self.logger.error(f"Failed to insert products information into the database: {e}")
            raise    

            






