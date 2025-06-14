import os
import logging
import time

import pandas as pd
import numpy as np
from tqdm import tqdm

from app.clients import get_openai_client
from app.config import IMAGE_FEATURE_EXTRACTION_MODEL, PRODUCT_EMBEDDING_BATCH_SIZE
from app.ai_utils import get_embedding, batch_embedding


logger = logging.getLogger("dataset_preprocessing")
logger.setLevel(logging.INFO)

def data_preprocessing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess the dataset to handle missing values or values with only space.
    Handle inventory status, product with price is in stock, otherwise out of stock.
    Handle discontinued products, out of stock with is_discontinues is yes will be labeled as discontinued.
    Drop products with price below 0.05.

    Args:
        df: DataFrame containing products information

    Returns:
        df: Preprocessed DataFrame
    """
    initial_count = len(df)
    logger.info(f"Starting data preprocessing with {initial_count} products")

    # Handle missing values or values with only space
    logger.info("Handling missing values and empty strings...")
    for column in df.columns:
        df[column] = df[column].apply(
            lambda x: np.nan
            if (
                (isinstance(x, list) and len(x) == 0)  # To handle empty lists
                or (isinstance(x, str) and x.strip() == "")  # To handle empty cell with only space
            )
            else x
        )
    # In order to insert data into the database, convert np.nan to None
    df['features'] = df['features'].where(pd.notnull(df['features']), None)

    # Handle inventory status, product with price is in stock, otherwise out of stock
    logger.info("Setting inventory status based on price...")
    df["inventory_status"] = df["price"].apply(
        lambda x: "in_stock" if pd.notnull(x) else "out_of_stock"
    )
    in_stock_count = (df["inventory_status"] == "in_stock").sum()
    out_of_stock_count = (df["inventory_status"] == "out_of_stock").sum()
    logger.info(f"Inventory status: {in_stock_count} in stock, {out_of_stock_count} out of stock")

    # Handle discontinued products(product that has no price and labeled as discontinued in details)
    logger.info("Checking for out of stock and discontinued products...")
    mask = (
        (df["inventory_status"] == "out_of_stock") &
        (df["details"].apply(lambda d: isinstance(d, dict) and (d.get("is_discontinued") == "Yes" 
                                                                or d.get("is_discontinued") == "True")))
    )
    out_of_stock_and_discontinued_count = mask.sum()
    df.loc[mask, "inventory_status"] = "out of stock and discontinued"
    logger.info(f"Found {out_of_stock_and_discontinued_count} out of stock and discontinued products")

    # Remove products that are both out of stock and discontinued
    df = df[~(df["inventory_status"] == "out of stock and discontinued")]
    logger.info(f"Removed products that are both out of stock and discontinued")

    # Count products with very low prices
    low_price_count = (df["price"] <= 0.05).sum()
    # Keep products that either have no price (NaN) or have price > 0.05
    df = df[(df["price"].isna()) | (df["price"] > 0.05)]
    logger.info(f"Removed {low_price_count} products with price below 0.05")

    final_count = len(df)
    logger.info(f"Data preprocessing completed. {final_count} products remaining (removed {initial_count - final_count} products)")

    return df

def image_feature_extraction(img_url: str) -> str:
    """
    Extract feature(title) from image using OpenAI vision model.

    Args:
        img_url: URL of the image to extract feature from

    Returns:
        str: The extracted feature(title) from the image
    
    Raises:
        Exception: If failed to extract feature from the image
    """

    system_prompt = """
        You are an assistant that tags fashion product images
        and generates detailed and accurate titles suitable for e-commerce listings.        
    """
    
    task_prompt = """
        Generate a detailed product title for this fashion item.
        Pay attention to the brand and state clear categories for the product.
        Be more descriptive for the product to be promoted on e-commerce platform. 

        ## Output format
        - return the answer in JSON object format (do not include ''')

        ## Exampe output
        {
            "title": "Product Title"
        }   
    """

    try:

        client = get_openai_client()

        logger.info(f"Extracting feature from image: {img_url}")

        response = client.responses.create(
            model=IMAGE_FEATURE_EXTRACTION_MODEL,
            input = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": task_prompt
                        },
                        {
                            "type": "input_image",
                            "image_url": img_url
                        }
                    ]
                }

            ]
        )
        
        logger.info(f"Successfully extracted feature from image: {img_url}")

        return response.output_text
    
    except Exception as e:
        logger.error(f"Error in image_feature_extraction for image: {img_url} - {e}")
        return None


def products_description_embedding(df: pd.DataFrame, batch_size: int = PRODUCT_EMBEDDING_BATCH_SIZE,) -> pd.DataFrame:
    """
    Embedding the title, description, features, details of the product.

    Args:
        df: DataFrame containing products
        batch_size: Batch size for embedding products description

    Returns:
        df: DataFrame with embedding column
    """
    logger.info(f"Starting embedding process for {len(df)} products")
    
    embeddings_texts = df.apply(
        lambda x: f"Title: {x['title']}, Description: {x['description']}",
        axis=1
    ).to_list()

    all_embeddings = []
    for i in tqdm(range(0, len(embeddings_texts), PRODUCT_EMBEDDING_BATCH_SIZE), total=len(embeddings_texts) // PRODUCT_EMBEDDING_BATCH_SIZE, desc="Generating embeddings"):
        batch = embeddings_texts[i : i + PRODUCT_EMBEDDING_BATCH_SIZE]
        batch_embeddings = batch_embedding(batch)
        all_embeddings.extend(batch_embeddings)
        if i % 100 == 0:
            time.sleep(300) # to prevent memory leak error

    df["embedding"] = all_embeddings
    
    logger.info("Embedding process completed")
    return df