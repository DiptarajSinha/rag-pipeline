import vecs
from google import genai
from google.genai import types
import os
import logging
from typing import List
from ..config import settings

logger = logging.getLogger("rag-pipeline.vector_store")
logger.info("VECTOR_STORE_V1.5_INITIALIZED")

# Initialize Gemini Client
client = None
if settings.GOOGLE_GEMINI_API_KEY:
    client = genai.Client(api_key=settings.GOOGLE_GEMINI_API_KEY)

# We use text-embedding-004 as primary, but will fallback to embedding-001 if needed
PRIMARY_MODEL = "text-embedding-004"
FALLBACK_MODEL = "embedding-001"
VECTOR_DIMENSION = 768 # Both models use 768
COLLECTION_NAME = "document_embeddings_v2"

def _get_vecs_collection():
    """Helper to get/create a vecs collection with better diagnostics"""
    db_url = settings.DB_URL
    if not db_url:
        raise ValueError("DB_URL is missing. Please add it to Hugging Face Secrets.")
        
    try:
        # Create a vecs client
        logger.info(f"Connecting to Supabase...")
        vx = vecs.create_client(db_url)
        
        # Get or create the collection
        return vx.get_or_create_collection(name=COLLECTION_NAME, dimension=VECTOR_DIMENSION)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"SUPABASE_CONNECTION_ERROR: {error_msg}")
        raise ConnectionError(f"Critical error connecting to Supabase: {error_msg}")

def _get_embeddings(texts: List[str]) -> List[List[float]]:
    """Helper to get embeddings from Gemini API with batching and fallback"""
    if not client:
        raise ValueError("Gemini Client not initialized. Check API key.")
        
    batch_size = 100
    all_embeddings = []
    
    # Try models in order: 004 then 001
    current_model = PRIMARY_MODEL
    
    try:
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            try:
                result = client.models.embed_content(
                    model=current_model,
                    contents=batch,
                    config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
                )
            except Exception as e:
                # If primary fails with a NotFound error, try fallback for the whole document
                if "not found" in str(e).lower() and current_model == PRIMARY_MODEL:
                    logger.warning(f"Model {PRIMARY_MODEL} not found. Falling back to {FALLBACK_MODEL}")
                    current_model = FALLBACK_MODEL
                    # Retry the same batch with the fallback model
                    result = client.models.embed_content(
                        model=current_model,
                        contents=batch,
                        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
                    )
                else:
                    raise e
                    
            all_embeddings.extend([item.values for item in result.embeddings])
        return all_embeddings
    except Exception as e:
        logger.error(f"Gemini Embedding API error: {e}")
        raise

def add_document_chunks(doc_id: str, chunks: List[str]):
    """Add document chunks to Supabase using Gemini Embeddings"""
    collection = _get_vecs_collection()
            
    # Generate embeddings via API
    embeddings = _get_embeddings(chunks)
    
    # Prepare data for vecs
    records = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        chunk_id = f"{doc_id}_chunk_{i}"
        records.append((
            chunk_id,
            embedding,
            {"document_id": doc_id, "chunk_index": i, "content": chunk}
        ))
    
    # Upsert into pgvector
    logger.info(f"Upserting {len(records)} records into Supabase...")
    collection.upsert(records=records)
    collection.create_index()

def search_similar_chunks(query: str, k: int = 5) -> List[str]:
    """Search for similar document chunks with model fallback"""
    collection = _get_vecs_collection()
    if not client:
        return []
        
    current_model = PRIMARY_MODEL
    try:
        try:
            result = client.models.embed_content(
                model=current_model,
                contents=query,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
            )
        except Exception as e:
            if "not found" in str(e).lower():
                current_model = FALLBACK_MODEL
                result = client.models.embed_content(
                    model=current_model,
                    contents=query,
                    config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
                )
            else:
                raise e
                
        query_embedding = result.embeddings[0].values
        
        results = collection.query(
            data=query_embedding,
            limit=k,
            include_metadata=True
        )
        return [res[1].get("content", "") for res in results if res[1]]
    except Exception as e:
        logger.error(f"Error searching Supabase: {e}")
        return []

def get_collection_stats() -> dict:
    """Get statistics about the document collection"""
    try:
        collection = _get_vecs_collection()
        total = collection.count()
        return {"total_chunks": total}
    except Exception as e:
        logger.error(f"Error retrieving collection stats: {e}")
        return {"total_chunks": 0, "error": str(e)}
