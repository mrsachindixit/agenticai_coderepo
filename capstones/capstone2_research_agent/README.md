# Capstone 2 — Research Agent (Detailed Tutorial)

This capstone demonstrates how to build a research assistant agent that can:
- Discover literature (web/arXiv/search)
- Ingest and read PDFs
- Extract and store structured notes and citations
- Answer questions using retrieved evidence
- Synthesize summaries and draft sections for papers

This is a teaching-quality, production-minded example. It favors clear interfaces and small, composable components you can extend.

Contents
- `run.py` — CLI entrypoint for quick experiments
- `agents/planner.py` — high-level planning agent (produces structured research plans)
- `agents/executor.py` — executes plan steps and calls tools
- `tools/` — lightweight tool wrappers (web search, PDF ingestion, summarizer)
- `data/` — place for PDF files, index, and notes
- `requirements.txt` — capstone-specific dependencies

Quick start
1. Create a virtualenv and install deps:

```bash
python -m venv .venv
# Windows PowerShell activate
.\.venv\Scripts\Activate.ps1
pip install -r capstones/capstone2_research_agent/requirements.txt
```

2. Place PDFs in `capstones/capstone2_research_agent/data/pdfs/` or run the built-in literature search.

3. Run an experiment:

```bash
python capstones/capstone2_research_agent/run.py "Survey methods for low-resource NER"
```

Design overview
- Planner: turns a high-level research prompt into a short plan (search, read, extract, synthesize).
- Executor: runs each step using tools. Tools are small and easily replaceable.
- Notes store: simple JSON/SQLite store for extracted highlights, metadata, and citations.

Extending the project
- Replace the `tools.search` with an API-backed search (Semantic Scholar, Crossref, arXiv).
- Replace `tools.summarize` with calls to an LLM (Ollama) or a local model.
- Add a UI (Streamlit / FastAPI) to drive experiments and review notes.

Security & reproducibility
- Keep PDF sources and indexes in `data/` and version control only metadata and small samples.
- For heavy workloads, run ingestion/indexing as batch jobs and persist vector stores externally.

Next steps
- Run the example and review `data/notes.json` created by the agent.
- Ask me to add a `FastAPI` wrapper or Dockerfile for reproducible runs.
