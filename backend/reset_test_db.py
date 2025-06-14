import os
import psycopg
from dotenv import load_dotenv

def reset_test_database():
    """Reset the test database by dropping and recreating tables"""
    # Load environment variables
    load_dotenv()
    
    # Set up connection parameters
    connection_params = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", 5432),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "postgres"),
        # "dbname": os.getenv("DB_NAME", "fashion_ecommerce_test")
    }
    
    try:
        # Connect to the database
        with psycopg.connect(**connection_params) as conn:
            with conn.cursor() as cur:
                # Drop existing tables
                cur.execute("DROP TABLE IF EXISTS in_stock_products CASCADE;")
                cur.execute("DROP TABLE IF EXISTS out_of_stock_products CASCADE;")
                
                # Create extension if not exists
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                
                # Create tables with correct vector dimension
                cur.execute("""
                    CREATE TABLE in_stock_products (
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
                        embedding       VECTOR(1536),  -- pgvector column
                        UNIQUE (title, description, store)
                    );
                """)
                
                cur.execute("""
                    CREATE TABLE out_of_stock_products (
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
                        embedding       VECTOR(1536),  -- pgvector column
                        UNIQUE (title, description, store)
                    );
                """)
                
                # Create indexes
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS in_stock_emb_cos_idx
                    ON in_stock_products USING ivfflat (embedding vector_cosine_ops)
                """)
                
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS out_of_stock_emb_cos_idx
                    ON out_of_stock_products USING ivfflat (embedding vector_cosine_ops)
                """)
                
                conn.commit()
                print("Test database reset successfully!")
                
    except Exception as e:
        print(f"Error resetting test database: {e}")
        raise

if __name__ == "__main__":
    reset_test_database() 