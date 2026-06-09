# System Design: Self-Updating Docs Platform

## Concept
A system where documentation automatically stays in sync with the codebase. When code changes (merge to main), an agent detects affected doc sections, regenerates or flags stale content, proposes updates, and submits them for review — eliminating the documentation drift that makes most codebases' docs untrustworthy within weeks of a release.

## Architecture

```
[CI Trigger]  — on merge to main / release tag
        │
        ▼
[Change Analyser]
  - Parse git diff: changed functions, classes, signatures, config keys
  - Map changed symbols → doc sections using a pre-built symbol-to-doc index
        │
        ▼
[Staleness Classifier]
  - For each mapped doc section: is the diff semantically relevant to this section?
  - Output: STALE / LIKELY_STALE / OK per section
        │
        ▼
[Doc Generator Agent]  (for STALE sections)
  - Input: changed code + current doc section + adjacent context
  - Output: proposed replacement text, preserving author tone and structure
        │
        ▼
[Critic Agent]
  - Does the proposed text accurately reflect the new code behaviour?
  - Does it introduce false claims or hallucinated APIs?
        │
        ▼
[PR Opener / Notifier]
  - Open a draft PR with proposed doc changes
  - Tag original doc author if known (git blame)
  - For LIKELY_STALE: open issue with staleness flag rather than auto-edit
        │
        ▼
[Symbol Index Updater]
  - Rebuild symbol-to-doc index for next cycle
```

## Key Engineering Decisions
- **Symbol-to-doc index**: the key structural piece. Without it, the agent must re-read all docs on every change. Build once, update incrementally.
- **Conservative on ambiguous sections**: only auto-draft edits for sections where the mapping is direct (function signature changed → `Parameters` section). Prefer opening an issue for architectural/design sections.
- **Tone preservation**: few-shot the generator with existing doc style examples from the same file. Homogeneous doc voice matters for readability.
- **Human always approves**: auto-PR, never auto-merge. Docs affecting user-facing API contracts must have human sign-off.

## Failure Modes / Risks
- Generator hallucinate a parameter name or return type → incorrect docs merged → user bugs.
- Symbol-to-doc index drift (doc is restructured but index not rebuilt) → agent misses stale sections.
- High-churn codebases generate too many doc PRs → reviewer fatigue → all PRs ignored.
- Private/internal code details leaked into public docs if scope boundary not enforced.

## Code Anchors (existing repo)
- `module01_raw/1.10_rag_basic/build_index.py` — index build pattern applicable to symbol index
- `module03_langchain/3.21_rag_cross_encoder_rerank.py` — retrieval for doc-section mapping
- `module03_langchain/3.25_critic_refiner_loop.py` — critic agent for generated doc validation
- `module03_langchain/3.16_lg_pause_resume_hitl.py` — human approval before PR submission
