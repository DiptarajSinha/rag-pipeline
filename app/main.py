from fastapi import FastAPI
import logging
from .config import settings
from .api import upload, query, metadata

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("rag-pipeline")

app = FastAPI(
    title="RAG Pipeline API",
    description="Document upload and intelligent querying system with metadata management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include API routers
app.include_router(upload.router)
app.include_router(query.router)
app.include_router(metadata.router)

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing RAG Pipeline...")
    logger.info(f"Debug mode: {settings.DEBUG}")

@app.get("/")
async def root():
    return {
        "message": "RAG Pipeline API",
        "debug": settings.DEBUG,
        "version": "1.0.0-prod-v1.3",
        "status": "online",
        "endpoints": [
            "/docs - API Documentation",
            "/upload - Upload PDF documents",
            "/query - Query documents",
            "/metadata - Document metadata",
            "/health - Health check"
        ]
    }

@app.get("/health")
async def health():
    """Comprehensive health check"""
    try:
        from .services.doc_store import get_document_stats
        from .services.vector_store import get_collection_stats
        
        doc_stats = get_document_stats()
        vector_stats = get_collection_stats()
        
        return {
            "status": "healthy",
            "services": {
                "api": "running",
                "database": "connected",
                "vector_store": "connected",
                "llm_providers": "configured"
            },
            "stats": {
                "documents": doc_stats.get("total_documents", 0),
                "chunks": vector_stats.get("total_chunks", 0)
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "degraded",
            "error": str(e)
        }

@app.get("/config-test")
async def config_test():
    """Test configuration and API keys"""
    return {
        "gemini_key_loaded": bool(settings.GOOGLE_GEMINI_API_KEY),
        "openai_key_loaded": bool(settings.OPENAI_API_KEY),
        "cohere_key_loaded": bool(settings.COHERE_API_KEY),
        "debug_mode": settings.DEBUG
    }
