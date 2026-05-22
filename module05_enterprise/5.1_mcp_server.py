
"""
MCP Server exposing a Tool Call Agent (inline-first teaching version).

This server demonstrates:
- Tool definitions inline in this file
- Simple deterministic agent loop inline in this file
- MCP Protocol patterns (request/response envelopes)
- FastAPI integration with MCP
- Multiple endpoint patterns (agent orchestration vs. direct tool calls)
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict
import uvicorn
import time
import ast
import re

app = FastAPI(title="MCP Server with Tool Call Agent")


# ==================== INLINE TOOLS ====================
def get_weather(city: str) -> str:
    temps = {"bogotá": "12°C", "new york": "18°C", "london": "8°C", "tokyo": "22°C"}
    temp = temps.get(city.lower(), "15°C")
    return f"{city}: {temp}, Partly cloudy"


def get_pincode(city: str) -> str:
    pincodes = {"bogotá": "110111", "new york": "10001", "london": "SW1A1AA", "tokyo": "100-0001"}
    pincode = pincodes.get(city.lower(), "000000")
    return f"{city}: {pincode}"


def calculate(expression: str) -> str:
    result, err = _safe_eval(expression)
    return str(result) if err is None else f"Calculation error: {err}"


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


def run_agent_loop(user_query: str) -> Dict[str, Any]:
    """Simple deterministic tool-routing agent loop (heuristic)."""
    q = user_query.lower()
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
        match = re.search(r"(\d+\s*[\+\-\*/]\s*\d+)", q)
        if match:
            planned.append(("calculate", {"expression": match.group(1)}))

    if not planned:
        return {
            "query": user_query,
            "iterations": [],
            "final_answer": "I can help with weather, pincode, or calculation queries. Try asking: 'What's the weather in Bogotá?' or 'What is the pincode for London?'",
            "tools_available": list(TOOL_SCHEMAS.keys()),
        }

    iterations = []
    parts = ["Based on the tools called:"]
    for idx, (name, args) in enumerate(planned, start=1):
        result = TOOLS[name](**args)
        iterations.append({"step": idx, "action": f"Called {name}", "result": result})
        parts.append(f"- {name}: {result}")

    return {
        "query": user_query,
        "iterations": iterations,
        "final_answer": "\n".join(parts),
    }


class Envelope(BaseModel):
    id: str
    type: str
    resource: str
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = {}


@app.post("/mcp/invoke")
async def invoke(envelope: Envelope):
    """MCP invoke endpoint with tool call agent support.

    Resources:
    - "compute": Simple arithmetic evaluation
    - "search": Sample search results
    - "summarize": Text summarization
    - "agent/invoke": Tool call agent
    - "agent/tools": List available tools
    - "tool/weather": Get weather for a city
    - "tool/pincode": Get pincode for a city
    """
    start = time.time()
    resource = envelope.resource
    payload = envelope.payload or {}

    # Dispatch to handlers
    if resource == "compute":
        expr = payload.get("expression", "")
        result, err = _safe_eval(expr)
        status = "ok" if err is None else "error"
        body = {"status": status, "result": result, "error": err}
    
    elif resource == "search":
        q = payload.get("q", "")
        results = [{"title": f"Result for {q} #{i}", "url": f"https://example.org/{i}", "snippet": "Summary..."} for i in range(1, 4)]
        body = {"status": "ok", "result": results}
    
    elif resource == "summarize":
        text = payload.get("text", "")
        body = {"status": "ok", "result": text[:200]}
    
    # ========== TOOL CALL AGENT RESOURCES ==========
    elif resource == "agent/invoke":
        """Invoke the tool call agent"""
        user_query = payload.get("query", "")
        if not user_query:
            body = {"status": "error", "error": "Missing 'query' parameter"}
        else:
            agent_result = run_agent_loop(user_query)
            body = {"status": "ok", "result": agent_result}
    
    elif resource == "agent/tools":
        """List available tools in the agent"""
        tools_list = [
            {
                "name": schema["name"],
                "description": schema["description"],
                "parameters": schema.get("parameters", {})
            }
            for schema in TOOL_SCHEMAS.values()
        ]
        body = {"status": "ok", "result": tools_list}
    
    elif resource == "tool/weather":
        """Direct tool call: get weather"""
        city = payload.get("city", "")
        if not city:
            body = {"status": "error", "error": "Missing 'city' parameter"}
        else:
            result = get_weather(city)
            body = {"status": "ok", "result": result}
    
    elif resource == "tool/pincode":
        """Direct tool call: get pincode"""
        city = payload.get("city", "")
        if not city:
            body = {"status": "error", "error": "Missing 'city' parameter"}
        else:
            result = get_pincode(city)
            body = {"status": "ok", "result": result}
    
    elif resource == "tool/calculate":
        """Direct tool call: calculate expression"""
        expression = payload.get("expression", "")
        if not expression:
            body = {"status": "error", "error": "Missing 'expression' parameter"}
        else:
            result = calculate(expression)
            body = {"status": "ok", "result": result}
    
    else:
        body = {"status": "error", "error": f"unknown resource: {resource}"}

    elapsed = time.time() - start
    resp = {
        "id": envelope.id,
        "type": "response",
        "resource": envelope.resource,
        "metadata": {"elapsed": elapsed},
        "payload": body,
    }
    return resp


def _safe_eval(expr: str):
    """Evaluate a simple arithmetic expression safely using ast.

    Only allows numeric literals and +,-,*,/,(),**,%.
    """
    try:
        node = ast.parse(expr, mode="eval")
        for n in ast.walk(node):
            if isinstance(n, ast.Call):
                return None, "calls not allowed"
            if isinstance(n, ast.Name):
                return None, "names not allowed"
        code = compile(node, '<string>', 'eval')
        return eval(code, {__builtins__: {}}, {}), None
    except Exception as e:
        return None, str(e)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
