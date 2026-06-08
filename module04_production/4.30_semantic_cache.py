import time
import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.ollama_client import chat, embed


CACHE: list[tuple[list[float], str, str, float]] = []
THRESHOLD = 0.92
TTL_SECONDS = 600.0


def cosine(a, b) -> float:
    a, b = np.array(a), np.array(b)
    return float(a @ b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9)


def lookup(prompt: str) -> tuple[str | None, float, str | None]:
    now = time.time()
    qv = embed(prompt)[0]
    best = (None, 0.0, None)
    for vec, p, ans, exp in list(CACHE):
        if exp < now:
            continue
        sim = cosine(qv, vec)
        if sim > best[1]:
            best = (ans, sim, p)
    if best[1] >= THRESHOLD:
        return best
    return (None, best[1], best[2])


def ask(prompt: str) -> tuple[str, float, bool]:
    cached, sim, matched = lookup(prompt)
    t0 = time.perf_counter()
    if cached is not None:
        return cached, time.perf_counter() - t0, True

    answer = chat([
        {"role": "system", "content": "Be concise — under 30 words."},
        {"role": "user", "content": prompt},
    ])
    latency = time.perf_counter() - t0

    qv = embed(prompt)[0]
    CACHE.append((qv, prompt, answer, time.time() + TTL_SECONDS))
    return answer, latency, False


if __name__ == "__main__":
    queries = [
        "What is retrieval-augmented generation?",
        "What is RAG in simple terms?",
        "Explain RAG please",
        "How does prompt caching work?",
        "Tell me about prompt caching",
        "What is the capital of France?",
    ]

    saved = 0.0
    for q in queries:
        ans, lat, hit = ask(q)
        tag = "HIT " if hit else "MISS"
        print(f"[{tag}] {lat*1000:6.1f}ms  q={q!r}")
        if hit:
            saved += 1

    print(f"\nCache size: {len(CACHE)}  |  LLM calls saved: {int(saved)} of {len(queries)}")
    print(f"Threshold: {THRESHOLD}  TTL: {TTL_SECONDS}s")
    print("Production note: lower threshold -> more hits but risk of wrong answer.")
    print("Always log similarity per hit so you can tune from real traffic.")
