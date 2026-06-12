import json
import time
import urllib.request


OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.1:latest"


def chat_once(system_prompt: str, user_prompt: str, options: dict) -> tuple[str, float]:
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "options": options,
    }

    started = time.perf_counter()
    req = urllib.request.Request(
        OLLAMA_CHAT_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    elapsed = time.perf_counter() - started

    text = str(data["message"]["content"]).strip()
    return text, elapsed


def run_case(title: str, system_prompt: str, user_prompt: str, options: dict):
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)
    print("System:", system_prompt)
    print("User  :", user_prompt)
    print("Options:", options)

    answer, elapsed = chat_once(system_prompt, user_prompt, options)
    print(f"Latency: {elapsed:.2f}s")
    print("Answer:")
    print(answer)


def main():
    query = "Give deployment recommendations for an AI support assistant."

    run_case(
        "Case 1: Weak structure + high randomness",
        "You are helpful.",
        query,
        {"temperature": 0.9, "top_p": 0.95, "num_predict": 300},
    )

    run_case(
        "Case 2: Strong structure + controlled output",
        "You are a production architect. Output exactly 5 bullets. Max 12 words each.",
        query,
        {"temperature": 0.2, "top_p": 0.8, "num_predict": 120, "repeat_penalty": 1.1},
    )

    run_case(
        "Case 3: Same prompt with strict brevity budget",
        "You are a production architect. Output exactly 3 bullets. Max 10 words each.",
        query,
        {"temperature": 0.1, "top_p": 0.7, "num_predict": 80, "repeat_penalty": 1.15},
    )


if __name__ == "__main__":
    main()
