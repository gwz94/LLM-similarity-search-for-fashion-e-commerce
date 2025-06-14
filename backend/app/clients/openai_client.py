import os
import logging

from functools import lru_cache
from openai import OpenAI
from dotenv import load_dotenv

@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    """
    Initialize the OpenAI client and save it in the cache.
    """
    load_dotenv()
    client = OpenAI()
    return client