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
ollama pull llama3
ollama pull nomic-embed-text
```

Additional models used across advanced samples:
```bash
ollama pull llama3.1:latest
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
| `OLLAMA_MODEL` | `llama3` | Chat/completion model |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Embedding model |

Override in PowerShell:
```powershell
$env:OLLAMA_MODEL = "llama3"
$env:OLLAMA_EMBED_MODEL = "nomic-embed-text"
```

Override in Bash/zsh:
```bash
export OLLAMA_MODEL=llama3
export OLLAMA_EMBED_MODEL=nomic-embed-text
```

---

## 🏁 Capstone Assignments

Treat each capstone as a **professional-grade student assignment**, not a toy demo.

The intended flow is:
1. Read the full problem statement and requirements below.
2. Implement your own solution first — meet every requirement before looking at the reference.
3. Use the repository implementation later as a reference for comparison and study.

---

### Assignment 1 — SQLite Analyst Agent

**Scenario.** You are building an internal analytics assistant for a company whose data lives in a multi-table SQLite database. Business users type plain-English questions; your agent must turn them into safe SQL, execute the query, and return a human-readable summary.

**Functional requirements:**

| # | Requirement | Why it matters |
|---|-------------|---------------|
| 1 | **Schema introspection** — On startup the agent must automatically discover every table, column name, column type, and primary/foreign key relationships. It should also fetch a few sample rows per table so the LLM has concrete examples. | Without live schema context the model hallucinates column names. |
| 2 | **NL → SQL generation** — Send the discovered schema plus the user's natural-language question to the LLM. The prompt must instruct the model to return **structured JSON** (`{"sql": "...", "explanation": "..."}`) — not free text. Support JOINs, GROUP BY, HAVING, ORDER BY, CTEs, and aggregates. | Forces students to design a tight system prompt and parse structured output. |
| 3 | **SQL safety guard** — Before executing any generated query, validate it against an allowlist (must start with `SELECT`) **and** a blocklist of dangerous tokens (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `ATTACH`, `PRAGMA`, `CREATE`, `VACUUM`, `--`, `;`). Reject anything that fails. | Real-world agents must never run destructive SQL from user input. |
| 4 | **Auto-limit** — If the generated SQL does not already contain a `LIMIT` clause, append one (e.g., `LIMIT 100`) before execution. | Prevents accidental full-table scans on large databases. |
| 5 | **Query plan explanation** — After execution, run `EXPLAIN QUERY PLAN` on the same SQL and include the output so users (or instructors) can inspect efficiency. | Teaches students that observability matters even in LLM-based pipelines. |
| 6 | **Result summarization** — Make a **second** LLM call that receives the column names and first N result rows and produces a 2–4 sentence plain-English business summary (e.g., "3 engineering employees earn above ₹20 L …"). | Demonstrates multi-step LLM orchestration — generate SQL, then summarize results. |
| 7 | **Rich test database** — Seed at least five interrelated tables (departments, employees with manager self-reference, projects, a many-to-many employee_projects junction, salary_history). Populate with enough rows that JOIN-based queries are meaningful. Optionally support CSV import. | A single flat table makes every query trivial; relational depth forces real SQL. |

**Deliverable:** A CLI that accepts a natural-language question as an argument and prints: the generated SQL, the intent explanation, the query plan, a result preview, and the business summary.

---

### Assignment 2 — Research Agent

**Scenario.** You are building a research-automation assistant that takes a high-level research prompt (e.g., *"Survey methods for low-resource named-entity recognition"*), breaks it into a structured plan, executes each step with specialised tools, and produces an evidence-backed synthesis.

**Functional requirements:**

