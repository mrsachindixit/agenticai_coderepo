# 🤖 AgenticAI — Hands-On Code Companion

Build real AI agents from scratch: tool-calling, RAG, memory, multi-agent systems, and production hardening — all running locally with Ollama.

> This repo accompanies the **AgenticAI** book. Every module maps directly to a chapter.

---

## 🚀 Start here (5 minutes)

**Step 1 — Install prerequisites**
- Python 3.9+: https://python.org
- Ollama: https://ollama.ai

**Step 2 — Create and activate a virtual environment**

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

**Step 3 — Install dependencies**

```bash
pip install -r requirements.txt
```

**Step 4 — Pull local models**

```bash
ollama pull llama3
ollama pull nomic-embed-text
```

**Step 5 — Start Ollama**

```bash
ollama serve
```

**Step 6 — Run your first example**

```bash
python capstones/capstone1_sql_agent/cap1_app.py "List engineering employees with salary > 2000000"
```

You should see a natural-language answer backed by a live SQL query. If that works, you're ready.

---

## 🗺️ Learning path

Follow the modules in order — each one builds on the previous:

| Module | Topic |
|---|---|
| `module01_raw/` | LLM basics, tool calling, RAG intro, memory |
| `module02_basics/` | Chat objects, multi-modal, image analysis |
| `module03_langchain/` | LangChain agents, memory, LangGraph, middleware |
| `module04_production/` | Security, performance, monitoring, PII/bias |
| `module05_enterprise/` | MCP, A2A protocols, enterprise patterns |
| `capstones/` | End-to-end projects combining all concepts |
| `playground/` | Interactive Streamlit app |
| `evaluations/` | Test suites and sanity checks |
| `scripts/` | Reusable smoke test runner |

---

## ⚙️ Configuration

All configuration is via environment variables. Defaults work out of the box with no changes needed.

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

## 🎯 Capstone projects

### 1 · SQLite Analyst Agent
> Natural language → safe SQL → execution → explain plan → summary

```bash
python capstones/capstone1_sql_agent/cap1_app.py "List engineering employees with salary > 2000000"
```

### 2 · Research Agent
> Planner/executor workflow with research tools and PDF ingestion

```bash
python capstones/capstone2_research_agent/run.py "Survey methods for low-resource NER"
```

### 3 · Standalone RAG Agent
> Ingest documents, build a persistent vector index, and query conversationally

Build index first:
```bash
python capstones/capstone3_rag_agent/build_index.py --data_dir capstones/capstone3_rag_agent/data --persist_dir capstones/capstone3_rag_agent/chroma_db
```

Then query:
```bash
python capstones/capstone3_rag_agent/query_agent.py --persist_dir capstones/capstone3_rag_agent/chroma_db
```

---

## 🎮 Playground

An interactive Streamlit app to experiment with agent features without writing code:

```bash
streamlit run playground/app.py
```

---

## 🧪 Testing and sanity checks

### Run tests

All tests:
```bash
pytest -q
```

Focused suites:
```bash
pytest evaluations/tests_unit -q
pytest evaluations/tests_rag -q
pytest evaluations/tests_agents -q
```

### Smoke test (run this before every session)

Quick check — versions, files, imports, compile:
```bash
python scripts/smoke_test.py
```

With pytest collection + Ollama endpoint check:
```bash
python scripts/smoke_test.py --with-pytest --with-ollama
```

Full deterministic sample suite:
```bash
python scripts/smoke_test.py --with-samples
```

Live execution checks (uses LLM, takes longer):
```bash
python scripts/smoke_test.py --with-live-samples --samples-timeout 180
```

List all configured sample checks:
```bash
python scripts/smoke_test.py --list-samples
```

PowerShell wrapper:
```powershell
.\scripts\smoke_test.ps1 -WithPytest -WithOllama -WithSamples
```

---

## 🛠️ Troubleshooting

| Symptom | Fix |
|---|---|
| `Connection refused` | Run `ollama serve` |
| `Model not found` | Run `ollama pull llama3` then `ollama list` |
| Import errors | Run `pip install --upgrade -r requirements.txt` |
| Missing advanced model | Some demos need `llama3.1:latest`, `lfm2.5-thinking:latest`, or `llava` — pull on demand |

---

## 📝 Notes

- Book manuscript and diagram assets are in the private `agenticai_book` repository and are intentionally excluded here.
- All code runs fully locally — no OpenAI API key or cloud account required.

