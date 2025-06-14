import os, json
import multiprocessing
from typing import List

import numpy as np

from dotenv import load_dotenv
from app.clients import get_openai_client

load_dotenv()
client = get_openai_client()

def get_embedding(text: str) -> list[float]:
    """
    Embed a text string into a vector of floats.

    Args:
        text (str): The text to embed.

    Returns:
        List[float]: The embedding of the text.
    """
    EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")
    return np.array(
        client.embeddings.create(model=EMBEDDING_MODEL_NAME, input=text
                                 ).data[0].embedding, dtype=np.float32
    ).tolist()

def batch_embedding(texts: list[str]) -> list[list[float]]:
    """
    Embed a list of text strings into a list of vectors of floats.

    Args:
        texts (list[str]): The list of text strings to embed.

    Returns:
        list[list[float]]: The list of embeddings.
    """

    EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")
    response = client.embeddings.create(model=EMBEDDING_MODEL_NAME, input=texts)

    return [np.array(obj.embedding).tolist() for obj in response.data]

def get_embeddings_batch(texts: List[str], batch_size: int = 100) -> List[List[float]]:
    """Get embeddings for a batch of texts using multiprocessing"""
    with multiprocessing.Pool() as pool:
        # Process texts in batches
        results = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_results = pool.map(get_embedding, batch)
            results.extend(batch_results)
        return results