| # | Requirement | Why it matters |
|---|-------------|---------------|
| 1 | **Planner agent** — An LLM-powered planner that reads the user prompt and produces a **structured JSON plan** with `title`, `objectives`, and an ordered `steps` list. Each step must include an `id`, an `action` type (search / ingest / extract / synthesize), a brief `description`, and a `tools` suggestion list. Include a deterministic fallback plan if the LLM returns invalid JSON. | Separating planning from execution is the core pattern of planner/executor architectures. |
| 2 | **Executor agent** — A class that iterates over the plan's steps, dispatches each step to the matching tool, and collects structured results. Each step result must be **persisted** to disk as a timestamped JSON file (e.g., `data/notes/step_1_1713100000.json`). | Teaches state management and auditability — real agents must persist intermediate work. |
| 3 | **Tool: web/paper search** — A search tool that accepts a query and returns a list of `{title, url, snippet}` dicts. (A placeholder returning synthetic results is acceptable, but the interface must be production-shaped so it's swappable for a live API like arXiv or Semantic Scholar.) | Students learn to design tool interfaces that decouple implementation from integration. |
| 4 | **Tool: PDF/text ingest** — Walk a folder, extract full text from every PDF (via PyPDF or equivalent) and plain-text file, and return structured metadata per file (`file`, `path`, `length`, `text`). | Document ingestion is the foundation of any RAG or research pipeline. |
| 5 | **Tool: LLM summarizer** — Accept raw text, call the LLM with a summarization system prompt, and return a 3–5 sentence summary. Include a heuristic fallback (first N sentences) when the LLM is unreachable. | Graceful degradation is a production skill. |
| 6 | **RAG pipeline** — Build a full retrieval-augmented generation pipeline: chunk documents with `RecursiveCharacterTextSplitter` (configurable `chunk_size` / `chunk_overlap`), embed chunks with Ollama (`nomic-embed-text`), persist to a Chroma vector store, load a similarity retriever (k = 4), and answer questions with document context + source citations. | This is the heart of the capstone — students must wire ingestion, embedding, retrieval, and generation end-to-end. |
| 7 | **Dependency injection for testing** — The embedding function and chat function must be **injectable parameters**, not hard-coded. This lets unit tests supply deterministic fakes without hitting Ollama. | Without DI the entire test suite depends on a running model server. |
| 8 | **Unit tests** — Write at least two tests: (a) build an index from a temp folder, load a retriever, and verify `answer_question` returns the mocked answer; (b) monkeypatch the chat function and verify `summarize_all` produces the expected output. | Proves the pipeline works and that DI is correctly wired. |

**Deliverable:** A CLI that accepts a research prompt, prints the generated plan, executes every step, and writes all intermediate notes plus a final synthesis to `data/notes/`.

---

### Assignment 3 — Standalone RAG Agent

**Scenario.** You are building a **conversational** RAG agent that ingests a local collection of PDF documents, builds a persistent vector index, and then enters an interactive chat loop where each answer is grounded in the retrieved document context and aware of the prior conversation turns.

**Functional requirements:**

| # | Requirement | Why it matters |
|---|-------------|---------------|
| 1 | **PDF ingestion module** — Recursively walk a data directory, extract text from every PDF page (skip empty pages gracefully), and wrap each document in a `Document` object carrying `source` and `title` metadata. Support a standalone CLI mode for testing ingestion independently. | Separating ingestion from indexing keeps the pipeline modular and debuggable. |
| 2 | **Index builder** — Split documents with `RecursiveCharacterTextSplitter` (configurable `chunk_size`, `chunk_overlap`), embed with Ollama (`nomic-embed-text`), store in Chroma, and persist to disk. Preserve chunk-level metadata (source file, chunk index). Expose CLI flags for `--data_dir`, `--persist_dir`, `--chunk_size`, `--chunk_overlap`. | Students must understand that chunking strategy directly affects retrieval quality. |
| 3 | **Similarity retriever** — Load the persisted Chroma DB, wrap it in a similarity retriever (k = 4), and return the top-k document chunks for a given query. | The retriever is the bridge between the static index and the live agent. |
| 4 | **Conversational memory** — Maintain a rolling list of `(user_question, assistant_answer)` tuples. Inject the history into every prompt so the agent can resolve follow-up questions (e.g., "Tell me more about that"). | Without memory every turn is independent — this is a critical agent capability. |
| 5 | **Prompt construction** — Build each LLM call with three blocks: system instructions (answer from context, cite sources), concatenated retrieved chunks, and conversation history. Keep the prompt template clean and inspectable. | Shows students how prompt engineering works in a RAG-aware agent loop. |
| 6 | **Source-aware answers** — The system prompt must instruct the model to **cite the source file path** when helpful. | Grounding + citations are what distinguish RAG from plain chat. |
| 7 | **Interactive chat loop** — After the index is built, launch a REPL (`You: … / Agent: …`) that accepts questions, retrieves, generates, prints, and loops until the user types `exit`. | A running demo is more convincing than a single-shot script. |
| 8 | **Environment configuration** — Use a `.env` file (with a `.env.example` checked in) for `OLLAMA_BASE`, `OLLAMA_MODEL`, and `OLLAMA_EMBED_MODEL`. CLI flags should override env vars. | Teaches 12-factor-style configuration — no secrets hard-coded. |

**Deliverable:** Three runnable entry points: (a) ingest PDFs, (b) build/update the index, (c) launch the interactive conversational agent — each usable independently via CLI.

---

> **Note:** Reference implementations are available in `capstones/` — consult them **after** you have attempted each assignment independently.

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
| `Model not found` | Run `ollama pull llama3` then `ollama list` |
| Import errors | Run `pip install --upgrade -r requirements.txt` |
| Missing advanced model | Pull additional models as needed: `llama3.1:latest`, `lfm2.5-thinking:latest`, `llava` |

---

## 📝 Notes

- All code runs fully locally — no OpenAI API key or cloud account required.
