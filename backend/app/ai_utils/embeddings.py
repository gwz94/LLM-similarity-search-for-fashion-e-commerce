import os, json
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def embedding(text: str) -> np.array[float]:
    """
    Embed a text string into a vector of floats.

    Args:
        text (str): The text to embed.

    Returns:
        np.array[float]: The embedding of the text.
    """
    EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")
    return np.array(
        client.embeddings.create(model=EMBEDDING_MODEL_NAME, input=text
                                 ).data[0].embedding, dtype=np.float32
    )
