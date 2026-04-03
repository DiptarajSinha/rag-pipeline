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
    description="Production-grade Document RAG with Supabase and Gemini",
    version="1.0.0-prod-v2.3-diagnostic",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include API routers
app.include_router(upload.router)
app.include_router(query.router)
app.include_router(metadata.router)

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing RAG Pipeline v2.3-diagnostic...")
    logger.info(f"Debug mode: {settings.DEBUG}")

@app.get("/")
async def root():
    return {
        "message": "RAG Pipeline API - Diagnostic Mode",
        "debug": settings.DEBUG,
        "version": "1.0.0-prod-v2.3-diagnostic",
        "status": "online",
        "endpoints": [
            "/docs - API Documentation",
            "/models - Diagnostic endpoint to list available models",
            "/upload - Upload PDF documents",
            "/query - Query documents",
            "/metadata - Document metadata",
            "/health - Health check"
        ]
    }

@app.get("/models")
async def list_available_models():
    """Diagnostic endpoint to list models actually available to the API key"""
    try:
        from google import genai
        client = genai.Client(api_key=settings.GOOGLE_GEMINI_API_KEY)
        models = client.models.list()
        
        available_models = []
        for model in models:
            available_models.append({
                "name": model.name,
                "display_name": model.display_name,
                "supported_methods": model.supported_generation_methods
            })
            
        return {
            "status": "success",
            "count": len(available_models),
            "models": available_models
        }
    except Exception as e:
        logger.error(f"Failed to list models: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
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
            "version": "v2.3-diagnostic",
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
