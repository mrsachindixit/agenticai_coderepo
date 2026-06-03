import hashlib
import json
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor


OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.1:latest"


cache: dict[str, str] = {}
inflight: dict[str, threading.Event] = {}
inflight_result: dict[str, str] = {}
lock = threading.Lock()


def call_model(prompt: str) -> str:
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
    req = urllib.request.Request(
        OLLAMA_CHAT_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return str(data["message"]["content"])


def key_for_prompt(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def ask_without_coalescing(prompt: str) -> str:
    return call_model(prompt)


def ask_with_coalescing(prompt: str) -> str:
    key = key_for_prompt(prompt)

    with lock:
        if key in cache:
            return cache[key]

        if key in inflight:
            waiter = inflight[key]
            owner = False
        else:
            waiter = threading.Event()
            inflight[key] = waiter
            owner = True

    if owner:
        try:
            result = call_model(prompt)
            with lock:
                cache[key] = result
                inflight_result[key] = result
        finally:
            with lock:
                waiter.set()
                inflight.pop(key, None)
        return result

    waiter.wait(timeout=120)
    with lock:
        if key in cache:
            return cache[key]
        return inflight_result.get(key, "fallback")


def benchmark(fn, prompt: str, parallel_requests: int = 5):
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=parallel_requests) as ex:
        futures = [ex.submit(fn, prompt) for _ in range(parallel_requests)]
        outputs = [f.result() for f in futures]
    elapsed = time.perf_counter() - started
    return elapsed, outputs


if __name__ == "__main__":
    prompt = "In exactly 5 bullets, explain SLO monitoring for AI agents."

    t1, out1 = benchmark(ask_without_coalescing, prompt, parallel_requests=5)
    print(f"Without coalescing elapsed: {t1:.2f}s")

    t2, out2 = benchmark(ask_with_coalescing, prompt, parallel_requests=5)
    print(f"With coalescing elapsed   : {t2:.2f}s")

    print("\nSample output:")
    print(out2[0][:240])
