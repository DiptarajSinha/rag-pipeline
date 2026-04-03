import re
import logging

logger = logging.getLogger("rag-pipeline.text_processing")

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """Split text into overlapping chunks"""
    if not text.strip():
        return []
    
    words = text.split()
    chunks = []
    start = 0
    
    while start < len(words):
        # Calculate end position
        end = start + chunk_size
        
        # Get chunk words
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)
        
        # Add chunk if it has content
        if chunk_text.strip():
            chunks.append(chunk_text)
        
        # Move start position (with overlap)
        start = end - overlap
        
        # Break if we've processed all words
        if end >= len(words):
            break
    
    return chunks

def extract_pdf_text(file_path: str) -> str:
    """Extract text from PDF file with improved character handling"""
    try:
        from pypdf import PdfReader
        
        reader = PdfReader(file_path)
        text_content = ""
        
        for page in reader.pages:
            # Using basic extraction - cleaning will happen in clean_text
            page_text = page.extract_text()
            if page_text:
                text_content += page_text + "\n"
        
        return text_content.strip()
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        return ""

def clean_text(text: str) -> str:
    """Clean and normalize text, fixing 's p a c e d' character issues"""
    if not text:
        return ""
    
    # Fix 's p a c e d o u t' characters (common in some PDFs)
    # This regex looks for single letters separated by single spaces
    # and joins them back together if they appear in a sequence.
    def fix_spaced_text(match):
        # Join the characters and remove the spaces between them
        return match.group(0).replace(" ", "")

    # Look for sequences of [Letter Space Letter Space Letter]
    # We do this a few times to catch longer words
    text = re.sub(r'([a-zA-Z0-9])\s([a-zA-Z0-9])\s([a-zA-Z0-9])\s([a-zA-Z0-9])', fix_spaced_text, text)
    text = re.sub(r'([a-zA-Z0-9])\s([a-zA-Z0-9])', fix_spaced_text, text)
    
    # Remove extra whitespace and normalize
    text = " ".join(text.split())
    
    return text
