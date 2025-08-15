# RAG Pipeline — “Ask Your Docs” 📚🤖

Tired of scrolling 1 000-page PDFs? Upload them here and let an AI assistant answer your questions—powered by vector search + large language models.

---

## ✨ Features
- **Document ingestion**: upload ≤ 20 PDFs (≤ 1 000 pages each). Automatic text extraction, cleaning & chunking.
- **Semantic retrieval**: ChromaDB vector store + Sentence-Transformer embeddings.
- **Multi-LLM fallback**: Gemini → OpenAI → Cohere (cheapest first; automatic fail-over).
- **FastAPI REST API** with Swagger UI at `/docs`.
- **Metadata DB**: lightweight SQLite for filenames, page counts, chunks, timestamps.
- **Docker-first** workflow: single `docker compose up` runs everything.
- **Automated tests**: Pytest unit + integration tests validate upload, retrieval and /query.

---

## 🚀 Quick Start

1. Clone
`git clone https://github.com/YOUR_USERNAME/rag-pipeline.git
cd rag-pipeline`

2. Configure
`cp .env.example .env # add your API keys here`

3. Run
`docker compose up --build # http://localhost:8000/docs for Swagger UI`


---

## ⚙️ Environment Variables

| Key                         | Example value        | Purpose                              |
|-----------------------------|----------------------|--------------------------------------|
| `GOOGLE_GEMINI_API_KEY`     | `AIza...`            | Primary, free-tier LLM               |
| `OPENAI_API_KEY`            | `sk-...`             | Fallback LLM                         |
| `COHERE_API_KEY`            | `CLlu...`            | 2nd fallback LLM                     |
| `PROVIDER_PRIORITY`         | `gemini,openai,cohere` (default) | Comma-ordered list, left→right |
| `DEBUG`                     | `True` / `False`     | Verbose logging & reload            |

_No key? That provider politely steps aside._

---

## 🔌 API Usage

### Upload PDF
`curl -F "file=@myDoc.pdf" http://localhost:8000/upload`

### Ask a Question
`curl -H "Content-Type: application/json"
-d '{"question":"What is the main idea?"}'
http://localhost:8000/query`

### Check Health & Stats
curl http://localhost:8000/health
curl http://localhost:8000/upload/stats
curl http://localhost:8000/metadata

Interactive testing: open **`/docs`** in your browser.

---

## 🧪 Testing

full test suite
`docker compose run --rm test`

run a single test file
`docker compose exec web pytest tests/test_query.py -v`

Coverage:
- Upload happy / sad paths  
- Vector search returns ≥ 1 chunk  
- End-to-end `/query` 200 + non-empty answer  

---

## ☁️ Deployment

### Local Docker
`docker compose up --build`


### Render.com (free)
1. Create Web Service → **Environment = Docker**.  
2. Add env-vars above.  
3. Click **Deploy** → public URL ready.

Works on any Docker host (AWS, GCP, Azure, fly.io, Railway, etc.).

---

## 🔄 Postman Collection (optional)

Import `postman/RAG_pipeline.postman_collection.json` → run **Upload**, **Query**, **Health** requests with one click.

---

## 🤝 Contributing

Bug reports & PRs welcome—just keep code formatted (black) and tests green.  
Humorous commit messages earn extra karma.

---

## 📝 License
MIT — because knowledge (and mild sarcasm) wants to be free.

> “Reading is hard; let the vector database do it for you.”
