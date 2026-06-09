# System Design: Natural Language Workflow Engine

## Concept
A platform where business users define multi-step workflows in plain English and the system translates them into executable agentic graphs — with schema validation, step dependency resolution, and runtime monitoring. The goal is to give non-engineers the ability to compose and modify workflows without writing code, while still giving engineers full visibility and control over the underlying execution.

## Architecture

```
[Natural Language Workflow Description]
  e.g. "Every morning fetch sales data, summarise it, email the top 3 anomalies 
        to the ops team, and if any anomaly is > 20% log a ticket in Jira."
        │
        ▼
[Intent Parser Agent]
  - Extract: steps, triggers, conditions, data sources, outputs, actors
  - Output: structured workflow spec (JSON)
        │
        ▼
[Schema Validator]
  - Check: all referenced tools exist and have matching signatures
  - Check: no circular step dependencies
  - Output: validated spec or clarification request back to user
        │
        ▼
[Graph Compiler]
  - Map spec → LangGraph StateGraph (nodes = steps, edges = conditions)
  - Inject: error handling nodes, retry policies, monitoring hooks
        │
        ▼
[Preview Generator]
  - Render: human-readable flowchart of compiled graph
  - Show: estimated token cost, step count, data flow
  - User: approve / edit / regenerate
        │
        ▼
[Workflow Runtime]  (LangGraph execution engine)
  - Execute graph with configured triggers
  - Stream step events to dashboard
  - Pause on human-approval nodes
  - Checkpoint state after each node
        │
        ▼
[Observability Layer]
  - Per-step: latency, token count, success/failure
  - Per-run: total cost, critical-path bottleneck, SLO compliance
```

## Key Engineering Decisions
- **Structured spec as intermediate representation**: never go from NL directly to code. NL → spec → graph. The spec can be stored, versioned, and audited independently of the compiled graph.
- **Tool registry as ground truth**: the parser can only emit steps that reference real registered tools. Hallucinated tool names must fail at validation, not at runtime.
- **Preview before execute**: a compiled graph visual shown to the user before first run catches intent-vs-implementation mismatches without a production incident.
- **Stateless reducer nodes**: each LangGraph node is a pure `(state, event) → new_state` function. Makes replay, debugging, and partial re-runs safe.

## Failure Modes / Risks
- Ambiguous NL produces plausible-but-wrong spec → silent logic error in production runs.
- Tool registry grows stale → parser references outdated tool signatures → runtime type errors.
- Complex conditional logic in NL ("if A and (B or not C)") parsed incorrectly → missing branches.
- Unbounded loops in NL description ("keep retrying until success") compile to infinite graphs without a hard exit guard.

## Code Anchors (existing repo)
- `module03_langchain/3.5_lg_basic.py` — LangGraph StateGraph baseline
- `module03_langchain/3.15_langgraph_coordinator.py` — coordinator dispatching to subgraph nodes
- `module03_langchain/3.16_lg_pause_resume_hitl.py` — pause/resume with human approval mid-graph
- `module04_production/4.32_persistent_checkpoint_sqlite.py` — state checkpoint for long-running workflow runs
- `module04_production/4.31_streaming_events_langgraph.py` — step-level event streaming for dashboard
- `module02_basics/2.8_structured_output_response.py` — structured spec extraction from NL input
