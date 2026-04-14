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

Treat each capstone as a student assignment.

The intended flow is:
1. Read the problem statement.
2. Implement your own solution first.
3. Use the repository implementation later as a reference for comparison and study.

### Assignment 1 — SQLite Analyst Agent
**Problem statement:** Build an agent that converts natural-language business questions into safe, executable SQL.

**Expected student outcome:** Query intent explanation, SQL execution result, and final business summary.

### Assignment 2 — Research Agent
**Problem statement:** Build a planner/executor-style research agent that gathers evidence and produces a concise synthesis.

**Expected student outcome:** Structured output with evidence-backed conclusions.

### Assignment 3 — Standalone RAG Agent
**Problem statement:** Build a standalone RAG pipeline that ingests local documents, builds an index, and answers grounded queries.

**Expected student outcome:** Reproducible ingest/index pipeline and grounded responses with source awareness.

Reference implementations are available in `capstones/` after you attempt the assignments independently.

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
