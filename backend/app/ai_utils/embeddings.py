from app.utils.logger import setup_logger
import os
import numpy as np
from typing import List
import multiprocessing
from app.clients import get_openai_client

from app.config.settings import Settings

settings = Settings()

logger = setup_logger("embeddings")
client = get_openai_client()

def get_embedding(text: str) -> list[float]:
    """
    Embed a text string into a vector of floats.

    Args:
        text (str): The text to embed

    Returns:
        list[float]: The embedding of the text
    """
    try:
        logger.info("Generating embedding for text", extra={
            "text_length": len(text),
            "model": settings.EMBEDDING_MODEL_NAME
        })

        response = client.embeddings.create(model=settings.EMBEDDING_MODEL_NAME, input=text)
        embedding = np.array(response.data[0].embedding, dtype=np.float32).tolist()

        logger.info("Embedding generated successfully", extra={
            "embedding_length": len(embedding)
        })

        return embedding

    except Exception as e:
        logger.error("Failed to generate embedding", extra={
            "error": str(e),
            "error_type": type(e).__name__,
            "text_length": len(text)
        })
        raise

def batch_embedding(texts: list[str]) -> list[list[float]]:
    """
    Embed a list of text strings into a list of vectors of floats.

    Args:
        texts (list[str]): List of text strings to embed

    Returns:
        list[list[float]]: List of embeddings
    """
    try:
        logger.info("Starting batch embedding", extra={
            "batch_size": len(texts),
            "model": settings.EMBEDDING_MODEL_NAME
        })

        response = client.embeddings.create(model=settings.EMBEDDING_MODEL_NAME, input=texts)
        embeddings = [np.array(obj.embedding).tolist() for obj in response.data]

        logger.info("Batch embedding completed", extra={
            "input_size": len(texts),
            "output_size": len(embeddings)
        })

        return embeddings

    except Exception as e:
        logger.error("Batch embedding failed", extra={
            "error": str(e),
            "error_type": type(e).__name__,
            "batch_size": len(texts)
        })
        raise

def get_embeddings_batch(texts: List[str], batch_size: int = 100) -> List[List[float]]:
    """
    Get embeddings for a batch of texts using multiprocessing

    Args:
        texts (List[str]): List of text strings to embed
        batch_size (int): Batch size for embedding

    Returns:
        List[List[float]]: List of embeddings
    """
    try:
        logger.info("Starting multiprocessing batch embedding", extra={
            "total_texts": len(texts),
            "batch_size": batch_size,
            "num_batches": (len(texts) + batch_size - 1) // batch_size
        })

        with multiprocessing.Pool() as pool:
            results = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                logger.info("Processing batch", extra={
                    "batch_number": i // batch_size + 1,
                    "batch_size": len(batch)
                })
                
                batch_results = pool.map(get_embedding, batch)
                results.extend(batch_results)

        logger.info("Multiprocessing batch embedding completed", extra={
            "total_processed": len(results)
        })

        return results

    except Exception as e:
        logger.error("Multiprocessing batch embedding failed", extra={
            "error": str(e),
            "error_type": type(e).__name__,
            "total_texts": len(texts)
        })
        raise