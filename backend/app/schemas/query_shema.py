import re

from pydantic import BaseModel, field_validator
from typing import Optional


class QueryValidationBase(BaseModel):
    query: str
    top_k: Optional[int] = 10

    @field_validator("query")
    @classmethod
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError("Query cannot be empty or only spaces.")
        if len(v) > 100:
            raise ValueError("Query cannot be longer than 100 characters.")
        
        # Check if query contains only numbers
        if v.strip().isdigit():
            raise ValueError("Query cannot contain only numbers.")
        
        # Check if query contains only symbols:
        if not any(c.isalnum() for c in v):
            raise ValueError("Query cannot contain only symbols.")
        
        # Validate against harmful content
        harmful_words = [
            "gun", "bomb", "kill", "murder", "shoot", "attack", "weapon", "explosive",
            "bullet", "acid", "sniper", "grenade", "terror", "assault", "execute",
            "behead", "poison", "cyanide", "sarin", "anthrax", "suicide bomber",
            "arson", "sabotage", "molotov", "lynch", "genocide", "riot", "vandalism",
            "rape", "slaughter", "firearm", "extremist", "burn down", "hate crime",
            "abuse", "threaten"
        ]

        # Check for harmful words
        if any(word in v.lower() for word in harmful_words):
            raise ValueError("Query contains inappropriate words.")

        # Check for invalid characters
        if re.search(r"[<>{}[\]\\]", v):
            raise ValueError("Query contains invalid characters.")
    
        return v
        

    @field_validator("top_k")
    @classmethod
    def validate_top_k(cls, v):
        if v is not None and (v < 1 or v > 10):
            raise ValueError("Top k must be between 1 and 10.")
        return v if v is not None else 10
        
    
    
    