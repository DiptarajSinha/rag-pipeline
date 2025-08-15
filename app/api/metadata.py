from fastapi import APIRouter, HTTPException
from ..services.doc_store import list_documents, delete_document, get_document_stats

router = APIRouter(prefix="/metadata", tags=["Document Metadata"])

@router.get("")
async def get_all_metadata():
    """Get metadata for all uploaded documents"""
    try:
        documents = list_documents()
        stats = get_document_stats()
        
        return {
            "documents": documents,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve metadata: {str(e)}")

@router.get("/stats")
async def get_metadata_stats():
    """Get document statistics"""
    try:
        return get_document_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve stats: {str(e)}")

@router.delete("/{doc_id}")
async def delete_document_metadata(doc_id: str):
    """Delete document metadata (note: does not remove from vector store)"""
    try:
        success = delete_document(doc_id)
        if success:
            return {"message": f"Document {doc_id} metadata deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@router.get("/health")
async def metadata_health():
    """Health check for metadata service"""
    try:
        stats = get_document_stats()
        return {
            "status": "healthy",
            "database": "connected",
            "stats": stats
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e)
        }
