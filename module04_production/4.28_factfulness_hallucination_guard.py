from dataclasses import dataclass

from utils.ollama_client import chat


@dataclass
class EvalResult:
    supported_ratio: float
    decision: str


def llm(system_prompt: str, user_prompt: str) -> str:
    try:
        return chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]).strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def extract_claims(answer: str) -> list[str]:
    raw = llm(
        "Extract claims as one-per-line. Keep short.",
        f"Answer:\n{answer}\n\nReturn claim lines only.",
    )
    claims = [line.strip("- ").strip() for line in raw.splitlines() if line.strip()]
    return claims[:6]


def support_check(claim: str, context: str) -> int:
    prompt = (
        "Return ONLY SUPPORTED or UNSUPPORTED based on context.\n"
        f"Context: {context}\nClaim: {claim}"
    )
    verdict = llm("Be strict and literal.", prompt).upper()
    return int("SUPPORTED" in verdict and "UNSUPPORTED" not in verdict)


def evaluate(answer: str, context: str) -> EvalResult:
    claims = extract_claims(answer)
    if not claims:
        return EvalResult(0.0, "abstain")
    hits = sum(support_check(c, context) for c in claims)
    ratio = hits / max(len(claims), 1)
    decision = "answer" if ratio >= 0.7 else "abstain"
    return EvalResult(ratio, decision)


if __name__ == "__main__":
    context = (
        "Asha is in Engineering. Ravi is in Engineering. "
        "Safe SQL policy allows only SELECT queries."
    )
    question = "Who is in Engineering and is DELETE allowed?"

    baseline_answer = llm("Answer confidently.", f"Context: {context}\nQuestion: {question}")
    improved_answer = llm(
        "Answer only from context. If uncertain, say unknown.",
        f"Context: {context}\nQuestion: {question}",
    )

    baseline_eval = evaluate(baseline_answer, context)
    improved_eval = evaluate(improved_answer, context)

    print({
        "baseline": {
            "score": round(baseline_eval.supported_ratio, 4),
            "details": {"decision": baseline_eval.decision, "answer": baseline_answer},
        },
        "improved": {
            "score": round(improved_eval.supported_ratio, 4),
            "details": {"decision": improved_eval.decision, "answer": improved_answer},
        },
    })
