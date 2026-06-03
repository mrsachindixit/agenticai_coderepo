import time
from dataclasses import dataclass
from typing import Optional

from utils.ollama_client import chat


@dataclass
class VariantRun:
    name: str
    quality: float
    latency_ms: float
    cost_proxy: float


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
    latency_ms = (time.perf_counter() - started) * 1000
    return text, latency_ms


def score_quality(answer: str, required_terms: list[str]) -> float:
    text = answer.lower()
    hits = sum(1 for term in required_terms if term.lower() in text)
    return hits / max(len(required_terms), 1)


def utility(v: VariantRun) -> float:
    return (0.7 * v.quality) - (0.2 * (v.latency_ms / 1000.0)) - (0.1 * v.cost_proxy)


def normalize_0_1(value: float, low: float, high: float) -> float:
    if high <= low:
        return 1.0
    return (value - low) / (high - low)


if __name__ == "__main__":
    query = "In the multi-agent flow, explain when to call horoscope_tool vs weather_tool for user membership."
    required = ["premium", "horoscope_tool", "weather_tool"]

    variant_specs = [
        ("fast", "Answer in one short sentence.", {"num_predict": 40, "temperature": 0.1}),
        ("balanced", "Answer in two concise bullet points.", {"num_predict": 90, "temperature": 0.2}),
        ("detailed", "Answer in four detailed bullet points.", {"num_predict": 180, "temperature": 0.3}),
    ]

    runs = []
    for name, system_prompt, options in variant_specs:
        answer, latency_ms = llm_answer(system_prompt, query, options)
        quality = score_quality(answer, required)
        cost_proxy = len(answer) / 1000
        runs.append(VariantRun(name=name, quality=quality, latency_ms=latency_ms, cost_proxy=cost_proxy))

    ranked = sorted(runs, key=utility, reverse=True)
    utility_values = [utility(v) for v in runs]
    min_utility = min(utility_values)
    max_utility = max(utility_values)
    for v in ranked:
        print({"variant": v.name, "quality": round(v.quality, 2), "latency_ms": round(v.latency_ms, 1), "cost_proxy": round(v.cost_proxy, 3), "utility": round(utility(v), 4)})

    baseline = next((v for v in runs if v.name == "detailed"), runs[0])
    improved = ranked[0]
    print({
        "baseline": {
            "score": round(normalize_0_1(utility(baseline), min_utility, max_utility), 4),
            "details": {
                "variant": baseline.name,
                "quality": round(baseline.quality, 3),
                "latency_ms": round(baseline.latency_ms, 1),
                "cost_proxy": round(baseline.cost_proxy, 3),
                "utility": round(utility(baseline), 4),
            },
        },
        "improved": {
            "score": round(normalize_0_1(utility(improved), min_utility, max_utility), 4),
            "details": {
                "variant": improved.name,
                "quality": round(improved.quality, 3),
                "latency_ms": round(improved.latency_ms, 1),
                "cost_proxy": round(improved.cost_proxy, 3),
                "utility": round(utility(improved), 4),
            },
        },
    })
