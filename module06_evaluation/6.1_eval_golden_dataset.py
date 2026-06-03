from dataclasses import dataclass

from utils.ollama_client import chat


@dataclass
class Example:
    question: str
    context: str
    expected_substrings: list[str]


def llm_answer(system_prompt: str, user_prompt: str) -> str:
    try:
        return chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]).strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def score_example(answer: str, expected_substrings: list[str]) -> int:
    text = answer.lower()
    return int(all(term.lower() in text for term in expected_substrings))


if __name__ == "__main__":
    golden = [
        Example(
            "What is weather and pincode of Berlin?",
            "Use tool stub outputs: get_weather('Berlin')->'Berlin: +12°C', get_pincode('Berlin')->'Berlin: 123456'.",
            ["berlin", "+12", "123456"],
        ),
        Example(
            "Which department is Asha in from the SQLite tutorial sample?",
            "SQLite sample rows include: (Asha, Engineering, 2200000), (Ravi, Engineering, 1800000).",
            ["asha", "engineering"],
        ),
        Example(
            "How do tools and memory interplay in agents?",
            "RAG note: tools fetch fresh data; memory keeps conversation continuity across turns.",
            ["tools", "memory"],
        ),
    ]

    baseline_system = "Answer briefly."
    improved_system = "Answer in one short sentence and include all required keywords exactly."

    baseline_scores = []
    improved_scores = []

    for ex in golden:
        user = (
            f"Context: {ex.context}\n"
            f"Question: {ex.question}\n"
            f"Required keywords: {', '.join(ex.expected_substrings)}"
        )
        baseline = llm_answer(baseline_system, user)
        improved = llm_answer(improved_system, user)
        b_score = score_example(baseline, ex.expected_substrings)
        i_score = score_example(improved, ex.expected_substrings)
        baseline_scores.append(b_score)
        improved_scores.append(i_score)
        print({"question": ex.question, "baseline": b_score, "improved": i_score})

    baseline_rate = sum(baseline_scores) / max(len(baseline_scores), 1)
    improved_rate = sum(improved_scores) / max(len(improved_scores), 1)
    print({
        "baseline": {
            "score": round(baseline_rate, 4),
            "details": {"pass_rate": round(baseline_rate, 4), "cases": len(baseline_scores)},
        },
        "improved": {
            "score": round(improved_rate, 4),
            "details": {"pass_rate": round(improved_rate, 4), "cases": len(improved_scores)},
        },
    })
