# AgenticAI Teaching Style Instructions

Use these rules for all educational samples in this repository.

## Teaching philosophy
- Keep examples concept-first and runnable.
- Prefer inline procedural code over heavy class hierarchies.
- Keep files succinct and practical.
- Avoid over-engineering and avoid academic/geeky framing.
- Show baseline vs improved patterns when teaching optimization or evaluation.
- Use real model invocation where feasible for demonstrations.

## Code style
- Keep scripts short and readable.
- Use clear variable names.
- Minimize abstraction unless it clearly improves learning.
- Avoid unnecessary comments; code should read naturally.

## Curriculum style
- One file should teach one clear idea.
- Preserve progressive learning order across modules.
- Favor deterministic scoring snippets around LLM calls so outcomes are inspectable.

## Privacy and publication safety
- The `agenticai_book/` content is draft and must be treated as private until explicitly published.
- Do not copy manuscript prose, unpublished examples, or narrative text from `agenticai_book/` into public-facing code docs or repo files.
- When syncing book and code, prefer path/anchor alignment and concept labels only; avoid transferring draft wording.
