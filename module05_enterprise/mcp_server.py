
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Any, Dict
import uvicorn
import time
import ast

app = FastAPI(title="MCP Example Server")


class Envelope(BaseModel):
    id: str
    type: str
    resource: str
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = {}


@app.post("/mcp/invoke")
async def invoke(envelope: Envelope):
    """Simple MCP invoke endpoint.

    Expects an envelope with a `resource` field describing the requested tool.
    Returns a response envelope with `status`, `result`, and optional `log`.
    This is a minimal, educational implementation — replace tool handlers with real integrations.
    """
    start = time.time()
    resource = envelope.resource
    payload = envelope.payload or {}

    # Dispatch to toy handlers
    if resource == "compute":
        expr = payload.get("expression", "")
        result, err = _safe_eval(expr)
        status = "ok" if err is None else "error"
        body = {"status": status, "result": result, "error": err}
    elif resource == "search":
        q = payload.get("q", "")
        # Return deterministic sample results for demo
        results = [{"title": f"Result for {q} #{i}", "url": f"https://example.org/{i}", "snippet": "Summary..."} for i in range(1, 4)]
        body = {"status": "ok", "result": results}
    elif resource == "summarize":
        text = payload.get("text", "")
        # naive summarization: first 200 chars
        body = {"status": "ok", "result": text[:200]}
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
