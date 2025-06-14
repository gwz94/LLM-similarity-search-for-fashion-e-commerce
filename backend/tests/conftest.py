import pytest
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
backend_dir = str(Path(__file__).parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Set test environment variables
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DB_USER"] = "postgres"
os.environ["DB_PASSWORD"] = "postgres"
os.environ["DB_NAME"] = "fashion_ecommerce_test"
os.environ["EMBEDDING_DIMENSION"] = "1536"  # Set to match production dimension

# Load environment variables for testing
@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables"""
    os.environ["EMBEDDING_DIMENSION"] = "1536"  # Small dimension for testing
    os.environ["DB_HOST"] = "localhost"
    os.environ["DB_PORT"] = "5432"
    os.environ["DB_USER"] = "postgres"
    os.environ["DB_PASSWORD"] = "postgres"
    os.environ["DB_NAME"] = "fashion_ecommerce_test"
    yield 