import os
from typing import Annotated

from fastapi import Depends
from app.database.vector_db import VectorDatabase
from app.config.settings import Settings

settings = Settings()


def get_db():
    """Dependency to get database connection"""
    connection_params = {
        "host": settings.DB_HOST,
        "port": settings.DB_PORT,
        "user": settings.DB_USER,
        "password": settings.DB_PASSWORD,
        "dbname": settings.DB_NAME,
    }
    db = VectorDatabase(connection_params)
    try:
        db.connect()
        yield db
    finally:
        db.disconnect()


# Type alias for dependency injection
DB = Annotated[VectorDatabase, Depends(get_db)]
