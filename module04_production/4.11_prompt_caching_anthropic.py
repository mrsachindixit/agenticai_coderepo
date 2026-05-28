import os
import time
from typing import Any

from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic
from langchain_anthropic.middleware import AnthropicPromptCachingMiddleware
from langgraph.checkpoint.memory import InMemorySaver


def get_refund_policy(plan_name: str) -> str:
    return f"{plan_name} plan refund policy: full refund within 7 days, prorated refund within 30 days."


def get_invoice_status(invoice_id: str) -> str:
    return f"Invoice {invoice_id}: paid on 2026-05-12."


def build_agent(use_cache: bool):
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("Set ANTHROPIC_API_KEY before running this example.")

    model = ChatAnthropic(
        model="claude-sonnet-4-5",
        api_key=api_key,
        temperature=0,
        max_tokens=700,
    )

    middleware = []
    if use_cache:
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


def _usage_from_message(msg: Any) -> dict[str, int]:
    usage = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read_input_tokens": 0,
        "cache_creation_input_tokens": 0,
    }

    usage_meta = getattr(msg, "usage_metadata", None)
    if isinstance(usage_meta, dict):
        usage["input_tokens"] = int(usage_meta.get("input_tokens", usage["input_tokens"]))
        usage["output_tokens"] = int(usage_meta.get("output_tokens", usage["output_tokens"]))
        usage["cache_read_input_tokens"] = int(
            usage_meta.get("cache_read_input_tokens", usage["cache_read_input_tokens"])
        )
        usage["cache_creation_input_tokens"] = int(
            usage_meta.get("cache_creation_input_tokens", usage["cache_creation_input_tokens"])
        )

    response_metadata = getattr(msg, "response_metadata", None)
    if isinstance(response_metadata, dict):
        token_usage = response_metadata.get("usage") or response_metadata.get("token_usage") or {}
        if isinstance(token_usage, dict):
            usage["input_tokens"] = int(token_usage.get("input_tokens", usage["input_tokens"]))
            usage["output_tokens"] = int(token_usage.get("output_tokens", usage["output_tokens"]))
            usage["cache_read_input_tokens"] = int(
                token_usage.get("cache_read_input_tokens", usage["cache_read_input_tokens"])
            )
            usage["cache_creation_input_tokens"] = int(
                token_usage.get("cache_creation_input_tokens", usage["cache_creation_input_tokens"])
            )

    return usage


def run_turn(agent, user_message: str, thread_id: str) -> dict[str, Any]:
    started = time.perf_counter()
    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_message}]},
        {"configurable": {"thread_id": thread_id}},
    )
    elapsed = time.perf_counter() - started

    final_msg = result["messages"][-1]
    content = final_msg.content
    if isinstance(content, list):
        text = "\n".join(
            block.get("text", str(block)) if isinstance(block, dict) else str(block)
            for block in content
        )
    else:
        text = str(content)

    return {
        "elapsed": elapsed,
        "text": text,
        "usage": _usage_from_message(final_msg),
    }


def run_scenario(name: str, use_cache: bool):
    agent = build_agent(use_cache=use_cache)
    thread_id = f"prompt-caching-{name.lower().replace(' ', '-') }"

    q1 = "I am on the Pro plan. Tell me the refund policy and also check invoice INV-2048."
    q2 = "Based on that, what should I do next if I still want a refund today?"

    print(f"\n{name}\n" + "=" * 60)
    print(f"User: {q1}\n")
    turn1 = run_turn(agent, q1, thread_id)
    print(turn1["text"])
    print(f"\nElapsed: {turn1['elapsed']:.2f}s")

    print("\n" + "-" * 60)
    print(f"User: {q2}\n")
    turn2 = run_turn(agent, q2, thread_id)
    print(turn2["text"])
    print(f"\nElapsed: {turn2['elapsed']:.2f}s")

    return [
        {"scenario": name, "turn": 1, **turn1["usage"], "elapsed": turn1["elapsed"]},
        {"scenario": name, "turn": 2, **turn2["usage"], "elapsed": turn2["elapsed"]},
    ]


def print_summary(rows: list[dict[str, Any]]) -> None:
    print("\n" + "=" * 90)
    print("Summary")
    print("=" * 90)
    header = (
        f"{'Scenario':<18} {'Turn':<5} {'Elapsed(s)':<11} "
        f"{'Input':<8} {'Output':<8} {'CacheRead':<10} {'CacheWrite':<11}"
    )
    print(header)
    print("-" * len(header))
    for row in rows:
        print(
            f"{row['scenario']:<18} {row['turn']:<5} {row['elapsed']:<11.2f} "
            f"{row['input_tokens']:<8} {row['output_tokens']:<8} "
            f"{row['cache_read_input_tokens']:<10} {row['cache_creation_input_tokens']:<11}"
        )


if __name__ == "__main__":
    results = []
    results.extend(run_scenario("Cache OFF", use_cache=False))
    results.extend(run_scenario("Cache ON", use_cache=True))
    print_summary(results)
