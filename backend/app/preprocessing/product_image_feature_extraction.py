from app.clients import get_openai_client
from app.config.settings import Settings

from app.utils.logger import setup_logger

logger = setup_logger("product_image_feature_extraction")

settings = Settings()

def product_image_title_extraction(img_url: str) -> str:
    """
    Extract title from image using OpenAI vision model.

    Args:
        img_url (str): URL of the image to extract feature from

    Returns:
        str: The extracted title from the image

    Raises:
        Exception: If failed to extract title from the image
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

        logger.info("Starting image title extraction", extra={"image_url": img_url})

        # NOTE: This could be used to extract categories(color, occasion, etc.) to increase the context of the product.
        # Which will increase the accuracy of the product search. Will consider if there is credit left.
        response = client.responses.create(
            model=settings.IMAGE_FEATURE_EXTRACTION_MODEL,
            input=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": task_prompt},
                        {"type": "input_image", "image_url": img_url},
                    ],
                },
            ],
        )

        logger.info("Image title extraction completed", extra={"image_url": img_url})

        return response.output_text

    except Exception as e:
        logger.error("Title extraction failed", extra={
            "image_url": img_url,
            "error": str(e),
            "error_type": type(e).__name__
        })
        return None

def product_image_feature_extraction(img_url: str) -> str:
    """
    Extract title from image using OpenAI vision model.

    Args:
        img_url (str): URL of the image to extract feature from

    Returns:
        str: The extracted feature from the image

    Raises:
        Exception: If failed to extract title from the image
    """

    system_prompt = """
        You are an assistant that tags fashion product images
        and generates detailed and accurate titles suitable for e-commerce listings.        
    """

    task_prompt = """
        Please generate a detailed product title for this fashion item.
                


        ## Output format
        - please return in JSON object format (do not include ```)


        ## Example output
        {   
            "Image_available": "Yes",
            "Description": "This is a description of the product",
            "Age Range": "All Ages" or "Kids (0-12)" or "Teens (13-19)" or "Young Adults (20-29)" or "Adults (30-49)" or "Seniors (50+)",
            "Brand": "Brand name",
            "Color": "Neutral" or "Warm" or "Cool" or "Pastels & Brights",
            "Occasion": "Beach" or "Office" or "Party" or "Casual" or "Formal" or "Sport" or "Other",
            "Categories": "Clothing" or "Shoes" or "Accessories" or "Bag & Luggage" or "Kids and Baby" or "Sportswear" or "Uniforms & Workwear"
        }
    """

    try:
        client = get_openai_client()

        logger.info("Starting image feature extraction", extra={"image_url": img_url})

        # NOTE: This could be used to extract categories(color, occasion, etc.) to increase the context of the product.
        # Which will increase the accuracy of the product search. Will consider if there is credit left.
        response = client.responses.create(
            model=settings.IMAGE_FEATURE_EXTRACTION_MODEL,
            input=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": task_prompt},
                        {"type": "input_image", "image_url": img_url},
                    ],
                },
            ],
        )

        logger.info("Image feature extraction completed", extra={"image_url": img_url})

        return response.output_text

    except Exception as e:
        logger.error("Feature extraction failed", extra={
            "image_url": img_url,
            "error": str(e),
            "error_type": type(e).__name__
        })
        return None