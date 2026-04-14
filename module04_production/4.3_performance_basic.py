# Performance — Hand-Rolled Basics

import functools
import os
import time
import requests

OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://localhost:11434")


# --- Streaming (perceived latency reduction) ---

def stream_generate(prompt, model="llama3.2"):
    url = f"{OLLAMA_BASE}/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": True}
    with requests.post(url, json=payload, stream=True, timeout=120) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if not line:
                continue
            print(line.decode("utf-8"), end="", flush=True)


# --- Retry with exponential backoff ---

def retry_with_backoff(fn, retries=3, base_delay=0.5):
    last_err = None
    for i in range(retries):
        try:
            return fn()
        except Exception as e:
            last_err = e
            time.sleep(base_delay * (2 ** i))
    raise last_err


# --- LRU caching for embeddings ---

@functools.lru_cache(maxsize=256)
def cached_embedding(text):
    url = f"{OLLAMA_BASE}/api/embeddings"
    r = requests.post(url, json={"model": "nomic-embed-text", "input": [text]}, timeout=120)
    r.raise_for_status()
    data = r.json()
    return data["embeddings"][0] if "embeddings" in data else data["data"][0]["embedding"]


# --- Batch embeddings (fewer HTTP round-trips) ---

def batch_embeddings(texts):
    url = f"{OLLAMA_BASE}/api/embeddings"
    r = requests.post(url, json={"model": "nomic-embed-text", "input": texts}, timeout=120)
    r.raise_for_status()
    data = r.json()
    return data["embeddings"] if "embeddings" in data else [d["embedding"] for d in data["data"]]


if __name__ == "__main__":
    start = time.time()
    stream_generate("Explain retrieval augmented generation in 5 bullet points.")
    print(f"\nTime: {time.time() - start:.1f}s")

    e1 = cached_embedding("agent memory")
    e2 = cached_embedding("agent memory")  # cache hit
    print("Cached embeddings: OK")

    vecs = retry_with_backoff(lambda: batch_embeddings(["agent memory", "tool calling", "rag"]))
    print(f"Batch embeddings: {len(vecs)} vectors")
