from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

# Database configuration
DB_URL = "sqlite:///./data/metadata.db"
DOC_LIMIT = 20

# SQLAlchemy setup
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
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
Base.metadata.create_all(bind=engine)

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
        print(f"Error saving metadata: {e}")
        return False
    finally:
        db.close()

def count_documents() -> int:
    """Count total documents in database"""
    db = SessionLocal()
    try:
        return db.query(DocumentMetadata).count()
    except Exception:
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
        print(f"Error listing documents: {e}")
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
        print(f"Error deleting document: {e}")
        return False
    finally:
        db.close()

def get_document_stats():
    """Get document statistics"""
    db = SessionLocal()
    try:
        total_docs = db.query(DocumentMetadata).count()
        total_pages = db.query(db.func.sum(DocumentMetadata.pages)).scalar() or 0
        total_chunks = db.query(db.func.sum(DocumentMetadata.chunks)).scalar() or 0
        
        return {
            "total_documents": total_docs,
            "total_pages": total_pages,
            "total_chunks": total_chunks,
            "documents_remaining": DOC_LIMIT - total_docs
        }
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {"error": str(e)}
    finally:
        db.close()
