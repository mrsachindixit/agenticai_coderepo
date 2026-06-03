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
ollama pull llama3.1
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

Follow the modules in order — each one builds on the previous. The arc moves from a single raw LLM call all the way to enterprise-grade protocols and alternative frameworks.

---

### Module 01 · Raw LLM Interactions
*Start here. No frameworks — just Python + Ollama. You learn what an LLM actually does at the API level.*

| File | What it teaches |
|---|---|
| `1.1_hello_llm.py` | Your first LLM call — send a prompt, read a response |
| `1.2_chat_io.py` | Interactive chat loop with streaming and turn history |
| `1.3_tool_single.py` | Give the LLM one tool and let it decide when to use it |
| `1.4_memory_sim.py` | Simulate short-term memory by managing the message list yourself |
| `1.5_code_gen.py` | Prompt the LLM to write Python, then execute the output safely |
| `1.6_regex_bot.py` | Deterministic response routing via regex — no LLM for intent |
| `1.7_nlp_bot.py` | Lightweight NLP intent detection as a fallback before the LLM |
| `1.8_tools_multi.py` | Multiple tools in one agent loop — LLM picks which to call |
| `1.9_db_agent_sqlite.py` | Full agent that translates natural language to SQL and executes it |
| `1.10_rag_basic/` | Retrieval-Augmented Generation from scratch: embed, store, retrieve, answer |

---

### Module 02 · LangChain Primitives
*Introduce LangChain's chat model objects. Same concepts as Module 01 but now using the framework's building blocks — notice how the pattern maps 1:1.*

| File | What it teaches |
|---|---|
| `2.1_chat_obj_llm.py` | `ChatOllama` object replaces raw `requests` — same call, cleaner interface |
| `2.2_image_analysis.py` | Multi-modal input: pass an image to a vision-capable LLM |
| `2.3_chat_obj_tool_single.py` | `model.bind_tools([...])` — single tool, same loop as `1.3` but framework-native |
| `2.4_chat_obj_tool_multi.py` | Multiple tools bound to the model; LangChain handles the dispatch loop |

---

### Module 03 · LangChain Agents & LangGraph
*The framework takes over orchestration. You declare agents, graphs, and memory — the framework runs the loop.*

| File | What it teaches |
|---|---|
| `3.1_tool_call.py` | LangChain `@tool` decorator and `.invoke()` — the declarative equivalent of `1.3` |
| `3.2_agent_simple.py` | `create_react_agent` — hand the LLM a toolset and let the ReAct loop run |
| `3.3_memory_checkpoint_langchain.py` | Persist conversation state with `MemorySaver` checkpoints |
| `3.4_multi_agent.py` | Two agents collaborating: one plans, one executes |
| `3.5_lg_basic.py` | First LangGraph: nodes, edges, and `StateGraph` — graphs replace imperative loops |
| `3.6_agent_middleware_langchain.py` | Intercept agent steps with middleware: logging, auth, rate-limit |
| `3.7_multi_tool_call.py` | LLM makes multiple tool calls in a single turn |
| `3.8_agent_multi_tool.py` | Agent with a full tool registry; LangChain resolves calls automatically |
| `3.9_agent_tools_seq_basic.py` | Force sequential tool execution — output of one feeds into the next |
| `3.10_memory_checkpoint_langchain_1.py` | Persistent memory across sessions using thread IDs |
| `3.11_multi_agent.py` | Supervisor pattern: one agent routes tasks to specialist sub-agents |
| `3.12_rag_langchain.py` | Full RAG pipeline using LangChain retriever + chat chain |
| `3.13_agent_tools_with_tool_seq.py` | Tools that themselves trigger further tool calls (tool chaining) |
| `3.14_multi_tool_orchestration.py` | Parallel and conditional tool fan-out in a single agent run |
| `3.15_langgraph_coordinator.py` | LangGraph coordinator node that routes to worker subgraphs |
| `3.16_lg_pause_resume_hitl.py` | Human-in-the-loop: graph pauses mid-run and waits for human approval |

---

### Module 04 · Production Concerns
*Your agent works in a notebook — now make it safe, observable, and resilient. Each file adds one production dimension.*

