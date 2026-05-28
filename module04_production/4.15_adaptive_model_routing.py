import time
import json
import urllib.request


OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
fast_model = "llama3.1:latest"
strong_model = "lfm2.5-thinking:latest"


def classify_query_complexity(query: str) -> str:
    q = query.lower()
    complex_signals = [
        "compare",
        "tradeoff",
        "design",
        "architecture",
        "step-by-step",
        "multi",
        "optimize",
    ]
    score = sum(1 for s in complex_signals if s in q) + (len(query) > 140)
    return "complex" if score >= 2 else "simple"


def route_model(query: str) -> str:
    return strong_model if classify_query_complexity(query) == "complex" else fast_model


def answer(query: str) -> str:
    model = route_model(query)
    started = time.perf_counter()
    payload = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": query}],
            "stream": False,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_CHAT_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    elapsed = time.perf_counter() - started
    print(f"Model: {model} | Latency: {elapsed:.2f}s")
    return str(data["message"]["content"])


if __name__ == "__main__":
    q1 = "What is RAG in one paragraph?"
    q2 = "Compare RAG vs fine-tuning for enterprise search and propose architecture tradeoffs."

    print("\nQuery 1:", q1)
    print(answer(q1))

    print("\n" + "=" * 70)

    print("\nQuery 2:", q2)
    print(answer(q2))
