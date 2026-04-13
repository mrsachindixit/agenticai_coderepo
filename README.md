# 🤖 AgenticAI — Hands-On Code Companion

Build real AI agents from scratch: tool-calling, RAG, memory, multi-agent systems, and production hardening — all running locally with Ollama.

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
| `module06_frameworks/` | LlamaIndex, DSPy, Embabel — framework comparison samples |
| `capstones/` | End-to-end projects combining all concepts |
| `playground/` | Interactive Streamlit app |
| `evaluations/` | Test suites and sanity checks |

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

## 🎯 Capstone assignments

Treat each capstone as a practical assignment with a clear objective, deliverable, and run check.

### Assignment 1 · SQLite Analyst Agent
**Objective:** Convert natural-language business questions into safe, executable SQL.

**Deliverable:** An agent answer that includes query intent, SQL execution result, and summary.

**Run check:**
```bash
python capstones/capstone1_sql_agent/cap1_app.py "List engineering employees with salary > 2000000"
```

### Assignment 2 · Research Agent
**Objective:** Orchestrate planner/executor steps to produce a concise research output.

**Deliverable:** A structured response based on tool-driven evidence collection.

**Run check:**
```bash
python capstones/capstone2_research_agent/run.py "Survey methods for low-resource NER"
```

### Assignment 3 · Standalone RAG Agent
**Objective:** Build and query a local retrieval index over your documents.

**Deliverable:** Reproducible ingest/index workflow and grounded answers from indexed content.

**Run check (step 1: build index):**
```bash
python capstones/capstone3_rag_agent/build_index.py --data_dir capstones/capstone3_rag_agent/data --persist_dir capstones/capstone3_rag_agent/chroma_db
```

**Run check (step 2: query):**
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
pytest evaluations/tests_modules -q
pytest evaluations/tests_samples -q
```

`evaluations/tests_modules/` is the single-owner suite for module files (`module01_raw` → `module05_enterprise`) with one self-contained test per source file.

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

- All code runs fully locally — no OpenAI API key or cloud account required.

