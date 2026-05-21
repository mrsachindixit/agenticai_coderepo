
"""
MCP Server exposing a Tool Call Agent.

This server demonstrates:
- Tool Call Agent (SEE: agent.py for agent implementation)
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

from agent import ToolCallAgent

app = FastAPI(title="MCP Server with Tool Call Agent")

# ==================== AGENT SETUP ====================
# Import and initialize the agent (see agent.py for implementation)
tool_call_agent = ToolCallAgent()


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
            agent_result = tool_call_agent.run_agent_loop(user_query)
            body = {"status": "ok", "result": agent_result}
    
    elif resource == "agent/tools":
        """List available tools in the agent"""
        tools_list = [
            {
                "name": schema["name"],
                "description": schema["description"],
                "parameters": schema.get("parameters", {})
            }
            for schema in tool_call_agent.tool_schemas.values()
        ]
        body = {"status": "ok", "result": tools_list}
    
    elif resource == "tool/weather":
        """Direct tool call: get weather"""
        city = payload.get("city", "")
        if not city:
            body = {"status": "error", "error": "Missing 'city' parameter"}
        else:
            result = tool_call_agent.invoke_tool("get_weather", {"city": city})
            body = {"status": "ok", "result": result}
    
    elif resource == "tool/pincode":
        """Direct tool call: get pincode"""
        city = payload.get("city", "")
        if not city:
            body = {"status": "error", "error": "Missing 'city' parameter"}
        else:
            result = tool_call_agent.invoke_tool("get_pincode", {"city": city})
            body = {"status": "ok", "result": result}
    
    elif resource == "tool/calculate":
        """Direct tool call: calculate expression"""
        expression = payload.get("expression", "")
        if not expression:
            body = {"status": "error", "error": "Missing 'expression' parameter"}
        else:
            result = tool_call_agent.invoke_tool("calculate", {"expression": expression})
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
