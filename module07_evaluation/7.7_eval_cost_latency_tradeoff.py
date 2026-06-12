"""Two trade-offs every agent owner has to reason about, side by side.

Picking a model/prompt variant is never just "which is most accurate?". You are
always trading accuracy against something:

  1. ACCURACY vs LATENCY - a bigger prompt / stronger model is more accurate but
     slower. Metric: accuracy_per_second (accuracy you buy per second of wait).

  2. ACCURACY vs COST - more tokens / a pricier model cost more. Metric:
     accuracy_per_cost (accuracy you buy per unit of cost).

The "best" variant depends on which axis you care about. A chatbot on a landing
page cares about latency; a nightly batch job cares about cost. This eval prints
both frontiers so you choose deliberately instead of defaulting to "biggest model".
"""

import time
from dataclasses import dataclass
from typing import Optional

from utils.ollama_client import chat


@dataclass
class VariantRun:
    name: str
    accuracy: float       # quality proxy in 0..1
    latency_ms: float
    cost_proxy: float     # stand-in for $ (token-ish)


def llm_answer(system_prompt: str, user_prompt: str, options: Optional[dict] = None) -> tuple[str, float]:
    started = time.perf_counter()
    try:
        text = chat(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            **(options or {}),
        ).strip()
    except Exception as exc:
        text = f"ERROR: {exc}"
    return text, (time.perf_counter() - started) * 1000


def score_accuracy(answer: str, required_terms: list[str]) -> float:
    text = answer.lower()
    hits = sum(1 for term in required_terms if term.lower() in text)
    return hits / max(len(required_terms), 1)


def accuracy_per_second(v: VariantRun) -> float:
    return v.accuracy / max(v.latency_ms / 1000.0, 1e-6)   # accuracy vs latency


def accuracy_per_cost(v: VariantRun) -> float:
    return v.accuracy / max(v.cost_proxy, 1e-6)            # accuracy vs cost


def best(runs: list[VariantRun], key) -> VariantRun:
    return max(runs, key=key)


if __name__ == "__main__":
    query = "In the multi-agent flow, explain when to call horoscope_tool vs weather_tool for a premium user."
    required = ["premium", "horoscope_tool", "weather_tool"]

    variant_specs = [
        ("fast",     "Answer in one short sentence.",        {"num_predict": 40,  "temperature": 0.1}),
        ("balanced", "Answer in two concise bullet points.", {"num_predict": 90,  "temperature": 0.2}),
        ("detailed", "Answer in four detailed bullet points.", {"num_predict": 180, "temperature": 0.3}),
    ]

    runs: list[VariantRun] = []
    for name, system_prompt, options in variant_specs:
        answer, latency_ms = llm_answer(system_prompt, query, options)
        runs.append(VariantRun(
            name=name,
            accuracy=score_accuracy(answer, required),
            latency_ms=latency_ms,
            cost_proxy=max(len(answer) / 1000, 1e-3),  # cheap token proxy
        ))

    print("Per-variant metrics:")
    for v in runs:
        print({
            "variant": v.name,
            "accuracy": round(v.accuracy, 2),
            "latency_ms": round(v.latency_ms, 1),
            "cost": round(v.cost_proxy, 3),
            "acc_per_sec": round(accuracy_per_second(v), 3),   # latency trade-off
            "acc_per_cost": round(accuracy_per_cost(v), 3),    # cost trade-off
        })

    best_latency = best(runs, accuracy_per_second)
    best_cost = best(runs, accuracy_per_cost)
    best_raw = best(runs, lambda v: v.accuracy)

    print("\nWho wins on each axis:")
    print(f"  most accurate (ignore budget): {best_raw.name}")
    print(f"  best accuracy per second      : {best_latency.name}  <- pick for latency-sensitive apps")
    print(f"  best accuracy per cost        : {best_cost.name}  <- pick for cost-sensitive batch jobs")

    if best_latency.name != best_cost.name:
        print("\nNote: the latency winner and the cost winner differ - there is no free lunch.")
    else:
        print("\nNote: same winner on both axes here, but that is not guaranteed in general.")
