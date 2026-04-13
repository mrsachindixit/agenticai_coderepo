# AgenticAI Repo (Public Code)

Code companion for the AgenticAI book — designed for students to learn by running real examples.

---

## 🚀 Start here (5 minutes)

1. Install Python 3.9+ and Ollama: https://ollama.ai

2. Create and activate a virtual environment:

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

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Pull required local models:

```bash
ollama pull llama3
ollama pull nomic-embed-text
```

5. Start Ollama:

```bash
ollama serve
```

6. Run a first example:

```bash
python capstones/capstone1_sql_agent/cap1_app.py "List engineering employees with salary > 2000000"
```

---

## 🧭 Repo map

- `module01_raw/` → `module05_enterprise/` — progressive learning modules
- `capstones/` — end-to-end projects
- `playground/` — Streamlit app for interactive experimentation
- `evaluations/` — test suites and sanity checks
- `scripts/` — reusable smoke test command-line tools

---

## ⚙️ Configuration

Environment variables (optional):
- `OLLAMA_BASE` (default: `http://localhost:11434`)
- `OLLAMA_MODEL` (default: `llama3`)
- `OLLAMA_EMBED_MODEL` (default: `nomic-embed-text`)

PowerShell:
```powershell
$env:OLLAMA_MODEL = "llama3"
$env:OLLAMA_EMBED_MODEL = "nomic-embed-text"
```

Bash/zsh:
```bash
export OLLAMA_MODEL=llama3
export OLLAMA_EMBED_MODEL=nomic-embed-text
```

---

## 🎯 Capstone projects

### 1) SQLite Analyst Agent (`capstone1_sql_agent`)
Natural language → safe SQL (`SELECT`-only) → execution → explain plan → summary.

```bash
python capstones/capstone1_sql_agent/cap1_app.py "List engineering employees with salary > 2000000"
```

### 2) Research Agent (`capstone2_research_agent`)
Planner/executor workflow with research-focused tools and PDF ingestion.

```bash
python capstones/capstone2_research_agent/run.py "Survey methods for low-resource NER"
```

### 3) Standalone RAG Agent (`capstone3_rag_agent`)
Build a persistent index and run conversational retrieval.

Build index:
```bash
python capstones/capstone3_rag_agent/build_index.py --data_dir capstones/capstone3_rag_agent/data --persist_dir capstones/capstone3_rag_agent/chroma_db
```

Query agent:
```bash
python capstones/capstone3_rag_agent/query_agent.py --persist_dir capstones/capstone3_rag_agent/chroma_db
```

---

## 🎮 Playground

```bash
streamlit run playground/app.py
```

---

## 🧪 Testing and sanity checks

### Standard tests
Run all:
```bash
pytest -q
```

Run selected:
```bash
pytest evaluations/tests_unit -q
pytest evaluations/tests_rag -q
pytest evaluations/tests_agents -q
```

### Reusable smoke command (recommended)
Quick smoke (versions + files + imports + compile check):
```bash
python scripts/smoke_test.py
```

Add pytest collection checks:
```bash
python scripts/smoke_test.py --with-pytest
```

Add Ollama endpoint check:
```bash
python scripts/smoke_test.py --with-ollama
```

Run deterministic sample-suite sanity:
```bash
python scripts/smoke_test.py --with-samples
```

Run live sample execution checks (LLM/tooling, longer):
```bash
python scripts/smoke_test.py --with-live-samples --samples-timeout 180
```

List configured sample checks:
```bash
python scripts/smoke_test.py --list-samples
```

PowerShell wrapper:
```powershell
.\scripts\smoke_test.ps1 -WithPytest -WithOllama -WithSamples
```

---

## 🛠️ Troubleshooting

- **Connection refused**: start Ollama using `ollama serve`
- **Model not found**: run `ollama pull llama3` and `ollama list`
- **Import issues**: run `pip install --upgrade -r requirements.txt`
- **Advanced model tags**: some demos use `llama3.1:latest`, `lfm2.5-thinking:latest`, or `llava`; pull them only when needed.

---

## 📝 Notes

- Book manuscript/diagram authoring assets are intentionally excluded from this public repo.
- Book content is maintained in the private `agenticai_book` repository.
