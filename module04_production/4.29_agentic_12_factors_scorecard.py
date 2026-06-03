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


def score_system(checks: dict[str, bool]) -> dict:
    per_factor = {f: int(checks.get(f, False)) for f in FACTORS}
    total = sum(per_factor.values())
    score = total / len(FACTORS)
    missing = [f for f, ok in per_factor.items() if ok == 0]
    actions = [f"improve:{m}" for m in missing[:3]]
    return {
        "score": round(score, 4),
        "details": {
            "passed": total,
            "total": len(FACTORS),
            "factors": per_factor,
            "top_actions": actions,
        },
    }


if __name__ == "__main__":
    baseline_checks = {
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

    improved_checks = {
        "clear_goal": True,
        "prompt_control": True,
        "tool_contracts": True,
        "state_management": True,
        "memory_strategy": True,
        "safety_guardrails": True,
        "least_privilege": True,
        "observability": True,
        "evaluation_loop": True,
        "latency_cost_control": True,
        "protocol_interop": True,
        "versioning_governance": True,
    }

    print({
        "baseline": score_system(baseline_checks),
        "improved": score_system(improved_checks),
    })
