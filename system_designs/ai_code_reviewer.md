# System Design: AI Code Reviewer Agent

## Concept
An agent that reviews a pull request diff, applies team-specific standards and security rules, and produces structured, actionable comments — distinguishing between blocking issues, suggestions, and style notes. Unlike linters, it reasons about intent, context, and business logic.

## Architecture

```
[PR Diff + File Context]
        │
        ▼
[Context Fetcher]
  - Fetch: changed files, related test files, PR description, linked ticket
  - Fetch: past review comments on same codebase (memory / RAG)
        │
        ▼
[Specialist Reviewers] (parallel)
  ├── [Security Agent]    — injection, auth bypass, secrets in code, OWASP top-10
  ├── [Logic Agent]       — correctness, edge cases, algorithmic issues
  ├── [Style Agent]       — team conventions, naming, dead code
  └── [Test Coverage Agent] — missing test paths, untested branches
        │
        ▼
[Critic-Refiner Loop]  — each reviewer self-checks: "Is this comment actionable? Is it false positive?"
        │
        ▼
[Aggregator Agent]
  - Deduplicate overlapping findings
  - Classify: BLOCK / SUGGEST / STYLE
  - Rank by severity and file location
        │
        ▼
[Output Formatter]
  - GitHub PR Review API format (inline comments per line)
  - Summary comment: overall verdict, blocker count, key risks
```

## Key Engineering Decisions
- **Specialist decomposition**: one agent per concern reduces context pollution — security agent doesn't need to care about naming style.
- **Critic-refiner on each specialist**: each reviewer challenges its own output before aggregation. Cuts false-positive comment rate significantly.
- **Context budget**: load only the diff + immediate function context, not whole files. Full file context leads to off-topic comments and token waste.
- **Severity-tiered output**: separate BLOCK from SUGGEST from STYLE. Reviewers lose trust in AI comments when style nitpicks drown out real bugs.

## Failure Modes / Risks
- Logic agent misreads intent → leaves blocking comment on correct code → reviewer fatigue.
- Security agent over-triggers on benign patterns (e.g., flags every `eval` regardless of context).
- No memory of prior review decisions → same comment repeated across PRs → noise.
- Large diffs (1000+ lines) exceed context limits — needs diff chunking with per-chunk reviews then merging.

## Code Anchors (existing repo)
- `module03_langchain/3.25_critic_refiner_loop.py` — per-agent self-review pattern
- `module03_langchain/3.23_mixture_of_agents.py` — parallel specialist + aggregator pattern
- `module03_langchain/3.24_multi_agent_deadlock_safety.py` — breaker for parallel agent coordination
- `module06_evaluation/6.3_eval_llm_judge_rubric.py` — rubric-based scoring applicable to review quality
