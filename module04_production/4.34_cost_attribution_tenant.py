import contextvars
from contextlib import contextmanager
import os
import sys
import time
import uuid
from collections import defaultdict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.ollama_client import chat


PRICES = {
    "ollama/llama3.1:latest":   {"in": 0.0,   "out": 0.0},   # local -> 0 cost (still log tokens!)
    "openai/gpt-4o-mini":       {"in": 0.15,  "out": 0.60},
    "openai/gpt-4o":            {"in": 2.50,  "out": 10.00},
    "anthropic/claude-sonnet-4-5": {"in": 3.00, "out": 15.00},
}


_ctx: contextvars.ContextVar[dict] = contextvars.ContextVar("llm_ctx", default={})


@contextmanager
def attribute(**tags):
    token = _ctx.set({**_ctx.get(), **tags, "request_id": str(uuid.uuid4())})
    try:
        yield
    finally:
        _ctx.reset(token)


LEDGER: list[dict] = []


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def tracked_chat(messages, model_key: str = "ollama/llama3.1:latest", **opts) -> str:
    t0 = time.perf_counter()
    answer = chat(messages, model=model_key.split("/", 1)[1], **opts)
    elapsed = time.perf_counter() - t0

    in_tokens  = sum(estimate_tokens(m["content"]) for m in messages)
    out_tokens = estimate_tokens(answer)
    p = PRICES[model_key]
    cost = (in_tokens * p["in"] + out_tokens * p["out"]) / 1_000_000

    LEDGER.append({
        **_ctx.get(),
        "model": model_key,
        "in_tok": in_tokens,
        "out_tok": out_tokens,
        "cost_usd": cost,
        "ms": round(elapsed * 1000, 1),
    })
    return answer


def chargeback(group_by: list[str]) -> list[dict]:
    buckets: dict[tuple, dict] = defaultdict(lambda: {"calls": 0, "in_tok": 0, "out_tok": 0, "cost_usd": 0.0})
    for row in LEDGER:
        key = tuple(row.get(g) for g in group_by)
        b = buckets[key]
        b["calls"]    += 1
        b["in_tok"]   += row["in_tok"]
        b["out_tok"]  += row["out_tok"]
        b["cost_usd"] += row["cost_usd"]
    return [
        {**dict(zip(group_by, k)), **{m: round(v, 4) if isinstance(v, float) else v for m, v in v.items()}}
        for k, v in sorted(buckets.items())
    ]


if __name__ == "__main__":
    for tenant, feature, n in [("acme", "chat", 2), ("acme", "summarize", 1), ("globex", "chat", 3)]:
        for i in range(n):
            with attribute(tenant=tenant, feature=feature):
                tracked_chat([
                    {"role": "system", "content": "Be concise."},
                    {"role": "user",   "content": f"{feature} request {i} for {tenant}"},
                ])

    print("=== Per-tenant chargeback ===")
    for row in chargeback(["tenant"]):
        print(row)

    print("\n=== Per-tenant per-feature ===")
    for row in chargeback(["tenant", "feature"]):
        print(row)

    print("\n=== Per-model (helps capacity planning) ===")
    for row in chargeback(["model"]):
        print(row)

