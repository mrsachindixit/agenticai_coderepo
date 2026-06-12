import time

from utils.ollama_client import chat


def exact_match(pred: str, target: str) -> int:
    return int(pred.strip().lower() == target.strip().lower())


def contains_all(pred: str, required_terms: list[str]) -> int:
    p = pred.lower()
    return int(all(t.lower() in p for t in required_terms))


def llm_answer(system_prompt: str, user_prompt: str) -> tuple[str, float]:
    started = time.perf_counter()
    try:
        text = chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]).strip()
    except Exception as exc:
        text = f"ERROR: {exc}"
    return text, (time.perf_counter() - started) * 1000


def run_case(name: str, pred: str, target: str, required_terms: list[str], latency_ms: float, cost_usd: float):
    em = exact_match(pred, target)
    grounded = contains_all(pred, required_terms)
    print("\n" + "=" * 80)
    print(name)
    print("=" * 80)
    print("Prediction:", pred)
    print("Target    :", target)
    print(f"ExactMatch={em} Grounded={grounded} LatencyMs={latency_ms:.0f} CostUSD={cost_usd:.5f}")


if __name__ == "__main__":
    started = time.perf_counter()
    question = (
        "Tutorial stub reminder: get_weather('Berlin') -> 'Berlin: +12°C' and "
        "get_pincode('Berlin') -> 'Berlin: 123456'. "
        "Answer in one sentence with both values."
    )

    baseline_pred, baseline_ms = llm_answer("Answer briefly.", question)
    improved_pred, improved_ms = llm_answer(
        "Answer in one sentence and include Berlin, +12°C, and 123456 exactly.",
        question,
    )

    run_case(
        "Baseline",
        pred=baseline_pred,
        target="Berlin weather is +12°C and pincode is 123456.",
        required_terms=["berlin", "+12", "123456"],
        latency_ms=baseline_ms,
        cost_usd=len(baseline_pred) / 1000000,
    )
    run_case(
        "Improved",
        pred=improved_pred,
        target="Berlin weather is +12°C and pincode is 123456.",
        required_terms=["berlin", "+12", "123456"],
        latency_ms=improved_ms,
        cost_usd=len(improved_pred) / 1000000,
    )
    b_em = exact_match(baseline_pred, "Berlin weather is +12°C and pincode is 123456.")
    b_grounded = contains_all(baseline_pred, ["berlin", "+12", "123456"])
    i_em = exact_match(improved_pred, "Berlin weather is +12°C and pincode is 123456.")
    i_grounded = contains_all(improved_pred, ["berlin", "+12", "123456"])
    result = {
        "baseline": {
            "score": round((b_em + b_grounded) / 2, 3),
            "details": {
                "exact_match": b_em,
                "grounded": b_grounded,
                "latency_ms": round(baseline_ms, 1),
                "cost_proxy": round(len(baseline_pred) / 1000000, 6),
            },
        },
        "improved": {
            "score": round((i_em + i_grounded) / 2, 3),
            "details": {
                "exact_match": i_em,
                "grounded": i_grounded,
                "latency_ms": round(improved_ms, 1),
                "cost_proxy": round(len(improved_pred) / 1000000, 6),
            },
        },
        "runtime_s": round(time.perf_counter() - started, 3),
    }
    print(result)
