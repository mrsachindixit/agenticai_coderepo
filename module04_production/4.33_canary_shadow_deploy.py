import random
import statistics
import time

def baseline_answer(q: str) -> tuple[str, float, bool]:
    time.sleep(0.05)
    correct = random.random() < 0.85          # 85 % quality
    return f"baseline:{q[:8]}", 0.05, correct

def candidate_answer(q: str) -> tuple[str, float, bool]:
    time.sleep(0.07)
    correct = random.random() < 0.78          # SECRETLY worse — auto-rollback should catch this
    return f"candidate:{q[:8]}", 0.07, correct


metrics: dict[str, list[dict]] = {"baseline": [], "candidate": []}


def record(variant: str, latency: float, correct: bool) -> None:
    metrics[variant].append({"lat": latency, "ok": correct})


def summary(variant: str) -> dict:
    rows = metrics[variant]
    if not rows:
        return {"n": 0}
    return {
        "n": len(rows),
        "p50_ms": round(statistics.median(r["lat"] for r in rows) * 1000, 1),
        "quality": round(sum(r["ok"] for r in rows) / len(rows), 3),
    }


def canary_route(query: str, candidate_pct: float, min_n: int, quality_floor: float) -> tuple[str, str]:
    use_candidate = random.random() < candidate_pct
    variant = "candidate" if use_candidate else "baseline"
    answer, lat, ok = (candidate_answer(query) if use_candidate else baseline_answer(query))
    record(variant, lat, ok)
    return answer, variant


def should_rollback(min_n: int, quality_floor: float) -> bool:
    cand = summary("candidate")
    base = summary("baseline")
    if cand.get("n", 0) < min_n:
        return False
    return cand["quality"] < min(quality_floor, base["quality"] - 0.05)


def shadow_route(query: str) -> str:
    user_facing, lat_b, ok_b = baseline_answer(query)
    _shadow,    lat_c, ok_c = candidate_answer(query)
    record("baseline",  lat_b, ok_b)
    record("candidate", lat_c, ok_c)
    return user_facing


if __name__ == "__main__":
    random.seed(0)

    print("=== Stage 1: SHADOW (zero user risk) ===")
    for i in range(200):
        shadow_route(f"q{i}")
    print("baseline :", summary("baseline"))
    print("candidate:", summary("candidate"))
    decision = "PROMOTE TO CANARY" if summary("candidate")["quality"] >= summary("baseline")["quality"] - 0.03 else "REJECT"
    print(f"shadow decision -> {decision}\n")

    metrics["baseline"].clear(); metrics["candidate"].clear()

    print("=== Stage 2: CANARY @ 10 % (live traffic, monitored) ===")
    candidate_pct = 0.10
    rolled_back_at = None
    for i in range(500):
        canary_route(f"q{i}", candidate_pct=candidate_pct, min_n=20, quality_floor=0.80)
        if rolled_back_at is None and should_rollback(min_n=20, quality_floor=0.80):
            rolled_back_at = i
            candidate_pct = 0.0
            print(f"!! AUTO-ROLLBACK triggered after {i} requests")

    print("baseline :", summary("baseline"))
    print("candidate:", summary("candidate"))
    print(f"rolled_back_at_request: {rolled_back_at}")
    print("\nLesson: shadow finds the bug with zero blast radius;")
    print("canary catches it after limited blast radius and rolls back automatically.")
