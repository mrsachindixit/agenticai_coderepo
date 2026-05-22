"""LLM-first agent with heuristic fallback."""

from __future__ import annotations

import ast
import json
import os
import re
from typing import Any, Dict

import requests

OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


def ollama_chat(messages: list[dict[str, str]], temperature: float = 0.2) -> str:
    url = f"{OLLAMA_BASE}/api/chat"
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature},
    }
    response = requests.post(url, json=payload, timeout=300)
    response.raise_for_status()
    data = response.json()
    return data.get("message", {}).get("content", "")

def get_weather(city: str) -> str:
    temps = {"bogotá": "12°C", "new york": "18°C", "london": "8°C", "tokyo": "22°C"}
    temp = temps.get(city.lower(), "15°C")
    return f"{city}: {temp}, Partly cloudy"


def get_pincode(city: str) -> str:
    pincodes = {"bogotá": "110111", "new york": "10001", "london": "SW1A1AA", "tokyo": "100-0001"}
    pincode = pincodes.get(city.lower(), "000000")
    return f"{city}: {pincode}"


def calculate(expression: str) -> str:
    try:
        node = ast.parse(expression, mode="eval")
        for n in ast.walk(node):
            if isinstance(n, ast.Call):
                return "Error: Function calls not allowed"
            if isinstance(n, ast.Name):
                return "Error: Variable names not allowed"
        code = compile(node, "<string>", "eval")
        return str(eval(code, {"__builtins__": {}}, {}))
    except Exception as exc:
        return f"Calculation error: {exc}"


TOOLS = {
    "get_weather": get_weather,
    "get_pincode": get_pincode,
    "calculate": calculate,
}

TOOL_SCHEMAS = {
    "get_weather": {
        "name": "get_weather",
        "description": "Get weather for a city",
        "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
    },
    "get_pincode": {
        "name": "get_pincode",
        "description": "Get postal code for a city",
        "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
    },
    "calculate": {
        "name": "calculate",
        "description": "Perform arithmetic calculation",
        "parameters": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]},
    },
}

def run_heuristic_agent(query: str) -> Dict[str, Any]:
    q = query.lower()
    planned = []

    if any(w in q for w in ["weather", "temperature", "climate", "hot", "cold"]):
        for city in ["bogotá", "new york", "london", "tokyo"]:
            if city in q:
                planned.append(("get_weather", {"city": city}))
                break

    if any(w in q for w in ["pincode", "postal", "zip", "code"]):
        for city in ["bogotá", "new york", "london", "tokyo"]:
            if city in q:
                planned.append(("get_pincode", {"city": city}))
                break

    if any(w in q for w in ["calculate", "math", "compute", "plus", "minus"]):
        m = re.search(r"(\d+\s*[\+\-\*/]\s*\d+)", q)
        if m:
            planned.append(("calculate", {"expression": m.group(1)}))

    if not planned:
        return {
            "mode": "heuristic",
            "query": query,
            "iterations": [],
            "final_answer": "I can help with weather, pincode, or calculation queries.",
            "tools_available": list(TOOL_SCHEMAS.keys()),
        }

    iterations = []
    parts = ["Based on the tools called:"]
    for idx, (name, args) in enumerate(planned, start=1):
        result = TOOLS[name](**args)
        iterations.append({"step": idx, "action": f"Called {name}", "result": result})
        parts.append(f"- {name}: {result}")

    return {"mode": "heuristic", "query": query, "iterations": iterations, "final_answer": "\n".join(parts)}


def run_llm_agent(query: str) -> Dict[str, Any]:
    try:
        schema_summary = {
            "available_tools": [
                {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["parameters"],
                }
                for t in TOOL_SCHEMAS.values()
            ]
        }

        plan_raw = ollama_chat(
            [
                {
                    "role": "system",
                    "content": (
                        "You are a strict tool planner. Choose exactly one tool from available_tools or 'none'. "
                        "Return ONLY JSON: {\"tool_name\":\"...\",\"args\":{},\"reason\":\"...\"}."
                    ),
                },
                {
                    "role": "user",
                    "content": f"User query: {query}\nTool metadata: {json.dumps(schema_summary, ensure_ascii=False)}",
                },
            ],
            temperature=0.0,
        )

        text = plan_raw.strip()
        if text.startswith("```"):
            match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text, flags=re.IGNORECASE)
            if match:
                text = match.group(1)
        else:
            s = text.find("{")
            e = text.rfind("}")
            if s != -1 and e > s:
                text = text[s : e + 1]

        plan = json.loads(text)
        tool_name = str(plan.get("tool_name", "")).strip()
        args = plan.get("args", {})

        if tool_name == "none":
            fallback = run_heuristic_agent(query)
            fallback["mode"] = "heuristic_fallback"
            fallback["fallback_reason"] = "llm_selected_none"
            fallback["llm_plan"] = {"tool_name": "none", "reason": str(plan.get("reason", ""))}
            return fallback

        if tool_name not in TOOL_SCHEMAS:
            raise ValueError(f"Unknown tool selected by LLM: {tool_name}")
        if not isinstance(args, dict):
            raise ValueError("LLM args must be a JSON object")

        required = TOOL_SCHEMAS[tool_name]["parameters"].get("required", [])
        missing = [k for k in required if k not in args]
        if missing:
            raise ValueError(f"Missing required args from LLM plan: {missing}")

        tool_result = TOOLS[tool_name](**args)

        final_answer = ollama_chat(
            [
                {
                    "role": "system",
                    "content": "You are a concise assistant. Use tool output as source of truth. Reply in 1-3 sentences.",
                },
                {
                    "role": "user",
                    "content": f"User query: {query}\nSelected tool: {tool_name}\nTool output: {tool_result}",
                },
            ],
            temperature=0.2,
        )

        return {
            "mode": "llm",
            "query": query,
            "llm_plan": {"tool_name": tool_name, "args": args, "reason": str(plan.get("reason", ""))},
            "iterations": [
                {"step": 1, "action": "LLM planned tool call", "result": {"tool_name": tool_name, "args": args}},
                {"step": 2, "action": f"Executed {tool_name}", "result": tool_result},
            ],
            "final_answer": final_answer,
        }

    except Exception as exc:
        fallback = run_heuristic_agent(query)
        fallback["mode"] = "heuristic_fallback"
        fallback["fallback_reason"] = str(exc)
        return fallback


if __name__ == "__main__":
    print("=== 5.1.3 LLM Agent (inline) ===")
    q1 = "What's the weather in Tokyo?"
    q2 = "What is the postal code for London?"
    q3 = "Calculate 25 + 17 * 3"

    for q in [q1, q2, q3]:
        print(f"\nUser: {q}")
        result = run_llm_agent(q)
        print(json.dumps(result, indent=2, ensure_ascii=False))
