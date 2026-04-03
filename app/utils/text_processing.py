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
    """Extract text from PDF file"""
    try:
        from pypdf import PdfReader
        
        reader = PdfReader(file_path)
        text_content = ""
        
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_content += page_text + "\n"
        
        return text_content.strip()
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        return ""

def clean_text(text: str) -> str:
    """Rigorous text cleaning to resolve 's p a c e d' character issues from PDFs"""
    if not text:
        return ""
    
    # Use a more aggressive approach to heal separated characters.
    # While there's a space between two single characters, join them.
    # We do this up to 10 times to handle long words like "P R O F E S S I O N A L".
    for _ in range(10):
        # Replaces Space + Char + Space with Space + Char (essentially collapsing)
        text = re.sub(r'(\s|^)([a-zA-Z0-9])\s(?=[a-zA-Z0-9](\s|$))', r'\1\2', text)
    
    # Final cleanup of extra whitespace
    text = " ".join(text.split())
    
    return text
