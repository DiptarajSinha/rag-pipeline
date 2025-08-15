from fastapi import APIRouter, UploadFile, File, HTTPException
from ..services.vector_store import add_document_chunks, get_collection_stats
from ..services.doc_store import save_metadata, count_documents, DOC_LIMIT
from ..utils.text_processing import extract_pdf_text, chunk_text, clean_text
import uuid
import os

router = APIRouter(prefix="/upload", tags=["Document Upload"])

@router.post("")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a PDF document with limits enforcement"""
    
    # Check document limit
    current_count = count_documents()
    if current_count >= DOC_LIMIT:
        raise HTTPException(
            status_code=400, 
            detail=f"Document limit reached. Maximum {DOC_LIMIT} documents allowed. Currently have {current_count} documents."
        )
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Validate file size (max 50MB)
    file_content = await file.read()
    if len(file_content) > 50 * 1024 * 1024:  # 50MB
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 50MB")
    
    try:
        # Generate unique document ID
        doc_id = str(uuid.uuid4())
        
        # Save file temporarily
        temp_path = f"/app/uploads/{doc_id}_{file.filename}"
        os.makedirs("/app/uploads", exist_ok=True)
        
        with open(temp_path, "wb") as f:
            f.write(file_content)
        
        # Extract text from PDF
        text_content = extract_pdf_text(temp_path)
        
        if not text_content:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
        # Count pages (approximate based on text length)
        estimated_pages = max(1, len(text_content) // 2000)  # Rough estimate
        
        # Check page limit
        if estimated_pages > 1000:
            raise HTTPException(
                status_code=400, 
                detail=f"Document too large. Maximum 1000 pages allowed. This document has approximately {estimated_pages} pages."
            )
        
        # Clean and chunk the text
        cleaned_text = clean_text(text_content)
        chunks = chunk_text(cleaned_text)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No text content found in document")
        
        # Add chunks to vector database
        success = add_document_chunks(doc_id, chunks)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to process document")
        
        # Save metadata to database
        metadata_saved = save_metadata(
            doc_id=doc_id,
            filename=file.filename,
            pages=estimated_pages,
            chunks=len(chunks),
            text_length=len(cleaned_text)
        )
        
        if not metadata_saved:
            print(f"Warning: Failed to save metadata for document {doc_id}")
        
        # Clean up temporary file
        os.remove(temp_path)
        
        return {
            "document_id": doc_id,
            "filename": file.filename,
            "chunks_created": len(chunks),
            "text_length": len(cleaned_text),
            "estimated_pages": estimated_pages,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.get("/stats")
async def get_upload_stats():
    """Get statistics about uploaded documents"""
    from ..services.doc_store import get_document_stats
    
    stats = get_document_stats()
    vector_stats = get_collection_stats()
    
    return {
        **stats,
        "vector_chunks": vector_stats.get("total_chunks", 0)
    }
