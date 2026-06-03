import json
from dataclasses import dataclass

from utils.ollama_client import chat


@dataclass
class RegressionCase:
    name: str
    query: str


def llm_answer(system_prompt: str, user_prompt: str) -> str:
    try:
        return chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]).strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def is_json_with_keys(text: str, keys: list[str]) -> int:
    try:
        parsed = json.loads(text)
        return int(all(k in parsed for k in keys))
    except Exception:
        return 0


if __name__ == "__main__":
    cases = [
        RegressionCase("tool-single", "User asks weather in Berlin. Return tool call intent."),
        RegressionCase("sql-agent", "User asks: List Engineering employees with salaries from SQLite sample."),
    ]

    baseline_system = "Answer naturally."
    improved_system = (
        "Return strict JSON only with keys task_type and payload. "
        "task_type must be one of tool_call or sql_plan."
    )

    baseline_scores = []
    improved_scores = []

    for c in cases:
        baseline = llm_answer(baseline_system, c.query)
        improved = llm_answer(improved_system, c.query)
        b_score = is_json_with_keys(baseline, ["task_type", "payload"])
        i_score = is_json_with_keys(improved, ["task_type", "payload"])
        baseline_scores.append(b_score)
        improved_scores.append(i_score)
        print({"case": c.name, "baseline_json_ok": b_score, "improved_json_ok": i_score})

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
