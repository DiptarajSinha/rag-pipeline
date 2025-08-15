import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

import pytest
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint returns correct information"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["message"] == "RAG Pipeline API"

def test_health_endpoint():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data

def test_config_test_endpoint():
    """Test config test endpoint"""
    response = client.get("/config-test")
    assert response.status_code == 200
    data = response.json()
    assert "debug_mode" in data

def test_metadata_stats():
    """Test metadata stats endpoint"""
    response = client.get("/metadata/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data

def test_upload_stats():
    """Test upload stats endpoint"""
    response = client.get("/upload/stats")
    assert response.status_code == 200

def test_query_endpoint_no_documents():
    """Test query endpoint with no documents"""
    query_data = {"question": "What is AI?"}
    response = client.post(
        "/query",
        json=query_data,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data

def test_upload_invalid_file():
    """Test upload with invalid file type"""
    # Create a temporary text file
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
        f.write("This is a test file")
        temp_file_path = f.name
    
    try:
        with open(temp_file_path, "rb") as f:
            response = client.post(
                "/upload",
                files={"file": ("test.txt", f, "text/plain")}
            )
        assert response.status_code == 400
        assert "Only PDF files are supported" in response.json()["detail"]
    finally:
        os.unlink(temp_file_path)

@pytest.mark.asyncio
async def test_vector_store_functions():
    """Test vector store basic functions"""
    from app.services.vector_store import get_collection_stats
    
    stats = get_collection_stats()
    assert "total_chunks" in stats

@pytest.mark.asyncio 
async def test_text_processing():
    """Test text processing functions"""
    from app.utils.text_processing import chunk_text, clean_text
    
    test_text = "This is a test document. " * 100
    cleaned = clean_text(test_text)
    chunks = chunk_text(cleaned, chunk_size=50)
    
    assert len(cleaned) > 0
    assert len(chunks) > 0
    assert all(isinstance(chunk, str) for chunk in chunks)

def test_llm_providers_import():
    """Test that LLM providers can be imported"""
    try:
        from app.services.llm_providers import PROVIDERS, generate_with_fallback
        assert len(PROVIDERS) > 0
        assert callable(generate_with_fallback)
    except ImportError as e:
        pytest.fail(f"Could not import LLM providers: {e}")

def test_doc_store_functions():
    """Test document store functions"""
    from app.services.doc_store import count_documents, get_document_stats
    
    count = count_documents()
    assert isinstance(count, int)
    assert count >= 0
    
    stats = get_document_stats()
    assert "total_documents" in stats
    assert "documents_remaining" in stats
