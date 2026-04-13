import argparse
from langchain.vectorstores import Chroma
from utils import get_env
from utils.ollama_client import chat as ollama_chat, embed as ollama_embed
import os


def _build_prompt(query: str, retrieved_texts: list, chat_history: list):
    system = (
        "You are an assistant that answers questions using the provided document context. "
        "When helpful, cite the source path. Keep answers concise and factual."
    )
    context = "\n---\n".join(retrieved_texts)
    history_block = "\n".join([f"User: {u}\nAssistant: {a}" for u, a in chat_history]) if chat_history else ""
    user = f"Context:\n{context}\n\nHistory:\n{history_block}\n\nUser question: {query}\n\nAnswer using the context above." 
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    return messages


def load_chain(persist_dir: str, model: str | None = None):
    # Chroma with Ollama embedding function
    vectordb = Chroma(persist_directory=persist_dir, embedding_function=ollama_embed)
    retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 4})

    # Simple memory as list of (user, assistant) tuples
    memory = []

    def ask(question: str):
        # Retrieve
        docs = retriever.get_relevant_documents(question)
        texts = [d.page_content if hasattr(d, 'page_content') else d for d in docs]
        messages = _build_prompt(question, texts, memory)
        resp = ollama_chat(messages, model=model) if model else ollama_chat(messages)
        # store in memory
        memory.append((question, resp))
        return resp

    return ask


def chat_loop(ask_fn):
    print("RAG conversational agent (Ollama) ready — ask questions, or type 'exit' to quit")
    while True:
        try:
            q = input("You: ")
        except EOFError:
            break
        if not q:
            continue
        if q.strip().lower() in ("exit", "quit"):
            break
        resp = ask_fn(q)
        print("Agent:\n", resp)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--persist_dir", default="chroma_db")
    parser.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "llama3"))
    args = parser.parse_args()

    chain = load_chain(args.persist_dir, args.model)
    chat_loop(chain)
