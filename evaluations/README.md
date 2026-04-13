# Evaluations (Minimal)

Run tests with:

```bash
pytest -q
```
This folder contains the project's test suites:

- `tests_unit/` — unit tests for small helpers and agents
- `tests_prompts/` — prompt regression checks
- `tests_rag/` — RAG index & retrieval checks
- `tests_agents/` — agent controller & behavior tests
- `tests_samples/` — sample-code sanity checks (compile + path consistency, optional live runs)

Run the full suite locally with:

```bash
pytest -q
```

If you only want to run a subset, run e.g. `pytest evaluations/tests_unit -q`.

To run sample sanity checks only:

```bash
pytest evaluations/tests_samples -q
```
