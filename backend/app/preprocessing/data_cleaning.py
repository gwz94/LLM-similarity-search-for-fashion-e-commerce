import pandas as pd
import numpy as np

from app.utils.logger import setup_logger

logger = setup_logger("data_cleaning")

def sanitize(value):
    """
    Sanitize the value to handle missing values or values with only space.

    Args:
        value: The value to sanitize

    Returns:
        The sanitized value
    """
    if isinstance(value, float) and np.isnan(value):
        return None
    elif isinstance(value, list):
        return [sanitize(item) for item in value]
    elif isinstance(value, dict):
        return {k: sanitize(v) for k, v in value.items()}
    return value

def data_cleaning(df: pd.DataFrame) -> pd.DataFrame:
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
    logger.info("Starting data cleaning", extra={"num_products": initial_count})

    # Handle missing values or values with only space
    logger.info("Handling missing values and empty strings")
    for column in df.columns:
        df[column] = df[column].apply(
            lambda x: np.nan
            if (
                (isinstance(x, list) and len(x) == 0)  # To handle empty lists
                or (
                    isinstance(x, str) and x.strip() == ""
                )  # To handle empty cell with only space
            )
            else x
        )
    # In order to insert data into the database, convert np.nan to None
    df["features"] = df["features"].apply(sanitize)

    # Handle inventory status, product with price is in stock, otherwise out of stock
    logger.info("Setting inventory status based on price")
    df["inventory_status"] = df["price"].apply(
        lambda x: "in_stock" if pd.notnull(x) else "out_of_stock"
    )
    in_stock_count = (df["inventory_status"] == "in_stock").sum()
    out_of_stock_count = (df["inventory_status"] == "out_of_stock").sum()
    logger.info("Inventory status", extra={"in_stock": in_stock_count, "out_of_stock": out_of_stock_count})

    # Handle discontinued products(product that has no price and labeled as discontinued in details)
    logger.info("Handling discontinued products")
    mask = (df["inventory_status"] == "out_of_stock") & (
        df["details"].apply(
            lambda d: isinstance(d, dict)
            and (
                d.get("is_discontinued") == "Yes" or d.get("is_discontinued") == "True"
            )
        )
    )
    out_of_stock_and_discontinued_count = mask.sum()
    df.loc[mask, "inventory_status"] = "out of stock and discontinued"
    logger.info("Discontinued products", extra={"count": out_of_stock_and_discontinued_count})

    # Remove products that are both out of stock and discontinued
    df = df[~(df["inventory_status"] == "out of stock and discontinued")]
    logger.info("Removed discontinued products", extra={"count": out_of_stock_and_discontinued_count})

    # Count products with very low prices
    low_price_count = (df["price"] <= 0.05).sum()
    # Keep products that either have no price (NaN) or have price > 0.05
    df = df[(df["price"].isna()) | (df["price"] > 0.05)]
    logger.info("Removed products with price below 0.05", extra={"count": low_price_count})

    final_count = len(df)
    logger.info("Data cleaning completed", extra={"initial_count": initial_count, "final_count": final_count})

    return df

