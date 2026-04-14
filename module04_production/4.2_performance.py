

import functools
import os
import time
import requests

OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://localhost:11434")

def stream_generate(prompt, model="llama3.2"):
    """Stream tokens from Ollama for faster perceived latency."""
    url = f"{OLLAMA_BASE}/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": True}
    with requests.post(url, json=payload, stream=True, timeout=120) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if not line:
                continue
            chunk = line.decode("utf-8")
            print(chunk, end="", flush=True)


def retry_with_backoff(fn, retries=3, base_delay=0.5):
    """Simple retry helper for transient errors."""
    last_err = None
    for i in range(retries):
        try:
            return fn()
        except Exception as e:
            last_err = e
            time.sleep(base_delay * (2 ** i))
    raise last_err


@functools.lru_cache(maxsize=256)
def cached_embedding(text):
    url = f"{OLLAMA_BASE}/api/embeddings"
    r = requests.post(
        url,
        json={"model": "nomic-embed-text", "input": [text]},
        timeout=120,
    )
    r.raise_for_status()
    data = r.json()
    if "embeddings" in data:
        return data["embeddings"][0]
    return data["data"][0]["embedding"]


def batch_embeddings(texts):
    """Batch embed multiple texts to reduce overhead."""
    url = f"{OLLAMA_BASE}/api/embeddings"
    payload = {"model": "nomic-embed-text", "input": texts}
    r = requests.post(url, json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()
    if "embeddings" in data:
        return data["embeddings"]
    return [item["embedding"] for item in data["data"]]


if __name__ == "__main__":
    start = time.time()
    stream_generate("Explain retrieval augmented generation in 5 bullet points.", model="llama3.2")
    print("\nTime:", time.time() - start)

    # Cached embeddings (repeated text will be fast)
    e1 = cached_embedding("agent memory")
    e2 = cached_embedding("agent memory")  # cache hit
    print("Got embeddings with caching.")

    # Retry with backoff for flaky calls
    def call_with_retry():
        return batch_embeddings(["agent memory", "tool calling", "rag"])  # batch request

    vecs = retry_with_backoff(call_with_retry)
    print("Batch embeddings returned:", len(vecs))


