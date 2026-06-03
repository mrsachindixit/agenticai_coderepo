import os
import time

from utils.ollama_client import chat

FAST_MODEL = os.getenv("FAST_MODEL", "llama3.1:latest")
DEEP_MODEL = os.getenv("DEEP_MODEL", "lfm2.5-thinking:latest")


def ask(model: str, prompt: str) -> tuple[str, float]:
    started = time.perf_counter()
    try:
        text = chat(
            [
                {"role": "system", "content": "Be concise and accurate."},
                {"role": "user", "content": prompt},
            ],
            model=model,
        ).strip()
    except Exception as exc:
        text = f"ERROR: {exc}"
    return text, (time.perf_counter() - started) * 1000


def route(prompt: str) -> str:
    hard_signals = ["sql", "membership", "tool", "sequence", "plan", "compare"]
    return DEEP_MODEL if any(s in prompt.lower() for s in hard_signals) else FAST_MODEL


if __name__ == "__main__":
    prompts = [
        "From tool stubs, what are weather and pincode of Berlin?",
        "For user456 in multi-agent flow, explain tool sequence for membership-based routing.",
        "For SQLite sample, describe a safe SELECT-only plan for Engineering salaries.",
    ]

    single_latency = []
    routed_latency = []

    print(f"FAST_MODEL={FAST_MODEL}")
    print(f"DEEP_MODEL={DEEP_MODEL}\n")

    for p in prompts:
        _, ms_single = ask(DEEP_MODEL, p)
        chosen = route(p)
        _, ms_routed = ask(chosen, p)
        single_latency.append(ms_single)
        routed_latency.append(ms_routed)
        print({"prompt": p, "single_model_ms": round(ms_single, 1), "routed_model": chosen, "routed_ms": round(ms_routed, 1)})

    avg_single = sum(single_latency) / max(len(single_latency), 1)
    avg_routed = sum(routed_latency) / max(len(routed_latency), 1)
    print(f"\nAvg single-model latency: {avg_single:.1f} ms")
    print(f"Avg routed latency      : {avg_routed:.1f} ms")
