FACTORS = [
    "clear_goal",
    "prompt_control",
    "tool_contracts",
    "state_management",
    "memory_strategy",
    "safety_guardrails",
    "least_privilege",
    "observability",
    "evaluation_loop",
    "latency_cost_control",
    "protocol_interop",
    "versioning_governance",
]


def evaluate(checks: dict[str, bool]) -> dict:
    vals = {f: int(checks.get(f, False)) for f in FACTORS}
    score = sum(vals.values()) / len(FACTORS)
    return {"score": round(score, 4), "details": vals}


if __name__ == "__main__":
    baseline = {
        "clear_goal": True,
        "prompt_control": True,
        "tool_contracts": True,
        "state_management": False,
        "memory_strategy": False,
        "safety_guardrails": True,
        "least_privilege": False,
        "observability": False,
        "evaluation_loop": False,
        "latency_cost_control": False,
        "protocol_interop": False,
        "versioning_governance": False,
    }
    improved = {k: True for k in FACTORS}

    print({"baseline": evaluate(baseline), "improved": evaluate(improved)})
