# Performance — Production Libraries (tenacity + LangChain caching)
# pip install tenacity langchain-ollama

import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from langchain_ollama import ChatOllama
from langchain_core.globals import set_llm_cache
from langchain_core.caches import InMemoryCache


# --- Tenacity: declarative retry with exponential backoff + jitter ---
# Replaces hand-rolled retry loops with battle-tested retry logic

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    reraise=True,
)
def call_llm_with_retry(llm, prompt: str) -> str:
    return llm.invoke(prompt).content


# --- LangChain LLM caching (identical prompts return cached responses) ---

def setup_llm_cache():
    # InMemoryCache for dev; use SQLiteCache or RedisCache in production
    set_llm_cache(InMemoryCache())


if __name__ == "__main__":
    setup_llm_cache()

    llm = ChatOllama(model="llama3.2:latest", base_url="http://localhost:11434")

    # First call — hits the model
    start = time.time()
    r1 = call_llm_with_retry(llm, "What is an LLM agent in one sentence?")
    t1 = time.time() - start
    print(f"First call  ({t1:.2f}s): {r1}")

    # Second identical call — cache hit, near-instant
    start = time.time()
    r2 = call_llm_with_retry(llm, "What is an LLM agent in one sentence?")
    t2 = time.time() - start
    print(f"Cache hit   ({t2:.2f}s): {r2}")

    print(f"\nSpeedup: {t1/max(t2,0.001):.0f}x")
