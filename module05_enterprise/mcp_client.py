
import requests
import uuid
from typing import Dict, Any

DEFAULT_URL = "http://127.0.0.1:8001/mcp/invoke"


def make_envelope(resource: str, payload: Dict[str, Any], metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    return {
        "id": str(uuid.uuid4()),
        "type": "invoke",
        "resource": resource,
        "payload": payload,
        "metadata": metadata or {},
    }


def invoke(resource: str, payload: Dict[str, Any], url: str = DEFAULT_URL):
    env = make_envelope(resource, payload)
    r = requests.post(url, json=env, timeout=30)
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    # Simple CLI demo
    print("MCP client demo — invoking compute and search on local MCP server")
    resp = invoke("compute", {"expression": "(2+3)*7"})
    print("Compute response:", resp)

    resp2 = invoke("search", {"q": "low-resource NER methods"})
    print("Search response:", resp2)