| File | Category | What it teaches |
|---|---|---|
| `4.0_security_attacks_demo.py` | Attack Labs (Recap) | Recap lab: run multiple prompt/data/tool attack simulations side-by-side |
| `4.1_security_basic.py` | Security Controls | Input validation and prompt injection defence without a library |
| `4.2_security_guardrails_ai.py` | Security Controls | Drop-in guardrails using the `guardrails-ai` framework |
| `4.3_performance_basic.py` | Performance | Response caching and timeout handling to reduce latency |
| `4.4_performance_production.py` | Performance | Retry logic with exponential back-off using `tenacity` |
| `4.5_monitoring_basic.py` | Observability | Structured logging of every LLM call: latency, tokens, outcome |
| `4.6_monitoring_opentelemetry.py` | Observability | OpenTelemetry traces and spans — agent calls become distributed traces |
| `4.7_pii_basic.py` | Data Protection | Detect and redact PII with regex before data reaches the LLM |
| `4.8_pii_presidio.py` | Data Protection | Production PII detection with Microsoft Presidio NER |
| `4.9_pii_langchain.py` | Data Protection | Presidio wired into a LangChain chain as a preprocessing step |
| `4.10_bias_guardrails.py` | Safety & Policy | Detect biased or harmful outputs and block or flag the response |
| `4.11_prompt_caching_anthropic.py` | Performance | Prompt caching in practice with cache-on/cache-off comparison and usage metrics |
| `4.12_tool_auth_basic.py` | Security Controls | Basic tool authorization via scopes (allow/deny behavior) |
| `4.13_mcp_tool_auth_basic.py` | Security Controls | MCP-style tool authorization pattern with scope checks |
| `4.14_prompt_perf_basics.py` | Performance | Prompt focus, role design, and memory cleanup effects on latency/tokens |
| `4.15_adaptive_model_routing.py` | Performance | Route simple vs complex queries to fast vs strong models |
| `4.16_parallel_tools_timeout.py` | Performance | Parallel tool fan-out with timeout and partial-result handling |
| `4.17_context_compaction.py` | Performance | Summarize old history and keep recent turns to shrink context window |
| `4.18_token_budget_controls.py` | Performance | Input budget policy with deterministic truncation and output reserve |
| `4.19_prompt_structure_and_params.py` | Performance | System/user prompt structuring and LLM parameter tuning for performance |
| `4.20_request_dedup_coalescing.py` | Performance | Coalesce identical in-flight requests to avoid duplicate model work |
| `4.21_timeout_fallback_ladder.py` | Performance | Timeout + fallback + degraded response strategy |
| `4.22_attack_prompt_injection.py` | Attack Labs | Focused lab: direct and indirect prompt injection attack demos |
| `4.23_attack_data_exfiltration.py` | Attack Labs | Focused lab: sensitive data exfiltration attack demo |
| `4.24_attack_sql_and_tool_abuse.py` | Attack Labs | Focused lab: SQL abuse and privileged tool abuse attack demos |
| `4.25_multi_llm_performance_routing.py` | Performance | Multi-LLM routing: fast vs deep model selection and latency comparison |
| `4.26_multi_llm_security_crosscheck.py` | Security Controls | Two-model safety pattern: generator model + guard/reviewer model |
| `4.27_output_format_perf_impact.py` | Performance | Output formatting impact on latency, size, and parseability |

---

### Module 05 · Enterprise Integrations
*Deploy and integrate agents using enterprise protocols such as MCP and A2A.*

| File | What it teaches |
|---|---|
| `5.1_mcp_server.py` | Build an MCP server from scratch using FastAPI — understand the envelope protocol |
| `5.2_mcp_client.py` | HTTP client that calls the `5.1` server's tools and reads its resources |
| `5.3_mcp_sdk_server.py` | Same server rebuilt with the official `mcp` SDK: `@mcp.tool`, `@mcp.resource`, `@mcp.prompt`, and a real LLM call via `Context` |
| `5.4_mcp_sdk_client.py` | Async `ClientSession` that invokes tools, reads resources, and fetches prompts from `5.3` |
| `5.5_a2a_demo.py` | Agent-to-Agent in one file: two Ollama-backed agents passing messages to each other |
| `5.6_a2a_server.py` | A2A server — registers agents, routes messages, maintains inboxes |
| `5.7_a2a_client.py` | A2A client — registers, sends messages, polls inbox |

---

### Module 06 · Evaluation & Testing for LLM/Agent Systems
*Learn how to measure quality, safety, cost, and regressions in LLM and agent workflows.*

| File | What it teaches |
|---|---|
| `6.0_eval_metrics_basics.py` | Core eval metrics: exact match, groundedness proxy, latency/cost signals |
| `6.1_eval_golden_dataset.py` | Golden dataset construction and pass-rate scoring |
| `6.2_eval_prompt_regression.py` | Prompt regression checks and format drift detection |
| `6.3_eval_llm_judge_rubric.py` | Rubric-based judging pattern (relevance/correctness/clarity) |
| `6.4_eval_agent_trajectory.py` | Agent path evaluation: tool choice, step budget, success |
| `6.5_eval_safety_attacks.py` | Safety evals for attack blocking behavior |
| `6.6_eval_rag_groundedness.py` | Groundedness checks using retrieved-context overlap |
| `6.7_eval_cost_latency_tradeoff.py` | Quality/latency/cost trade-off comparison across variants |
| `6.8_eval_ci_gate.py` | Release gating with thresholds for quality/safety/latency |
| `6.9_eval_report_card.py` | Consolidated eval report and action-oriented summary |
| `6.10_eval_planning_quality.py` | Planning eval: step coverage, dependency validity, and order quality |
| `6.11_eval_replanning_recovery.py` | Replanning eval: failure recovery via retry/fallback/degraded modes |
| `6.12_eval_multi_agent_handoff.py` | Multi-agent eval: delegation correctness, loop control, and termination |
| `6.13_eval_multi_llm_jury.py` | Multi-LLM eval panel: dual-judge scoring with agreement/disagreement signal |

---

### Module 07 · Framework Integrations
*Compare framework-specific patterns across Python, Java, and JavaScript runtimes.*

| File | What it teaches |
|---|---|
| `7.1_llamaindex_rag.py` | LlamaIndex RAG with Ollama embeddings — compare with `1.10` and `3.12` |
| `7.2_dspy_optimized_agent.py` | DSPy: declare signatures and let `BootstrapFewShot` optimise prompts automatically |
| `7.3_embabel_goal_agent.java` | Embabel (Java/Spring): `@Action` + `@Goal` — declarative planning, framework picks execution order |
| `7.4_langchain_js_tool_call.mjs` | LangChain in JavaScript — same tool-call pattern as `3.1`, different runtime |



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
| Missing advanced model | Pull additional models as needed: `llama3.1:latest`, `lfm2.5-thinking:latest`, `llava` |

---

## 📝 Notes

- All code runs fully locally — no OpenAI API key or cloud account required.
