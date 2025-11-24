# backend/app/utils/text_cleaning.py

import re

def clean_text(text: str) -> str:
    """
    Comprehensive text cleaning function for clinical notes.
    Removes HTML tags, URLs, extra whitespace, and normalizes text.
    
    Args:
        text: Raw input text
        
    Returns:
        Cleaned text string
    """
    if not isinstance(text, str):
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove extra whitespace (multiple spaces, tabs, newlines)
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    return text.strip()