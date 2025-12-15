# backend/app/utils/text_cleaning.py
# TEXT PREPROCESSING UTILITIES
# Cleans and normalizes clinical text before feeding it to ML models

import re

def clean_text(text: str) -> str:
    """
    Comprehensive text cleaning function for clinical notes.
    
    Performs the following cleaning operations:
    1. Removes HTML tags (in case text comes from web forms)
    2. Removes URLs (http/https/www links)
    3. Normalizes whitespace (converts multiple spaces/tabs/newlines to single space)
    4. Strips leading/trailing whitespace
    
    This ensures consistent text format for all three models:
    - BERT classifier
    - T5 summarizer
    - Llama generator
    
    Args:
        text: Raw input text (patient case description, clinical notes, etc.)
        
    Returns:
        Cleaned text string ready for model processing
        
    Examples:
        >>> clean_text("Patient   shows\n\nsigns  of <b>anxiety</b>")
        "Patient shows signs of anxiety"
        
        >>> clean_text("See more at https://example.com")
        "See more at"
    """
    # Handle non-string inputs gracefully
    if not isinstance(text, str):
        return ""
    
    # Remove HTML tags (e.g., <b>, <div>, etc.)
    # Regex matches anything between < and >
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove URLs (http, https, www)
    # Matches complete URLs including query parameters
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Normalize whitespace (replace multiple spaces/tabs/newlines with single space)
    # \s+ matches one or more whitespace characters (space, tab, newline, etc.)
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading and trailing whitespace
    return text.strip()