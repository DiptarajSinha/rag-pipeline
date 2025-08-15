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
        print(f"Error extracting PDF text: {e}")
        return ""

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Remove special characters if needed
    # Add more cleaning rules here as needed
    
    return text
