import vecs
from google import genai
from google.genai import types
import os
import logging
from typing import List
from .config import settings

logger = logging.getLogger("rag-pipeline.vector_store")

# Initialize Gemini Client
client = None
if settings.GOOGLE_GEMINI_API_KEY:
    client = genai.Client(api_key=settings.GOOGLE_GEMINI_API_KEY)

EMBEDDING_MODEL = "text-embedding-004" # Modern embedding model
VECTOR_DIMENSION = 768

# DB URL for Supabase
DB_URL = settings.DB_URL
COLLECTION_NAME = "document_embeddings"

def _get_vecs_collection():
    """Helper to get/create a vecs collection"""
    if not DB_URL:
        logger.error("DB_URL not found in settings.")
        return None
        
    try:
        # Create a vecs client
        vx = vecs.create_client(DB_URL)
        # Get or create the collection
        return vx.get_or_create_collection(name=COLLECTION_NAME, dimension=VECTOR_DIMENSION)
    except Exception as e:
        logger.error(f"Failed to connect to Supabase pgvector: {e}")
        return None

def _get_embeddings(texts: List[str]) -> List[List[float]]:
    """Helper to get embeddings from Gemini API with batching"""
    if not client:
        raise ValueError("Gemini Client not initialized. Check API key.")
        
    try:
        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=texts,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
        )
        # Handle the result format from the new SDK
        return [item.values for item in result.embeddings]
    except Exception as e:
        logger.error(f"Gemini Embedding API error: {e}")
        raise

def add_document_chunks(doc_id: str, chunks: List[str]) -> bool:
    """Add document chunks to Supabase using Gemini Embeddings"""
    collection = _get_vecs_collection()
    if not collection:
        return False
        
    try:
        if not chunks:
            return True
            
        # Generate embeddings via API
        embeddings = _get_embeddings(chunks)
        
        # Prepare data for vecs (id, vector, metadata)
        records = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = f"{doc_id}_chunk_{i}"
            records.append((
                chunk_id,
                embedding,
                {"document_id": doc_id, "chunk_index": i, "content": chunk}
            ))
        
        # Upsert into pgvector
        collection.upsert(records=records)
        collection.create_index()
        
        return True
    except Exception as e:
        logger.error(f"Error adding chunks to Supabase: {e}")
        return False

def search_similar_chunks(query: str, k: int = 5) -> List[str]:
    """Search for similar document chunks using Gemini Embedding API and Supabase"""
    collection = _get_vecs_collection()
    if not collection:
        return []
        
    if not client:
        logger.error("Gemini Client not initialized")
        return []
        
    try:
        # Generate query embedding
        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=query,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
        )
        query_embedding = result.embeddings[0].values
        
        # Search in pgvector
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
    collection = _get_vecs_collection()
    if not collection:
        return {"total_chunks": 0}
        
    try:
        total = collection.count()
        return {"total_chunks": total}
    except Exception as e:
        logger.error(f"Error retrieving collection stats: {e}")
        return {"total_chunks": 0, "error": str(e)}
