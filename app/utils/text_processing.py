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
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)
        
        if chunk_text.strip():
            chunks.append(chunk_text)
        
        start = end - overlap
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
    
    # 1. First, fix the 's p a c e d o u t' characters.
    # This regex finds single characters surrounded by spaces and joins them.
    # It specifically targets cases where there are multiple single characters in a row.
    
    # Pattern: a space, then a single char, then a space (repeatedly)
    # We use a loop to ensure we catch all overlapping patterns
    for _ in range(3):
        text = re.sub(r'(^|\s)([a-zA-Z0-9])\s(?=[a-zA-Z0-9](\s|$))', r'\1\2', text)

    # 2. Fix cases where punctuation might be spaced out
    text = re.sub(r'\s+([,.!?])', r'\1', text)
    
    # 3. Remove extra whitespace and normalize
    text = " ".join(text.split())
    
    return text
