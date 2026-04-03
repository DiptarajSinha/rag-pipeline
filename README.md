---
title: RAG Pipeline Pro
emoji: 🚀
colorFrom: cyan
colorTo: blue
sdk: docker
app_port: 7860
pinned: true
---

# 🚀 RAG Pipeline Pro: Production-Grade Document Intelligence

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

A high-performance, **cloud-persistent** Retrieval-Augmented Generation (RAG) pipeline. Built with **FastAPI**, **Gemini 2.5 Flash**, and **Supabase (pgvector)**, this system allows you to upload PDFs and query them with absolute accuracy.

---

## ✨ Features

- 🧠 **Gemini 2.5 Flash Intelligence**: Leverages Google's latest high-speed reasoning model for precise answers.
- 📂 **Cloud Persistence**: Unlike standard RAG demos, all your documents and vectors are stored permanently in **Supabase Cloud**.
- 🛠️ **Advanced Text Healing**: Includes a recursive cleaning engine to fix messy PDF extractions and "spaced-out" characters.
- ⚡ **Auto-Retry Architecture**: Built-in exponential backoff to handle API rate limits gracefully on the free tier.
- 🔍 **Vector Search**: High-speed HNSW indexing via `pgvector` for instant retrieval across large datasets.
- 🐳 **Docker Optimized**: Fully containerized for one-click deployment to Hugging Face Spaces.

---

## 🏗️ System Architecture

```mermaid
graph LR
    User([User]) --> API[FastAPI Gateway]
    API --> PDF[Text Extraction & Cleaning]
    PDF --> Embed[Gemini Embedding 001]
    Embed --> DB[(Supabase pgvector)]
    API --> Query[Semantic Search]
    Query --> DB
    Query --> LLM[Gemini 2.5 Flash]
    LLM --> Answer([Final Answer])
```

---

## 🚀 Quick Start

### 1. Prerequisites
- **Google AI Studio API Key** (Gemini)
- **Supabase Project** (with `pgvector` enabled)

### 2. Environment Variables
Configure the following secrets in your Hugging Face Space:
| Variable | Description |
| :--- | :--- |
| `GOOGLE_GEMINI_API_KEY` | Your Gemini API Key from Google AI Studio |
| `DB_URL` | Your Supabase **Transaction Pooler** URL (Port 6543) |

### 3. Usage
- **Upload**: `POST /upload` - Send a PDF for processing.
- **Query**: `POST /query` - Ask questions about your documents.
- **Health**: `GET /health` - Check system status and version.

---

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **LLM / Embeddings**: Google Generative AI (Gemini 2.5 Flash)
- **Vector Database**: Supabase (PostgreSQL + pgvector)
- **PDF Engine**: pypdf + Custom Text Healer
- **Deployment**: Docker on Hugging Face Spaces

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with ❤️ for the AI Developer Community.  
  <b>Version 3.0-Final (Stable)</b>
</p>
