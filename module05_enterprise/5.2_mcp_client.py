
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


def print_response(title: str, resp: Dict):
    """Pretty print response"""
    print(f"\n{'='*60}")
    print(f"📌 {title}")
    print(f"{'='*60}")
    import json
    print(json.dumps(resp.get('payload', resp), indent=2))


if __name__ == "__main__":
    print("🤖 MCP Tool Call Agent Demo\n")
    print("This demonstrates a self-contained tool call agent")
    print("exposed via MCP endpoints for student learning.\n")
    
    # ========== TRADITIONAL ENDPOINTS ==========
    print("\n" + "🔧 TRADITIONAL TOOLS".center(60))
    
    resp = invoke("compute", {"expression": "(2+3)*7"})
    print_response("Compute: (2+3)*7", resp)
    
    resp = invoke("search", {"q": "low-resource NER methods"})
    print_response("Search: low-resource NER methods", resp)
    
    # ========== TOOL CALL AGENT ENDPOINTS ==========
    print("\n" + "🤖 TOOL CALL AGENT ENDPOINTS".center(60))
    
    # List available tools
    resp = invoke("agent/tools", {})
    print_response("Available Tools in Agent", resp)
    
    # Direct tool calls
    resp = invoke("tool/weather", {"city": "Bogotá"})
    print_response("Direct Tool: Get Weather for Bogotá", resp)
    
    resp = invoke("tool/pincode", {"city": "London"})
    print_response("Direct Tool: Get Pincode for London", resp)
    
    resp = invoke("tool/calculate", {"expression": "25 + 17 * 3"})
    print_response("Direct Tool: Calculate 25 + 17 * 3", resp)
    
    # Agent orchestration (agent decides which tools to call)
    print("\n" + "🧠 AGENT ORCHESTRATION (Agent Decides Tools)".center(60))
    
    resp = invoke("agent/invoke", {"query": "What's the weather in Tokyo?"})
    print_response("Agent: Weather Query", resp)
    
    resp = invoke("agent/invoke", {"query": "Tell me the postal code for New York"})
    print_response("Agent: Postal Code Query", resp)
    
    resp = invoke("agent/invoke", {"query": "Calculate 100 plus 50 times 2"})
    print_response("Agent: Arithmetic Query", resp)
    
    resp = invoke("agent/invoke", {"query": "What is the meaning of life?"})
    print_response("Agent: Out-of-Scope Query (Shows Graceful Fallback)", resp)
