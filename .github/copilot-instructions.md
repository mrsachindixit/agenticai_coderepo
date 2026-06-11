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

## Code samples — MANDATORY style rules
These are non-negotiable for every `.py` file added under this repo:
1. **Inline, direct, learning-first.** Top-level functions only. Do NOT introduce classes, dataclasses, pydantic models, or utility modules unless the chapter being taught is specifically about that abstraction.
2. **No text introduction at the file header.** No multi-line module docstring, no banner comment block describing what the file is "about". The file should start with imports, then code. The book explains the concept; the code shows it.
3. **No abstraction for its own sake.** Prefer a 40-line script over a 200-line one with helpers. If you find yourself extracting a helper, ask whether the learner gains more by seeing the duplication inline.
4. **Tiny dependency surface.** Stick to `utils/ollama_client.py`, the Python standard library, and (where the chapter requires it) LangChain/LangGraph. Do not pull in pydantic, dataclasses, attrs, or similar unless the topic is schema/validation itself.
5. **Print, don't return.** Sample files run end-to-end and print observable output. Avoid building libraries.

## Curriculum style
- One file should teach one clear idea.
- Preserve progressive learning order across modules.
- Favor deterministic scoring snippets around LLM calls so outcomes are inspectable.

## Privacy and publication safety
- The `agenticai_book/` content is draft and must be treated as private until explicitly published.
- Do not copy manuscript prose, unpublished examples, or narrative text from `agenticai_book/` into public-facing code docs or repo files.
- When syncing book and code, prefer path/anchor alignment and concept labels only; avoid transferring draft wording.
