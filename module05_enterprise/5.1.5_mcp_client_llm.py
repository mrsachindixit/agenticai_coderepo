"""MCP LLM client demo."""

from __future__ import annotations

import json
import uuid
from typing import Any, Dict

import requests

DEFAULT_URL = "http://127.0.0.1:8004/mcp/invoke"


def make_envelope(resource: str, payload: Dict[str, Any], metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return {
        "id": str(uuid.uuid4()),
        "type": "invoke",
        "resource": resource,
        "payload": payload,
        "metadata": metadata or {},
    }


def invoke(resource: str, payload: Dict[str, Any], url: str = DEFAULT_URL) -> Dict[str, Any]:
    response = requests.post(url, json=make_envelope(resource, payload), timeout=60)
    response.raise_for_status()
    return response.json()


def print_response(title: str, resp: Dict[str, Any]) -> None:
    print(f"\n{'=' * 72}")
    print(title)
    print(f"{'=' * 72}")
    print(json.dumps(resp.get("payload", resp), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    print("LLM-first MCP client demo (with heuristic fallback)\n")
    tools = invoke("agent/tools", {})
    print_response("Available tools", tools)

    q1 = "What's the weather in Tokyo in celsius?"
    resp1 = invoke("agent/invoke", {"query": q1})
    print_response(f"LLM invoke: {q1}", resp1)

    q2 = "What is the postal code for London?"
    resp2 = invoke("agent/invoke", {"query": q2})
    print_response(f"LLM invoke: {q2}", resp2)

    q3 = "Can you help me with something random and unrelated?"
    resp3 = invoke("agent/invoke", {"query": q3})
    print_response(f"LLM invoke (fallback demo): {q3}", resp3)

    q4 = "Calculate 25 + 17 * 3"
    baseline = invoke("agent/invoke-heuristic", {"query": q4})
    print_response(f"Heuristic baseline: {q4}", baseline)
