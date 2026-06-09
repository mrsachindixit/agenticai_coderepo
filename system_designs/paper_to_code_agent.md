# System Design: Paper-to-Code Agent

## Concept
An agent that reads a research paper (PDF or arXiv URL) and produces a runnable implementation of the core algorithm or experiment described. The challenge is that papers describe *intent* and *math*, not code — the agent must bridge that gap through structured extraction, clarification, and iterative code generation.

## Architecture

```
[PDF / arXiv URL]
        │
        ▼
[Ingestion Tool]  — extract text, figures, pseudocode sections
        │
        ▼
[Extraction Agent]  — identify: algorithm, inputs/outputs, assumptions, constraints
        │
        ▼
[Clarification Loop]  — for any ambiguous step: generate a clarifying question,
                        answer it from paper context or via human-in-the-loop
        │
        ▼
[Code Generator]  — produce implementation stub from structured algorithm spec
        │
        ▼
[Test Generator]  — produce minimal unit tests from paper's own examples/tables
        │
        ▼
[Ralph Loop]  — run tests → on failure, feed error back → iterate (max N rounds)
        │
        ▼
[Explainer Agent]  — generate inline comments mapping each block to paper section
        │
        ▼
[Output: .py + test file + section-reference comments]
```

## Key Engineering Decisions
- **Extraction vs generation order**: extract algorithm structure first as structured JSON, then generate code from the JSON — not paper text directly. Reduces hallucination.
- **Ambiguity handling**: pause on unresolvable ambiguities rather than silently assuming. A human-in-the-loop checkpoint here saves re-runs.
- **Test source**: use the paper's own numerical examples as test inputs/outputs. If none exist, generate plausibility checks only (not correctness checks).
- **Scope guard**: limit to algorithms under ~50 lines of core logic. Full system reimplementations are out of scope.

## Failure Modes / Risks
- Paper uses notation inconsistently → extraction agent produces wrong spec → code silently wrong.
- Complex math (matrix ops, custom loss functions) generated incorrectly with no failing test to catch it.
- Long PDFs exceed context window before algorithm section is reached — use section-targeted chunking.

## Code Anchors (existing repo)
- `module01_raw/1.12_ralph_loop.py` — test-driven iteration loop used in final refinement stage
- `module03_langchain/3.19_agentic_rag.py` — agentic RAG for paper-section retrieval
- `module03_langchain/3.16_lg_pause_resume_hitl.py` — human-in-the-loop checkpoint for ambiguity resolution
- `module03_langchain/3.25_critic_refiner_loop.py` — rubric-based refinement applicable to code quality gate
