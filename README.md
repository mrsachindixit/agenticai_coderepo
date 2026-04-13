# AgenticAI Repo (Public Code)

This is the runnable code companion for the AgenticAI book.

## What this repo contains
- Core learning modules in `module01_raw/` to `module05_enterprise/`
- Capstone implementations in `capstones/`
- Playground app in `playground/`
- Evaluation suites in `evaluations/`
- Setup assets: `requirements.txt`, `setup_steps.md`, `.env.example`

## Prerequisites
- Python 3.9+
- Ollama installed and running: https://ollama.ai
- Git + terminal (`PowerShell`, `bash`, or `zsh`)

## Setup
```bash
pip install -r requirements.txt
ollama pull llama3
ollama pull nomic-embed-text
ollama serve
```

For full workshop setup notes, see `setup_steps.md`.

## Configuration
Environment variables (optional):
- `OLLAMA_BASE` (default: `http://localhost:11434`)
- `OLLAMA_MODEL` (default: `llama3`)
- `OLLAMA_EMBED_MODEL` (default: `nomic-embed-text`)

PowerShell example:
```powershell
$env:OLLAMA_MODEL = "llama3"
$env:OLLAMA_EMBED_MODEL = "nomic-embed-text"
```

Bash/zsh example:
```bash
export OLLAMA_MODEL=llama3
export OLLAMA_EMBED_MODEL=nomic-embed-text
```

## 🎯 Capstone projects

### 1) SQLite Analyst Agent (`capstone1_sql_agent`)
Natural language to safe SQL (`SELECT`-only), execution, explain plan, and summary.

Run:
```bash
python capstones/capstone1_sql_agent/cap1_app.py "List engineering employees with salary > 2000000"
```

### 2) Research Agent (`capstone2_research_agent`)
Planner/executor pattern with research-focused tools and PDF ingestion.

Run:
```bash
python capstones/capstone2_research_agent/run.py "Survey methods for low-resource NER"
```

### 3) Standalone RAG Agent (`capstone3_rag_agent`)
PDF ingestion + persistent vector index + conversational querying.

Build index:
```bash
python capstones/capstone3_rag_agent/build_index.py --data_dir capstones/capstone3_rag_agent/data --persist_dir capstones/capstone3_rag_agent/chroma_db
```

Query agent:
```bash
python capstones/capstone3_rag_agent/query_agent.py --persist_dir capstones/capstone3_rag_agent/chroma_db
```

## 🎮 Playground
Run the Streamlit app:
```bash
streamlit run playground/app.py
```

## 🧪 Evaluations & tests
Run all tests:
```bash
pytest -q
```

Run selected suites:
```bash
pytest evaluations/tests_unit -q
pytest evaluations/tests_rag -q
pytest evaluations/tests_agents -q
```

## Troubleshooting
- **Connection refused**: start Ollama with `ollama serve`
- **Model not found**: run `ollama pull llama3` and `ollama list`
- **Import issues**: `pip install --upgrade -r requirements.txt`
- **Advanced demo model tags**: some module scripts use `llama3.1:latest` or `lfm2.5-thinking:latest`; pull them if you run those specific demos.

## Notes
- Book manuscript and diagram-authoring assets are intentionally excluded from this public repo.
- Book content is maintained in the private `agenticai_book` repository.



