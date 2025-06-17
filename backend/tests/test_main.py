import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json

from app.main import app, SearchQuery
from app.database.vector_db import VectorDatabase

# Create a test client
client = TestClient(app)

# Mock data for testing
MOCK_IN_STOCK_RESULTS = [
    {
        "title": "Test In Stock Product",
        "average_rating": 4.5,
        "rating_number": 100,
        "features": {"color": "blue"},
        "description": "A test product",
        "price": 29.99,
        "images": ["image1.jpg"],
        "store": "Test Store",
        "categories": "Clothing",
        "details": {"size": "M"},
        "similarity": 0.85,
    }
]

MOCK_OUT_OF_STOCK_RESULTS = [
    {
        "title": "Test Out of Stock Product",
        "average_rating": 4.0,
        "rating_number": 50,
        "features": {"color": "red"},
        "description": "Another test product",
        "price": 39.99,
        "images": ["image2.jpg"],
        "store": "Test Store",
        "categories": "Clothing",
        "details": {"size": "L"},
        "similarity": 0.75,
    }
]

MOCK_RERANKED_RESULTS = [
    {
        "title": "Test In Stock Product",
        "average_rating": 4.5,
        "rating_number": 100,
        "features": {"color": "blue"},
        "description": "A test product",
        "price": 29.99,
        "images": ["image1.jpg"],
        "store": "Test Store",
        "categories": "Clothing",
        "details": {"size": "M"},
        "similarity": 0.85,
        "stock_status": "in_stock",
    }
]


@pytest.fixture
def mock_db():
    """Fixture to create a mock database"""
    with patch("app.main.VectorDatabase") as mock:
        db_instance = Mock(spec=VectorDatabase)
        mock.return_value = db_instance
        yield db_instance


@pytest.fixture
def mock_embedding():
    """Fixture to mock the embedding function"""
    with patch("app.main.get_embedding") as mock:
        # Create a mock embedding vector with 1536 dimensions
        mock.return_value = [0.1] * 1536  # Mock embedding vector with correct dimension
        yield mock


@pytest.fixture
def mock_reranker():
    """Fixture to mock the reranker function"""
    with patch("app.main.rerank_search_results") as mock:
        mock.return_value = MOCK_RERANKED_RESULTS
        yield mock


def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_search_products_success(mock_db, mock_embedding, mock_reranker):
    """Test successful product search"""
    # Configure mock database
    mock_db.search_products.side_effect = [
        MOCK_IN_STOCK_RESULTS,
        MOCK_OUT_OF_STOCK_RESULTS,
    ]

    # Test data
    test_query = {
        "query": "test query",
        "limit": 5,
        "out_of_stock_products_recommendation": True,
    }

    # Make request
    response = client.post("/search", json=test_query)

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "recommended_products" in data
    assert len(data["recommended_products"]) > 0

    # Verify mock calls
    mock_embedding.assert_called_once_with(test_query["query"])
    assert mock_db.search_products.call_count == 2
    mock_reranker.assert_called_once()


def test_search_products_invalid_query():
    """Test search with invalid query"""
    # Test with empty query
    response = client.post("/search", json={"query": ""})
    assert response.status_code == 422  # Validation error

    # Test with query containing invalid characters
    response = client.post(
        "/search", json={"query": "test<script>alert('xss')</script>"}
    )
    assert response.status_code == 422


def test_search_products_database_error(mock_db, mock_embedding):
    """Test search when database throws an error"""
    # Configure mock to raise an exception
    mock_db.search_products.side_effect = Exception("Database error")

    # Make request
    response = client.post("/search", json={"query": "test query"})

    # Assertions
    assert response.status_code == 500
    assert "Error processing search request" in response.json()["detail"]


def test_search_products_without_optional_params():
    """Test search with only required parameters"""
    response = client.post("/search", json={"query": "test query"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "recommended_products" in data


def test_search_products_with_custom_limit(mock_db, mock_embedding, mock_reranker):
    """Test search with custom limit"""
    # Configure mock database
    mock_db.search_products.side_effect = [
        MOCK_IN_STOCK_RESULTS,
        MOCK_OUT_OF_STOCK_RESULTS,
    ]

    # Test with custom limit
    response = client.post("/search", json={"query": "test query", "limit": 10})

    assert response.status_code == 200
    # Verify that the limit was passed to search_products
    assert mock_db.search_products.call_args[1]["top_k"] == 10
