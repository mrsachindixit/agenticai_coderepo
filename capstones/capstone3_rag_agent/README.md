Capstone 3 — Standalone RAG Agent (Professional Tutorial)

This project is a standalone, production-oriented Retrieval-Augmented Generation (RAG) capstone. It ingests local PDFs, builds a persistent vector index (Chroma), and provides a conversational RAG agent you can run locally.

Overview
- Ingest PDFs from a `data/` folder and extract text.
- Split documents into chunks and create embeddings.
- Persist an index with Chroma for fast retrieval.
- Run a conversational agent backed by retrieved context.

Features
- Clear, step-by-step tutorial and runnable scripts.
- Uses `langchain` with `Chroma` vector store.
- Uses Ollama for embeddings and chat. Configure `OLLAMA_BASE`/`OLLAMA_MODEL` or run a local Ollama instance.

Quick start
1. Create a Python 3.10+ virtual environment.

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Put PDFs you want indexed into `capstones/capstone3_rag_agent/data/`.
3. Configure Ollama (no OpenAI API key needed): set `OLLAMA_BASE`, `OLLAMA_MODEL`, and `OLLAMA_EMBED_MODEL` in your environment or run Ollama locally.
4. Build the index (uses Ollama embeddings):

```bash
python capstones/capstone3_rag_agent/build_index.py --data_dir capstones/capstone3_rag_agent/data --persist_dir capstones/capstone3_rag_agent/chroma_db
```

5. Run the conversational agent (uses Ollama chat):

```bash
python capstones/capstone3_rag_agent/query_agent.py --persist_dir capstones/capstone3_rag_agent/chroma_db
```

Files
- `ingest_pdfs.py` — extract text from PDFs and return Document objects.
- `build_index.py` — split text, create embeddings with Ollama, and persist Chroma DB.
- `query_agent.py` — conversational loop using Ollama chat + Chroma retriever.
- `utils.py` — small helpers (env loading, logging).
- `.env.example` — example env variables.
- Root `requirements.txt` — project dependencies.

Design notes and recommendations
- Use `Chroma`'s `persist_directory` to keep index between runs.
- For production, run ingestion as a batch job and only update on changes.
- Consider an API wrapper (FastAPI) if you want remote access.

Security & cost
- Using `OpenAI` requires API key; monitor usage and set rate limits or local models for cost control.
- For sensitive PDFs, ensure local-only storage and strict access controls.

Contact
This tutorial was created as part of the AgenticAI capstone collection. If you'd like, I can:
- Add a FastAPI wrapper
- Add Dockerfiles and CI steps
- Add automated tests to validate index integrity

---
Proceed to the code examples in this folder to run or customize the RAG agent.
