import vecs
import google.generativeai as genai
import os
import logging
from typing import List

logger = logging.getLogger("rag-pipeline.vector_store")

# Configure Google Generative AI for embeddings
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))
EMBEDDING_MODEL = "models/embedding-001"
VECTOR_DIMENSION = 768 # models/embedding-001 dimension

# DB URL for Supabase
DB_URL = os.getenv("DB_URL")
COLLECTION_NAME = "document_embeddings"

def _get_vecs_collection():
    """Helper to get/create a vecs collection"""
    if not DB_URL:
        logger.error("DB_URL not found in environment variables.")
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
    try:
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=texts,
            task_type="retrieval_document"
        )
        return result['embedding']
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
        # vecs expects a list of tuples: (id, vector, metadata)
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
        
        # Create an index if it doesn't exist (optional, but good for performance)
        # For small datasets, this is fast.
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
        
    try:
        # Generate query embedding
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=query,
            task_type="retrieval_query"
        )
        query_embedding = result['embedding']
        
        # Search in pgvector
        # results = collection.query(data=query_embedding, limit=k, include_value=False, include_metadata=True)
        # Note: vecs.query returns IDs by default, but we want the metadata/text
        results = collection.query(
            data=query_embedding,
            limit=k,
            include_metadata=True
        )
        
        # Extract text from metadata
        # vecs metadata is stored in the metadata column
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
        # Get count of documents in the collection
        # vecs doesn't have a direct count() on collection in all versions, 
        # but we can query or use the metadata
        total = collection.count() # Some versions of vecs support count()
        return {"total_chunks": total}
    except Exception as e:
        logger.error(f"Error retrieving collection stats: {e}")
        return {"total_chunks": 0, "error": str(e)}
