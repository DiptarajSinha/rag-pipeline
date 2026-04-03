from sqlalchemy import create_engine, Column, String, Integer, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os
import logging

logger = logging.getLogger("rag-pipeline.doc_store")

# Database configuration - defaults to local sqlite for dev, but REQUIRES postgres for prod
DB_URL = os.getenv("DB_URL", "sqlite:///./data/metadata.db")
DOC_LIMIT = 0 # Currently no limit, or fetch from env
try:
    DOC_LIMIT = int(os.getenv("DOC_LIMIT", "20"))
except ValueError:
    DOC_LIMIT = 20

# SQLAlchemy setup
# For Postgres, we don't need check_same_thread
connect_args = {}
if DB_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    DB_URL, 
    connect_args=connect_args,
    pool_pre_ping=True,  # Check connection health before using
    pool_recycle=300     # Recycle connections every 5 minutes
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DocumentMetadata(Base):
    __tablename__ = "documents"
    
    doc_id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    pages = Column(Integer, nullable=False)
    chunks = Column(Integer, nullable=False)
    text_length = Column(Integer, nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow)

# Create tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created successfully.")
except Exception as e:
    logger.error(f"Failed to initialize database tables: {e}")

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_metadata(doc_id: str, filename: str, pages: int, chunks: int, text_length: int):
    """Save document metadata to database"""
    db = SessionLocal()
    try:
        doc_meta = DocumentMetadata(
            doc_id=doc_id,
            filename=filename,
            pages=pages,
            chunks=chunks,
            text_length=text_length
        )
        db.add(doc_meta)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving metadata to database: {e}")
        return False
    finally:
        db.close()

def count_documents() -> int:
    """Count total documents in database"""
    db = SessionLocal()
    try:
        return db.query(DocumentMetadata).count()
    except Exception as e:
        logger.error(f"Error counting documents: {e}")
        return 0
    finally:
        db.close()

def list_documents() -> list:
    """List all documents with metadata"""
    db = SessionLocal()
    try:
        docs = db.query(DocumentMetadata).all()
        return [
            {
                "doc_id": doc.doc_id,
                "filename": doc.filename,
                "pages": doc.pages,
                "chunks": doc.chunks,
                "text_length": doc.text_length,
                "upload_time": doc.upload_time.isoformat()
            }
            for doc in docs
        ]
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        return []
    finally:
        db.close()

def delete_document(doc_id: str) -> bool:
    """Delete document metadata"""
    db = SessionLocal()
    try:
        doc = db.query(DocumentMetadata).filter(DocumentMetadata.doc_id == doc_id).first()
        if doc:
            db.delete(doc)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting document {doc_id}: {e}")
        return False
    finally:
        db.close()

def get_document_stats():
    """Get document statistics"""
    db = SessionLocal()
    try:
        total_docs = db.query(DocumentMetadata).count()
        total_pages = db.query(func.sum(DocumentMetadata.pages)).scalar() or 0
        total_chunks = db.query(func.sum(DocumentMetadata.chunks)).scalar() or 0
        
        return {
            "total_documents": total_docs,
            "total_pages": int(total_pages),
            "total_chunks": int(total_chunks),
            "documents_remaining": max(0, DOC_LIMIT - total_docs)
        }
    except Exception as e:
        logger.error(f"Error retrieving document statistics: {e}")
        return {"error": str(e)}
    finally:
        db.close()
