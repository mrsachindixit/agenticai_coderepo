# Capstone 1 — SQLite Analyst Agent (Full)

This capstone provides a full‑featured teaching agent that demonstrates how to use agentic AI for database work with a local SQLite database.

Features
- Natural language → safe `SELECT` generation (via local model)
- Schema inspection
- Execute queries with an enforced safety policy
- Explain query plans (`EXPLAIN QUERY PLAN`)
- Summarize results for non‑technical users

Usage
1. Ensure the sample DB exists (the app will create it if missing):

```bash
python capstones/capstone1_sql_agent/cap1_app.py "List engineering employees with salary > 2000000"
```

Teaching Goals
- Show how to decompose user intent into tool calls (schema, generate SQL, execute, explain, summarize).
- Demonstrate safety controls (allow only `SELECT`, ban dangerous tokens).
- Show how to use model feedback to improve outputs and provide human‑readable summaries.

Files
- `cap1_app.py` — CLI entrypoint and demo runner
- `agent.py` — `SQLiteAnalystAgent` implementation (generation, execution, explain, summarize)
- `data/setup_db.py` + `data/sample.db` — sample data used by demonstrations
# Capstone 1 — SQLite Analyst Agent (Minimal)

**Goal:** Natural language → safe SQL → execute → summarize results using Ollama (llama3).

## Quick Start
```bash
python capstones/capstone1_sql_agent/cap1_app.py "List engineering employees with salary > 2,000,000"
```
