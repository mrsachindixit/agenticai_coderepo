"""Query a RAG index: retrieve documents and augment LLM prompt with context."""

import json
import sys
import os
import requests

import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from utils.ollama_client import embed, chat

INDEX_FILE = "index.json"

def cosine(a, b):
    """Compute cosine similarity between two vectors."""
    a = np.array(a)
    b = np.array(b)
    norm_product = np.linalg.norm(a) * np.linalg.norm(b) + 1e-9
    return float(a @ b) / norm_product

def search(query, k=3):
    """Search the index for top-k documents similar to query.
    
    Args:
        query: Query string
        k: Number of top results to return
    
    Returns:
        List of top-k matching documents with scores
    """
    index_file_path=os.path.join(os.path.dirname(__file__), "data", INDEX_FILE)
    if not os.path.exists(index_file_path):
        raise FileNotFoundError(
            f"Index not found: {index_file_path}. Run build_index.py first."
        )
    
    with open(index_file_path, "r", encoding="utf-8") as f:
        index = json.load(f)
    
    query_vec = None

    if isinstance(query, str):
        texts = [query]

    url = f"http://localhost:11434/api/embed"
    payload = {"model": "nomic-embed-text", "input": texts}
    r = requests.post(url, json=payload, timeout=300)
    r.raise_for_status()
    data = r.json()
    if "embeddings" in data:
        query_vec = data["embeddings"]
    elif "data" in data:
        query_vec = [item["embedding"] for item in data["data"]]
    else:
        raise ValueError("Unexpected embeddings response format")

    scored = sorted(index, key=lambda r: cosine(query_vec[0], r["vec"][0]), reverse=True)
    return scored[:k]

def rag_answer(query, k=3):
    """Retrieve context and ask LLM with augmented context (basic RAG).
    
    This implements Retrieval-Augmented Generation:
    1. Retrieve top-k documents by embedding similarity
    2. Augment prompt with retrieved context
    3. Ask LLM to answer using the context
    
    Args:
        query: User query
        k: Number of documents to retrieve
    
    Returns:
        LLM response grounded in retrieved context
    """
    top = search(query, k=k)
    
    # Build context string from top documents
    context = "\n---\n".join([
        f"[{r['id']}]\n{r['text'][:1200]}" for r in top
    ])
    
    # Augment prompt with context
    messages = [
        {
            "role": "system",
            "content": "Use the provided context to answer. If the context doesn't contain the answer, say 'I don't know'."
        },
        {
            "role": "system",
            "content": f"Context:\n{context}"
        },
        {
            "role": "user",
            "content": query
        }
    ]
    
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "llama3.1:latest",  # Note: or "lfm2.5-thinking:latest" for better reasoning
        "messages": messages,
        "stream": False
    }
    print(f"Query: {query} : {messages}\n")
    response = requests.post(url, json=payload)
    return response.json().get("message",{}).get("content","")

if __name__ == "__main__":
    query_text = "What is Sachin's full name?"
    print(f"Query: {query_text}")
    print("\n" + "="*60 + "\n")
    answer = rag_answer(query_text, k=3)
    print("Answer:")
    print(answer)

    query_text = "Tell me about history of Pune"
    print(f"Query: {query_text}")
    print("\n" + "="*60 + "\n")
    answer = rag_answer(query_text, k=3)
    print("Answer:")
    print(answer)

    query_text = "If I go on heritage walk in Pune with Sachin, which places he would show me?"
    print(f"Query: {query_text}")
    print("\n" + "="*60 + "\n")
    answer = rag_answer(query_text, k=3)
    print("Answer:")
    print(answer)
