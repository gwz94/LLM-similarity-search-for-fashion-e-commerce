import pandas as pd
from tqdm import tqdm

from app.ai_utils.embeddings import batch_embedding
from app.config.settings import Settings
from app.utils.logger import setup_logger

logger = setup_logger("embedding_generation")

settings = Settings()

def products_description_embedding(
    df: pd.DataFrame, batch_size: int = settings.PRODUCT_EMBEDDING_BATCH_SIZE
) -> pd.DataFrame:
    """
    Embeds product title and descriptions. 
    Loads embeddings back into DataFrame.

    Args:
        df (pd.DataFrame): DataFrame containing products
        batch_size (int): Batch size for embedding products description

    Returns:
        df (pd.DataFrame): DataFrame with embedding column
    """
    logger.info("Starting embedding process", extra={"num_products": len(df)})

    embeddings_texts = df.apply(
        lambda x: f"Title: {x['title']}, Description: {x['description']}", axis=1
    ).to_list()

    all_embeddings = []
    for i in tqdm(
        range(0, len(embeddings_texts), batch_size),
        total=(len(embeddings_texts) + batch_size - 1) // batch_size,
        desc="Generating embeddings",
    ):
        batch = embeddings_texts[i : i + batch_size]
        batch_embeddings = batch_embedding(batch)
        all_embeddings.extend(batch_embeddings)

    df["embedding"] = all_embeddings

    logger.info("Embedding process completed", extra={"num_products": len(df)})
    return df
