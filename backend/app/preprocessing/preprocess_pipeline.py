import logging
import json

import pandas as pd

from app.preprocessing.data_cleaning import data_cleaning
from app.preprocessing.embedding_generation import products_description_embedding
from app.preprocessing.product_image_feature_extraction import product_image_feature_extraction, product_image_title_extraction

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)



def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess the dataset to handle missing values or values with only space.
    Drop products with price below 0.05.
    Embedding the title, description, details of the product.
    Extract feature from image if title is missing.

    Args:
        df (pd.DataFrame): DataFrame containing products

    Returns:
        df (pd.DataFrame): Preprocessed DataFrame
    """
    logger.info(f"Preprocessing {len(df)} products")

    logger.info("Starting data preprocessing...")
    df = data_cleaning(df)
    logger.info(f"Data preprocessing completed with {len(df)} products")

    # Generate embeddings for title, description, features, details
    df = products_description_embedding(df)

    # Extract title from image if title is missing
    # NOTE: Alaredy prechecked that every products has large image url in the images column
    mask = df["title"].isna()
    df.loc[mask, "title"] = df.loc[mask, "images"].apply(
        lambda x: product_image_title_extraction(x[0]["large"])
        if x and len(x) > 0 and "large" in x[0]
        else None
    )

    # Extract extra features from image for product that are in stock(with price value)
    # NOTE: This process of extracting features took more than 6 hours to complete. Thus will be removed for now.
    # mask = pd.notnull(df["price"])

    # llm_outputs = []
    # for image_url in df.loc[mask, "images"]:
    #     output = product_image_feature_extraction(image_url[0]["large"])
    #     llm_outputs.append(output)

    # df = update_products_details(df, llm_outputs)

    # logger.info(f"Image feature extraction completed with {len(df)} products")
    # Drop products with missing title
    df = df[~df["title"].isna()]

    return df

def update_products_details(df: pd.DataFrame, llm_outputs: list[dict]) -> pd.DataFrame:
    """
    Update the products details with the LLM outputs.

    Args:
        df (pd.DataFrame): DataFrame containing products
        llm_outputs (list[dict]): List of LLM outputs

    Returns:
        df: DataFrame with updated details
    """
    # Ensure llm_outputs is a list
    if not isinstance(llm_outputs, list):
        llm_outputs = [llm_outputs]

    for idx, llm_output in enumerate(llm_outputs):
        if idx >= len(df):
            break
            
        # If llm_output is already a dictionary, use it directly
        if isinstance(llm_output, dict):
            details = llm_output
        # If llm_output is a string, parse it as JSON
        else:
            try:
                details = json.loads(llm_output)
            except json.JSONDecodeError:
                continue
        
        # Update description only if it's null or empty
        if pd.isna(df.at[idx, 'description']) or df.at[idx, 'description'] == '':
            df.at[idx, 'description'] = details.get('Description', '')

        # Get existing details or create empty dict if null
        existing_details = {}
        if pd.notna(df.at[idx, 'details']):
            if isinstance(df.at[idx, 'details'], dict):
                existing_details = df.at[idx, 'details']
            elif isinstance(df.at[idx, 'details'], str):
                try:
                    existing_details = json.loads(df.at[idx, 'details'])
                except json.JSONDecodeError:
                    existing_details = {}

        # Create new details without Description
        new_details = {k: v for k, v in details.items() if k != 'Description'}

        # Merge existing and new details
        merged_details = {**existing_details, **new_details}

        # Update the details column
        df.at[idx, 'details'] = merged_details
    
    return df