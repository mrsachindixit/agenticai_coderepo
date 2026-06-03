import json

from utils.ollama_client import chat


def llm_answer(system_prompt: str, user_prompt: str) -> str:
    try:
        return chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]).strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def parse_plan(text: str) -> list[dict]:
    try:
        data = json.loads(text)
        steps = data.get("steps", [])
        return steps if isinstance(steps, list) else []
    except Exception:
        return []


def score_plan(steps: list[dict], required: list[str]) -> dict:
    names = [str(s.get("name", "")).lower() for s in steps]
    deps_ok = all(isinstance(s.get("depends_on", []), list) for s in steps)
    coverage = sum(1 for term in required if any(term in n for n in names))
    order_terms = ["load", "split", "embed", "retrieve", "answer"]
    found_positions = []
    for term in order_terms:
        idx = next((i for i, name in enumerate(names) if term in name), -1)
        found_positions.append(idx)
    order_ok = all(pos >= 0 for pos in found_positions) and found_positions == sorted(found_positions)
    return {
        "coverage": coverage / max(len(required), 1),
        "deps_ok": int(deps_ok),
        "order_ok": int(order_ok),
        "score": round((0.5 * (coverage / max(len(required), 1))) + (0.25 * int(deps_ok)) + (0.25 * int(order_ok)), 3),
    }


if __name__ == "__main__":
    task = "Build the same local RAG flow students saw: load docs, split chunks, embed, retrieve, answer."
    required_steps = ["load docs", "split", "embed", "retrieve", "answer"]
    user_prompt = (
        f"Task: {task}\n"
        "Return plan as strict JSON: {\"steps\": [{\"name\": str, \"depends_on\": [str]}]}"
    )

    baseline = llm_answer("Create a plan.", user_prompt)
    improved = llm_answer(
        "Create a 5-step plan with explicit dependencies that follows load->split->embed->retrieve->answer.",
        user_prompt,
    )

    baseline_score = score_plan(parse_plan(baseline), required_steps)
    improved_score = score_plan(parse_plan(improved), required_steps)

    print({
        "baseline": {"score": baseline_score.get("score", 0), "details": baseline_score},
        "improved": {"score": improved_score.get("score", 0), "details": improved_score},
    })
