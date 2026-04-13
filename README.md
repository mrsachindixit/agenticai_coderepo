# AgenticAI Repo (Public Code)

This repository contains the runnable code and setup assets that accompany the AgenticAI book.

## Included
- Python source code in `module01_raw/` to `module05_enterprise/`
- Capstone implementations in `capstones/`
- Playground app in `playground/`
- Evaluations/tests in `evaluations/`
- Setup and dependency files (`setup_steps.md`, `requirements.txt`)

## Quick Start
1. Install Python 3.9+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Follow full setup instructions in `setup_steps.md`

## Notes
- Book manuscript/diagram authoring files are intentionally excluded.
- This repo is designed to be public-safe as the code companion.

---

## 🎯 Capstone Projects

### 1 — SQLite Analyst Agent (Full)

An educational, production-like agent demonstrating agentic AI for database tasks.

**Features:**
- Schema discovery and column introspection
- Natural language to safe SELECT generation (model-assisted)
- Query execution with enforced safety (no DDL/DML, read-only)
- Query plan explanation (EXPLAIN QUERY PLAN)
- Result summarization for non-technical stakeholders

**Run the demo:**

```bash
python capstones/capstone1_sql_agent/cap1_app.py "List engineering employees with salary > 2000000"
```

**Files:**
- `capstones/capstone1_sql_agent/agent.py` — core SQLiteAnalystAgent class
- `capstones/capstone1_sql_agent/cap1_app.py` — CLI driver
- `capstones/capstone1_sql_agent/README.md` — teaching guide
- `capstones/capstone1_sql_agent/data/employees.csv` — sample dataset

---

### 2 — Multi‑Agent Enterprise Workflow (Minimal)

Planner to Executor pattern for task decomposition and execution.

**Features:**
- Planner agent breaks down user request into steps
- Executor agent carries out each step and reports results
- Checkpoint memory for recovery

**Run the demo:**

```bash
python capstones/capstone2_multi_agent/run.py "Design a safe SQL agent for HR salary analytics"
```

**Files:**
- `capstones/capstone2_multi_agent/agents/planner.py` — planner implementation
- `capstones/capstone2_multi_agent/agents/executor.py` — executor implementation
- `capstones/capstone2_multi_agent/run.py` — main orchestration

---

### 3 — Minimal RAG API (FastAPI)

Expose a lightweight RAG endpoint using the Module 2 index.

**Features:**
- Retrieve top-k documents by similarity
- Augment LLM prompts with context
- JSON API for client integration

**Setup & run:**

```bash
# Build the small demo index (one-time)
python module01_raw/1.8_rag_basic/build_index.py

# Start the RAG API
uvicorn capstones/capstone3_rag_api/app:app --reload --port 8080
```

**Test the endpoint:**

```bash
curl -X POST http://localhost:8080/ask \
   -H "Content-Type: application/json" \
   -d '{"question": "How do agents use tools and memory?"}'
```

**Files:**
- `capstones/capstone3_rag_api/app.py` — FastAPI server
- `module01_raw/1.8_rag_basic/index.json` — pre-built index

---

## 🎮 Running the Playground

**Streamlit UI** for interactive chat and RAG exploration.

```bash
streamlit run playground/app.py
```

- **Chat mode:** talk to the LLM with a custom system prompt
- **RAG Explorer:** search the built index or upload documents

---

### Quick Start
### Prerequisites
- **Ollama** installed and running (see [ollama.ai](https://ollama.ai))
- **Python 3.9+**
- Standard dev tools:IDE `git`, `pip`, `bash`/`PowerShell`
### Setup
```bash
# 1) Start Ollama server (if not already running)
ollama serve
# (in another terminal)
# 2) Pull recommended models
ollama pull llama3
ollama pull nomic-embed-text

# 3) Install Python dependencies
pip install -r requirements.txt
```
All examples and capstones use the root `requirements.txt` for dependencies.
**"Connection refused" errors:**

- Ensure Ollama is running: `ollama serve` in a separate terminal
- Verify Ollama is accessible at `http://localhost:11434` (configurable via `OLLAMA_BASE` env var)

**"Model not found" errors:**
  
- Pull the model: `ollama pull llama3`
- Check installed models: `ollama list`
- Switch default model: `export OLLAMA_MODEL=lfm2.5-thinking:latest` (if installed)

**Import errors (LangChain, etc.):**
  
- Reinstall dependencies: `pip install --upgrade -r requirements.txt`
- Create a fresh virtual environment: `python -m venv venv && source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
## 📝 Model Compatibility

By default, this course uses **`llama3`**. If you prefer an alternative:

```bash
# Use a faster model
ollama pull lfm2.5-thinking:latest
export OLLAMA_MODEL=lfm2.5-thinking:latest

# Use a lightweight model
ollama pull gemma3:2b
export OLLAMA_MODEL=gemma3:2b
```
Note: Larger models (7B+) produce better results but require more VRAM. Start with `llama3` or `gemma3:2b` on modest hardware.

---
## ⚙️ Configuration

**Environment variables:**

- `OLLAMA_BASE` — Ollama API endpoint (default: `http://localhost:11434`)
- `OLLAMA_MODEL` — chat model name (default: `llama3`)
- `OLLAMA_EMBED_MODEL` — embedding model (default: `nomic-embed-text`)

Example:

```bash
export OLLAMA_MODEL=llama2
export OLLAMA_EMBED_MODEL=nomic-embed-text
python capstones/capstone1_sql_agent/cap1_app.py "Show me senior engineers"
```

---

## 🧪 Evaluations & Tests

The `evaluations/` folder contains comprehensive tests:

- **`tests_unit/`** — unit tests for helpers and agent components
- **`tests_prompts/`** — prompt regression (definition checks, grammar validation)
- **`tests_rag/`** — RAG index building, retrieval quality
- **`tests_agents/`** — agent controller behavior and JSON parsing

**Run all tests locally:**

```bash
pytest -q
```

**Run a specific test suite:**

```bash
pytest evaluations/tests_unit -q
pytest evaluations/tests_rag -q
```



