import os
import sys
from langchain_ollama import ChatOllama
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, START, END


DB_PATH = os.path.join(os.path.dirname(__file__), "_checkpoints.sqlite")


llm = ChatOllama(model="llama3.1:latest", base_url="http://localhost:11434", temperature=0)


def chat_node(state: dict) -> dict:
    history = state.get("history", [])
    convo = "\n".join(history + [f"User: {state['question']}"])
    answer = llm.invoke(f"Continue the conversation concisely:\n{convo}\nAssistant:").content
    return {
        "answer": answer,
        "history": history + [f"User: {state['question']}", f"Assistant: {answer}"],
    }


def build_graph(checkpointer):
    return (
        StateGraph(dict)
        .add_node("chat", chat_node)
        .add_edge(START, "chat")
        .add_edge("chat", END)
        .compile(checkpointer=checkpointer)
    )


def run_demo():
    with SqliteSaver.from_conn_string(DB_PATH) as saver:
        graph = build_graph(saver)
        cfg = {"configurable": {"thread_id": "demo-thread-1"}}

        print("--- session 1 (process A) ---")
        out = graph.invoke({"question": "My favourite colour is teal.", "history": []}, config=cfg)
        print(f"A: {out['answer']}")

        out = graph.invoke({"question": "What did I just tell you?", "history": out["history"]}, config=cfg)
        print(f"A: {out['answer']}")

        history_count = len(graph.get_state(cfg).values["history"])
        print(f"persisted turns: {history_count}")

    print("\n[simulated restart — reopening DB]\n")

    with SqliteSaver.from_conn_string(DB_PATH) as saver:
        graph = build_graph(saver)
        cfg = {"configurable": {"thread_id": "demo-thread-1"}}

        existing = graph.get_state(cfg).values
        out = graph.invoke({"question": "Repeat my favourite colour.", "history": existing["history"]}, config=cfg)
        print(f"--- session 2 (process B) ---")
        print(f"A: {out['answer']}")

        print("\nCheckpoint trail:")
        for cp in graph.get_state_history(cfg):
            preview = (cp.values.get("answer") or "")[:40]
            print(f"  ts={cp.created_at} step={cp.metadata.get('step')} ans={preview!r}")


if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    run_demo()
