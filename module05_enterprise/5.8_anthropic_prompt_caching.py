import os
import time

from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic
from langchain_anthropic.middleware import AnthropicPromptCachingMiddleware
from langgraph.checkpoint.memory import InMemorySaver


def get_refund_policy(plan_name: str) -> str:
    return f"{plan_name} plan refund policy: full refund within 7 days, prorated refund within 30 days."


def get_invoice_status(invoice_id: str) -> str:
    return f"Invoice {invoice_id}: paid on 2026-05-12."


def build_agent():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("Set ANTHROPIC_API_KEY before running this example.")

    model = ChatAnthropic(
        model="claude-sonnet-4-5",
        api_key=api_key,
        temperature=0,
        max_tokens=700,
    )

    middleware = [
        AnthropicPromptCachingMiddleware(
            ttl="1h",
            min_messages_to_cache=2,
            unsupported_model_behavior="raise",
        )
    ]

    system_prompt = (
        "You are an enterprise support assistant for a subscription SaaS company. "
        "Always answer in three parts: summary, evidence used, next action. "
        "Use tools when refund policy or invoice status is requested. "
        "If the user asks a follow-up, preserve prior context and avoid repeating unchanged policy text unless needed. "
        "Be concise and accurate."
    )

    return create_agent(
        model=model,
        tools=[get_refund_policy, get_invoice_status],
        system_prompt=system_prompt,
        middleware=middleware,
        checkpointer=InMemorySaver(),
    )


def run_turn(agent, user_message: str, thread_id: str) -> str:
    started = time.perf_counter()
    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_message}]},
        {"configurable": {"thread_id": thread_id}},
    )
    elapsed = time.perf_counter() - started
    final_message = result["messages"][-1].content
    if isinstance(final_message, list):
        final_text = "\n".join(
            block.get("text", str(block)) if isinstance(block, dict) else str(block)
            for block in final_message
        )
    else:
        final_text = str(final_message)
    print(f"Elapsed: {elapsed:.2f}s")
    return final_text


if __name__ == "__main__":
    agent = build_agent()
    thread_id = "anthropic-cache-demo-1"

    q1 = "I am on the Pro plan. Tell me the refund policy and also check invoice INV-2048."
    print(f"User: {q1}\n")
    print(run_turn(agent, q1, thread_id))

    print("\n" + "=" * 60 + "\n")

    q2 = "Based on that, what should I do next if I still want a refund today?"
    print(f"User: {q2}\n")
    print(run_turn(agent, q2, thread_id))
