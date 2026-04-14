# 🤖 AgenticAI — Hands-On Code Companion

<p align="left">
	<img src="https://img.shields.io/badge/Local--First-Ollama-10b981?style=for-the-badge" alt="Local First" />
	<img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
	<img src="https://img.shields.io/badge/Frameworks-LangChain%20%7C%20LangGraph%20%7C%20DSPy%20%7C%20LlamaIndex-8b5cf6?style=for-the-badge" alt="Frameworks" />
</p>

Build real AI agents from scratch: tool-calling, RAG, memory, multi-agent systems, and production hardening — all running locally with Ollama.

---

## 🎯 Quick Navigation
- [🚀 Start Here (5 Minutes)](#-start-here-5-minutes)
- [🗺️ Learning Path](#-learning-path)
- [⚙️ Configuration](#️-configuration)
- [🏁 Capstone Assignments](#-capstone-assignments)
- [🎮 Playground](#-playground)
- [🧪 Testing and Sanity Checks](#-testing-and-sanity-checks)
- [🛠️ Troubleshooting](#️-troubleshooting)

---

## 🚀 Start Here (5 Minutes)

### 1) Install prerequisites
- Python 3.9+: https://python.org
- Ollama: https://ollama.ai

### 2) Create and activate a virtual environment
```bash
python -m venv .venv
```

Windows PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```

Linux / macOS:
```bash
source .venv/bin/activate
```

### 3) Install dependencies
```bash
pip install -r requirements.txt
```

### 4) Pull local models (minimum + full course set)

Minimum models to start:
```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

Additional models used across advanced samples:
```bash
ollama pull llama3.2:latest
ollama pull lfm2.5-thinking:latest
ollama pull llava
```

Check installed models anytime:
```bash
ollama list
```

### 5) Start Ollama
```bash
ollama serve
```

### 6) Run your first example
```bash
python capstones/capstone1_sql_agent/cap1_app.py "List engineering employees with salary > 2000000"
```

✅ You should see a natural-language answer backed by a live SQL query.

---

## 🗺️ Learning Path

Follow the modules in order — each one builds on the previous:

| Module | Topic |
|---|---|
| `module01_raw/` | LLM basics, tool calling, RAG intro, memory |
| `module02_basics/` | Chat objects, multi-modal, image analysis |
| `module03_langchain/` | LangChain agents, memory, LangGraph, middleware |
| `module04_production/` | Security, performance, monitoring, PII/bias |
| `module05_enterprise/` | MCP, A2A protocols, enterprise patterns |
| `module06_frameworks/` | LlamaIndex, DSPy, Embabel, cross-language comparison samples |
| `capstones/` | End-to-end projects combining all concepts |
| `playground/` | Interactive Streamlit app |
| `evaluations/` | Test suites and sanity checks |

---

## ⚙️ Configuration

All configuration is via environment variables. Defaults work out of the box.

| Variable | Default | Purpose |
|---|---|---|
| `OLLAMA_BASE` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.2` | Chat/completion model |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Embedding model |

Override in PowerShell:
```powershell
$env:OLLAMA_MODEL = "llama3.2"
$env:OLLAMA_EMBED_MODEL = "nomic-embed-text"
```

Override in Bash/zsh:
```bash
export OLLAMA_MODEL=llama3.2
export OLLAMA_EMBED_MODEL=nomic-embed-text
```

---

## 🏁 Capstone Assignments

Treat each capstone as a real-world project, not a toy demo.

The intended flow is:
1. Read the problem statement carefully.
2. Design and implement your own solution first.
3. Compare with the reference implementation in `capstones/` afterward.

---

### Assignment 1 — SQLite Analyst Agent

Build an end-to-end agent that lets non-technical business users ask plain-English questions against a **multi-table relational SQLite database** and receive safe, accurate, human-readable answers. Your agent should automatically discover the live schema (tables, columns, types, relationships, plus sample rows) so the LLM never hallucinates column names. It must generate SQL through a tightly prompted LLM call that returns structured JSON — not free text — and it should be capable of producing JOINs, aggregations, CTEs, and grouped queries, not just flat `SELECT *` statements. Before executing anything, the agent must enforce a read-only safety guard (allowlist + blocklist) and auto-append a `LIMIT` when missing. After execution, expose the query plan (`EXPLAIN QUERY PLAN`) for observability, and make a second LLM call to summarize the raw result into a concise business narrative. Seed your database with at least five interrelated tables (departments, employees with self-referencing managers, projects, a many-to-many junction, salary history) — a single flat table makes every query trivial and defeats the purpose. Deliver a CLI that accepts a natural-language question and prints the generated SQL, the intent explanation, the query plan, a result preview, and the business summary.

---

### Assignment 2 — Research Agent

Build a **planner/executor research assistant** that takes a high-level research prompt (e.g., *"Survey methods for low-resource named-entity recognition"*), decomposes it into a structured plan, executes each step using specialised tools, and produces an evidence-backed synthesis. The planner should be an LLM call that outputs a structured JSON plan with ordered steps (search, ingest, extract, synthesize) — include a deterministic fallback when the model returns invalid JSON. The executor should iterate over the plan, dispatch each step to the right tool, and **persist every intermediate result** to disk as timestamped JSON so the research trail is auditable. You will need at least three tools: a web/paper search tool (a placeholder with a production-shaped interface is fine), a PDF/text ingestion tool that walks a folder and extracts full text with structured metadata, and an LLM summarizer with a heuristic fallback when the model is unreachable. The crown jewel is a full **RAG pipeline** — chunk ingested documents, embed them into a Chroma vector store, load a similarity retriever, and answer follow-up questions grounded in document context with source citations. Design the embedding and chat functions as injectable parameters (not hard-coded) so you can write unit tests with deterministic fakes instead of depending on a live Ollama server. Deliver a CLI that prints the plan, executes every step, and writes all notes plus a final synthesis to `data/notes/`.

---

### Assignment 3 — Standalone RAG Agent

Build a **conversational RAG agent** that ingests a local collection of PDF documents, constructs a persistent vector index, and then enters an interactive chat loop where every answer is grounded in retrieved context and aware of prior conversation turns. The ingestion module should recursively walk a data directory, extract text page-by-page (handling empty pages gracefully), and carry source/title metadata through the entire pipeline. The index builder should split documents into configurable chunks, embed them with Ollama, store in Chroma, and persist to disk — expose CLI flags for chunk size, overlap, and directories so students can experiment with retrieval quality. Conversation memory is critical: maintain a rolling history so the agent can resolve follow-ups like *"Tell me more about that"* — without it every turn is independent and the agent feels broken. Each prompt should be composed of three clear blocks: system instructions (answer from context, cite sources), the concatenated retrieved chunks, and the conversation history. Use a `.env` file for all Ollama configuration and let CLI flags override env vars. Deliver three independently runnable entry points: (a) ingest PDFs, (b) build/update the index, (c) launch the interactive conversational agent.

---

> **Note:** Reference implementations are in `capstones/` — consult them **after** you attempt each assignment independently.

---

## 🎮 Playground

Use the interactive Streamlit app to experiment without writing code:

```bash
streamlit run playground/app.py
```

---

## 🧪 Testing and Sanity Checks

### Run all tests
```bash
pytest -q
```

### Run focused suites
```bash
pytest evaluations/tests_unit -q
pytest evaluations/tests_modules -q
pytest evaluations/tests_samples -q
```

`evaluations/tests_modules/` is the single-owner suite for module files (`module01_raw` -> `module05_enterprise`) with one self-contained test per source file.

---

## 🛠️ Troubleshooting

| Symptom | Fix |
|---|---|
| `Connection refused` | Run `ollama serve` |
| `Model not found` | Run `ollama pull llama3.2` then `ollama list` |
| Import errors | Run `pip install --upgrade -r requirements.txt` |
| Missing advanced model | Pull additional models as needed: `llama3.2:latest`, `lfm2.5-thinking:latest`, `llava` |

---

## 📝 Notes

- All code runs fully locally — no OpenAI API key or cloud account required.
