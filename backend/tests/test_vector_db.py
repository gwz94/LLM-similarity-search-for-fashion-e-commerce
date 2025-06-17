import pytest
import os
import json
import pandas as pd
from unittest.mock import Mock, patch
from app.database.vector_db import VectorDatabase
from app.config.settings import (
    IN_STOCK_PRODUCTS_TABLE_NAME,
    OUT_OF_STOCK_PRODUCTS_TABLE_NAME,
    SEARCH_SIMILARITY_THRESHOLD,
)

# Test data
MOCK_CONNECTION_PARAMS = {
    "host": "127.0.0.1",
    "port": 5432,
    "user": "test_user",
    "password": "test_password",
}

MOCK_PRODUCT_DATA = {
    "title": "Test Product",
    "average_rating": 4.5,
    "rating_number": 100,
    "features": ["feature1", "feature2"],
    "description": "Test description",
    "price": 99.99,
    "images": [{"url": "test.jpg"}],
    "store": "Test Store",
    "categories": "Test Category",
    "details": {"color": "red"},
    "embedding": [0.1] * 1536,  # Mock embedding vector with correct dimension
}


@pytest.fixture
def vector_db():
    """Fixture to create a VectorDatabase instance for testing"""
    with patch("psycopg.connect") as mock_connect:
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        db = VectorDatabase(MOCK_CONNECTION_PARAMS)
        db.conn = mock_conn
        yield db


def test_init(vector_db):
    """Test VectorDatabase initialization"""
    assert vector_db.connection_params == MOCK_CONNECTION_PARAMS
    assert vector_db.conn is not None


def test_connect(vector_db):
    """Test database connection"""
    # Reset the mock to ensure clean state
    vector_db.conn.cursor.reset_mock()
    vector_db.connect()
    vector_db.conn.cursor.assert_called_once()


def test_disconnect(vector_db):
    """Test database disconnection"""
    # Ensure connection exists before disconnecting
    if vector_db.conn is None:
        vector_db.connect()
    # Store the connection before disconnecting
    conn = vector_db.conn
    vector_db.disconnect()
    conn.close.assert_called_once()
    assert vector_db.conn is None


def test_initialize_database(vector_db):
    """Test database initialization"""
    mock_cursor = Mock()
    vector_db.conn.cursor.return_value = mock_cursor

    vector_db.initialize_database()

    # Verify that the necessary SQL commands were executed
    assert (
        mock_cursor.execute.call_count >= 4
    )  # At least 4 SQL commands should be executed
    mock_cursor.execute.assert_any_call("CREATE EXTENSION IF NOT EXISTS vector;")
    mock_cursor.execute.assert_any_call("DROP TABLE IF EXISTS in_stock_products")
    mock_cursor.execute.assert_any_call("DROP TABLE IF EXISTS out_of_stock_products")


def test_search_products(vector_db):
    """Test product search functionality"""
    # Mock cursor and its fetchall result
    mock_cursor = Mock()
    vector_db.conn.cursor.return_value = mock_cursor

    # Mock search results
    mock_results = [
        (
            MOCK_PRODUCT_DATA["title"],
            MOCK_PRODUCT_DATA["average_rating"],
            MOCK_PRODUCT_DATA["rating_number"],
            MOCK_PRODUCT_DATA["features"],
            MOCK_PRODUCT_DATA["description"],
            MOCK_PRODUCT_DATA["price"],
            MOCK_PRODUCT_DATA["images"],
            MOCK_PRODUCT_DATA["store"],
            MOCK_PRODUCT_DATA["categories"],
            json.dumps(MOCK_PRODUCT_DATA["details"]),
            0.8,  # Mock similarity score
        )
    ]
    mock_cursor.fetchall.return_value = mock_results

    # Test search with 1536-dimensional vector
    query_embedding = [0.1] * 1536
    results = vector_db.search_products(
        query_embedding, IN_STOCK_PRODUCTS_TABLE_NAME, top_k=10
    )

    # Verify results
    assert len(results) > 0
    assert results[0]["title"] == MOCK_PRODUCT_DATA["title"]
    assert results[0]["similarity"] >= SEARCH_SIMILARITY_THRESHOLD


def test_batch_insert_product(vector_db):
    """Test batch product insertion"""
    mock_cursor = Mock()
    vector_db.conn.cursor.return_value = mock_cursor

    # Create test data with 1536-dimensional vector
    test_products = [
        (
            MOCK_PRODUCT_DATA["title"],
            MOCK_PRODUCT_DATA["average_rating"],
            MOCK_PRODUCT_DATA["rating_number"],
            json.dumps(MOCK_PRODUCT_DATA["features"]),
            MOCK_PRODUCT_DATA["description"],
            MOCK_PRODUCT_DATA["price"],
            json.dumps(MOCK_PRODUCT_DATA["images"]),
            MOCK_PRODUCT_DATA["store"],
            MOCK_PRODUCT_DATA["categories"],
            json.dumps(MOCK_PRODUCT_DATA["details"]),
            MOCK_PRODUCT_DATA["embedding"],
        )
    ]

    # Test insertion
    vector_db.batch_insert_product(
        test_products, IN_STOCK_PRODUCTS_TABLE_NAME, batch_size=1
    )

    # Verify that executemany was called
    mock_cursor.executemany.assert_called_once()
    vector_db.conn.commit.assert_called_once()


def test_insert_products_information(vector_db):
    """Test product information insertion"""
    # Create test DataFrame with 1536-dimensional vector
    df = pd.DataFrame([{**MOCK_PRODUCT_DATA, "inventory_status": "in_stock"}])

    # Mock batch_insert_product
    with patch.object(vector_db, "batch_insert_product") as mock_batch_insert:
        vector_db.insert_products_information(df, IN_STOCK_PRODUCTS_TABLE_NAME)
        mock_batch_insert.assert_called_once()


def test_error_handling(vector_db):
    """Test error handling in database operations"""
    # Test connection error
    vector_db.conn = None  # Reset connection
    with patch("psycopg.connect", side_effect=Exception("Connection error")):
        with pytest.raises(Exception):
            vector_db.connect()

    # Test search error
    vector_db.conn = Mock()  # Reset connection
    vector_db.conn.cursor.side_effect = Exception("Search error")
    with pytest.raises(Exception):
        vector_db.search_products([0.1] * 1536, IN_STOCK_PRODUCTS_TABLE_NAME)
