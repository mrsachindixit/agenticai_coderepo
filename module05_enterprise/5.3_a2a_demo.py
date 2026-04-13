from utils.ollama_client import chat

def agent(role_desc: str, message: str) -> str:
    messages = [
        {"role":"system","content": role_desc},
        {"role":"user","content": message}
    ]
    return chat(messages, temperature=0.2)

if __name__ == "__main__":
    a1_role = "You are Agent A: a planner that decomposes tasks."
    a2_role = "You are Agent B: an executor that writes concrete instructions."

    task = "Build a safe SQL query agent and an explanation of results."
    plan = agent(a1_role, f"Decompose this task: {task}")
    exec_plan = agent(a2_role, f"Turn this plan into exact steps and checks:{plan}")
    final = agent(a1_role, f"Review the executor plan and finalize:{exec_plan}")
    print("== Finalized Plan ==", final)
