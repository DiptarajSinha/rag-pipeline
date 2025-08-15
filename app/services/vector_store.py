import chromadb
from sentence_transformers import SentenceTransformer
import os

# Initialize ChromaDB with persistent storage
client = chromadb.PersistentClient(path="/app/chroma_data")
collection = client.get_or_create_collection("documents")

# Initialize local embedding model (free)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def add_document_chunks(doc_id: str, chunks: list[str]) -> bool:
    """Add document chunks to vector database"""
    try:
        # Generate unique IDs for each chunk
        chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        
        # Generate embeddings for chunks
        embeddings = embedder.encode(chunks).tolist()
        
        # Create metadata for each chunk
        metadatas = [{"document_id": doc_id, "chunk_index": i} for i in range(len(chunks))]
        
        # Add to ChromaDB
        collection.add(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )
        return True
    except Exception as e:
        print(f"Error adding chunks to vector store: {e}")
        return False

def search_similar_chunks(query: str, k: int = 5) -> list[str]:
    """Search for similar document chunks"""
    try:
        # Generate query embedding
        query_embedding = embedder.encode([query])[0].tolist()
        
        # Search in ChromaDB
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        # Return the document chunks
        return results["documents"] if results["documents"] else []
    except Exception as e:
        print(f"Error searching vector store: {e}")
        return []

def get_collection_stats() -> dict:
    """Get statistics about the document collection"""
    try:
        count = collection.count()
        return {"total_chunks": count}
    except Exception as e:
        return {"total_chunks": 0, "error": str(e)}
