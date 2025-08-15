from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.vector_store import search_similar_chunks
from ..services.llm_providers import LLMRequest, generate_with_fallback

router = APIRouter(prefix="/query", tags=["Document Query"])

class QueryRequest(BaseModel):
    question: str
    max_chunks: int = 5

class QueryResponse(BaseModel):
    answer: str
    provider_used: str
    success: bool
    relevant_chunks: list[str]
    error: Optional[str] = None

@router.post("", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        # Search for relevant document chunks
        chunks = search_similar_chunks(query=request.question, k=request.max_chunks)
        
        # Flatten chunks if nested lists
        flattened_chunks = []
        for c in chunks:
            if isinstance(c, list):
                flattened_chunks.extend(c)
            else:
                flattened_chunks.append(c)
        
        if not flattened_chunks:
            return QueryResponse(
                answer="No relevant documents found. Please upload documents first.",
                provider_used="none",
                success=False,
                relevant_chunks=[],
                error="No documents in database"
            )
        
        # Join chunks with double newlines
        context = '\n\n'.join(flattened_chunks)
        
        # Generate answer using LLM
        llm_request = LLMRequest(query=request.question, context=context)
        result = generate_with_fallback(llm_request)
        
        return QueryResponse(
            answer=result["answer"],
            provider_used=result["provider_used"],
            success=result["success"],
            relevant_chunks=flattened_chunks,
            error=result.get("error")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@router.get("/test")
async def test_query():
    return {"message": "Query service is working", "status": "healthy"}
