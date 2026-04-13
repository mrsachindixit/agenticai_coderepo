"""
LlamaIndex RAG — Compare with module01_raw/1.8_rag_basic
=========================================================

WHAT THIS SHOWS (capabilities unique to LlamaIndex):
  1. SimpleDirectoryReader  — auto-detects file types (txt, pdf, csv, etc.)
  2. VectorStoreIndex       — in-memory vector store with one line
  3. QueryEngine            — retrieval + synthesis in a single call
  4. Response metadata      — source nodes, scores, and provenance built-in

WHY THIS MATTERS vs the raw approach (module01_raw/1.8_rag_basic):
  • Raw approach: manually glob files, call /api/embed, store JSON, cosine math
  • LlamaIndex:   ~10 lines for the same pipeline, plus chunking/metadata free

SCENARIO: Same as module01 — ingest local text docs, ask a question,
          get a grounded answer with source attribution.

PREREQUISITES:
  pip install llama-index llama-index-llms-ollama llama-index-embeddings-ollama

RUN:
  ollama serve
  python module06_frameworks/6.1_llamaindex_rag.py
"""

import os
import sys

# ---------------------------------------------------------------------------
# 1. Configure LlamaIndex to use local Ollama (no OpenAI key needed)
# ---------------------------------------------------------------------------
from llama_index.core import (
    Settings,
    SimpleDirectoryReader,
    VectorStoreIndex,
)
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_EMBED = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

# Global settings — every LlamaIndex component picks these up automatically
Settings.llm = Ollama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE, request_timeout=120)
Settings.embed_model = OllamaEmbedding(model_name=OLLAMA_EMBED, base_url=OLLAMA_BASE)
Settings.chunk_size = 512
Settings.chunk_overlap = 64

# ---------------------------------------------------------------------------
# 2. Load documents — one line replaces the manual glob+read loop
#    (Reusing the same data dir as module01_raw/1.8_rag_basic)
# ---------------------------------------------------------------------------
DATA_DIR = os.path.join(
    os.path.dirname(__file__), "..", "module01_raw", "1.8_rag_basic", "data"
)

def build_index():
    """Load docs, chunk, embed, and return a queryable vector index."""
    documents = SimpleDirectoryReader(
        input_dir=DATA_DIR,
        required_exts=[".txt"],
        recursive=False,
    ).load_data()
    print(f"Loaded {len(documents)} document chunks from {DATA_DIR}")

    # One line: chunks → embeddings → in-memory vector store
    index = VectorStoreIndex.from_documents(documents, show_progress=True)
    return index

# ---------------------------------------------------------------------------
# 3. Query with built-in retrieval + synthesis
# ---------------------------------------------------------------------------

def query_index(index, question: str) -> str:
    """Ask the index a question and return a grounded answer."""
    query_engine = index.as_query_engine(similarity_top_k=3)
    response = query_engine.query(question)

    # --- Unique to LlamaIndex: source-node provenance ---
    print("\n--- Source nodes (provenance) ---")
    for node in response.source_nodes:
        score = f"{node.score:.3f}" if node.score else "n/a"
        snippet = node.text[:120].replace("\n", " ")
        print(f"  [{score}] {snippet}...")
    print("--- end sources ---\n")

    return str(response)


# ---------------------------------------------------------------------------
# 4. Main — mirrors the module01 RAG basic workflow
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== LlamaIndex RAG (compare with module01_raw/1.8_rag_basic) ===\n")

    idx = build_index()

    questions = [
        "How do agents use tools and memory?",
        "What is Sachin's full name?",
    ]

    for q in questions:
        print(f"Q: {q}")
        answer = query_index(idx, q)
        print(f"A: {answer}\n{'=' * 60}\n")
