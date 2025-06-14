import os
import logging

import pandas as pd
import numpy as np

from app.preprocessing.data_preprocessing_util import data_preprocessing, image_feature_extraction, products_description_embedding 

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess the dataset to handle missing values or values with only space.
    Drop products with price below 0.05.
    Embedding the title, description, details of the product.
    Extract feature from image if title is missing.

    Args:
        df: DataFrame containing products

    Returns:
        df: Preprocessed DataFrame
    """
    logger.info(f"Preprocessing {len(df)} products")

    logger.info("Starting data preprocessing...")
    df = data_preprocessing(df)
    logger.info(f"Data preprocessing completed with {len(df)} products")

    # Generate embeddings for title, description, features, details
    df = products_description_embedding(df)

    # Extract feature from image if title is missing
    # Prechecked that every products has large image url in the images column
    mask = df["title"].isna()
    df.loc[mask, "title"] = df.loc[mask, "images"].apply(
        lambda x: image_feature_extraction(x[0]["large"]) if x and len(x) > 0 and "large" in x[0] else None
    )
    logger.info(f"Image feature extraction completed with {len(df)} products")

    return df