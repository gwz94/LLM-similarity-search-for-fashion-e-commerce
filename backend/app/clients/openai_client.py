from functools import lru_cache
from openai import OpenAI
from app.config.settings import get_settings


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    """
    Initialize the OpenAI client and save it in the cache.

    Returns:
        OpenAI: The OpenAI client.
    """
    settings = get_settings()
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return client
