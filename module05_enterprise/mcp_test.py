#!/usr/bin/env python3
"""
Interactive Test Script for Tool Call Agent

Run the MCP server first: python 5.1_mcp_server.py
Then run this script in another terminal to test all agent features.
"""

import requests
import json
import uuid
from typing import Dict, Any

DEFAULT_URL = "http://127.0.0.1:8001/mcp/invoke"

def make_envelope(resource: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Create MCP envelope"""
    return {
        "id": str(uuid.uuid4()),
        "type": "invoke",
        "resource": resource,
        "payload": payload,
    }

def invoke(resource: str, payload: Dict[str, Any], url: str = DEFAULT_URL) -> Dict[str, Any]:
    """Call MCP endpoint"""
    try:
        env = make_envelope(resource, payload)
        r = requests.post(url, json=env, timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        return {
            "error": "Cannot connect to server",
            "message": "Make sure the MCP server is running: python 5.1_mcp_server.py"
        }
    except Exception as e:
        return {"error": str(e)}

def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def print_result(result: Dict[str, Any]):
    """Pretty print result"""
    print(json.dumps(result.get("payload", result), indent=2))

def test_list_tools():
    """Test: List available tools"""
    print_section("Test 1: List Available Tools")
    print("Endpoint: agent/tools")
    print("Purpose: Discover what tools the agent can use\n")
    
    resp = invoke("agent/tools", {})
    print_result(resp)
    
    if "payload" in resp and resp["payload"].get("status") == "ok":
        tools = resp["payload"]["result"]
        print(f"\n✓ Agent has {len(tools)} tools available:")
        for tool in tools:
            print(f"  • {tool['name']}: {tool['description']}")

def test_direct_weather():
    """Test: Direct weather tool call"""
    print_section("Test 2: Direct Tool Call - Weather")
    print("Endpoint: tool/weather")
    print("Purpose: Call weather tool directly (bypass agent)\n")
    
    city = "London"
    print(f"Query: Get weather for {city}\n")
    resp = invoke("tool/weather", {"city": city})
    print_result(resp)

def test_direct_pincode():
    """Test: Direct pincode tool call"""
    print_section("Test 3: Direct Tool Call - Pincode")
    print("Endpoint: tool/pincode")
    print("Purpose: Call pincode tool directly\n")
    
    city = "Tokyo"
    print(f"Query: Get pincode for {city}\n")
    resp = invoke("tool/pincode", {"city": city})
    print_result(resp)

def test_direct_calculate():
    """Test: Direct calculate tool call"""
    print_section("Test 4: Direct Tool Call - Calculate")
    print("Endpoint: tool/calculate")
    print("Purpose: Call calculator tool directly\n")
    
    expr = "25 + 17 * 3"
    print(f"Query: Calculate {expr}\n")
    resp = invoke("tool/calculate", {"expression": expr})
    print_result(resp)

def test_agent_weather():
    """Test: Agent orchestration - Weather"""
    print_section("Test 5: Agent Orchestration - Weather")
    print("Endpoint: agent/invoke")
    print("Purpose: Agent decides which tool to use\n")
    
    query = "What's the weather in Bogotá?"
    print(f"Query: '{query}'\n")
    print("Agent Decision Process:")
    print("  1. Parse query")
    print("  2. Detect keyword 'weather'")
    print("  3. Extract city 'bogotá'")
    print("  4. Select get_weather tool")
    print("  5. Execute with city='Bogotá'")
    print("  6. Compose response\n")
    
    resp = invoke("agent/invoke", {"query": query})
    print_result(resp)
    
    if "payload" in resp and resp["payload"].get("status") == "ok":
        result = resp["payload"]["result"]
        print(f"\n✓ Agent made {len(result.get('iterations', []))} tool call(s)")
        for iteration in result.get("iterations", []):
            print(f"  Step {iteration['step']}: {iteration['action']}")
            print(f"  Result: {iteration['result']}")

def test_agent_pincode():
    """Test: Agent orchestration - Pincode"""
    print_section("Test 6: Agent Orchestration - Pincode")
    print("Endpoint: agent/invoke\n")
    
    query = "Tell me the postal code for New York"
    print(f"Query: '{query}'\n")
    
    resp = invoke("agent/invoke", {"query": query})
    print_result(resp)

def test_agent_calculate():
    """Test: Agent orchestration - Calculate"""
    print_section("Test 7: Agent Orchestration - Calculation")
    print("Endpoint: agent/invoke\n")
    
    query = "Calculate 100 plus 50 times 2"
    print(f"Query: '{query}'\n")
    
    resp = invoke("agent/invoke", {"query": query})
    print_result(resp)

def test_agent_unknown():
    """Test: Agent with out-of-scope query"""
    print_section("Test 8: Agent Graceful Fallback")
    print("Endpoint: agent/invoke")
    print("Purpose: Show fallback when query is out of scope\n")
    
    query = "What is the meaning of life?"
    print(f"Query: '{query}'\n")
    print("Agent Decision Process:")
    print("  1. Parse query")
    print("  2. No keywords match (weather, pincode, calculate)")
    print("  3. No tools selected")
    print("  4. Return helpful message\n")
    
    resp = invoke("agent/invoke", {"query": query})
    print_result(resp)

def test_error_handling():
    """Test: Error handling"""
    print_section("Test 9: Error Handling")
    print("Endpoint: tool/weather")
    print("Purpose: Show error when required parameter is missing\n")
    
    print("Query: Call weather tool with missing 'city' parameter\n")
    resp = invoke("tool/weather", {})
    print_result(resp)

def interactive_mode():
    """Interactive test mode"""
    print_section("Interactive Agent Testing")
    print("Commands:")
    print("  'tools'     - List available tools")
    print("  'weather'   - Direct weather query")
    print("  'pincode'   - Direct pincode query")
    print("  'calc'      - Direct calculation")
    print("  'agent'     - Run agent orchestration")
    print("  'quit'      - Exit\n")
    
    examples = {
        "weather": {
            "cmd": "What's the weather in London?",
            "opts": ["Bogotá", "New York", "London", "Tokyo"]
        },
        "pincode": {
            "cmd": "What is the postal code for Tokyo?",
            "opts": ["Bogotá", "New York", "London", "Tokyo"]
        },
        "calc": {
            "cmd": "25 + 17 * 3",
            "opts": ["2 + 2", "10 * 5", "100 - 25", "(50 + 50) * 2"]
        },
        "agent": {
            "cmd": "What's the weather in London?",
            "opts": [
                "Weather in Bogotá",
                "Pincode for New York",
                "Calculate 100 + 50 * 2",
                "Tell me something"
            ]
        }
    }
    
    while True:
        user_input = input("Enter command (or 'help' for options): ").strip().lower()
        
        if user_input == "quit":
            print("Goodbye!")
            break
        elif user_input == "help":
            print("\nAvailable commands:")
            for cmd in examples:
                print(f"  {cmd} - {examples[cmd]['cmd']}")
            print("  quit - Exit")
        elif user_input == "tools":
            test_list_tools()
        elif user_input == "weather":
            city = input("Enter city name (default: London): ").strip() or "London"
            resp = invoke("tool/weather", {"city": city})
            print()
            print_result(resp)
        elif user_input == "pincode":
            city = input("Enter city name (default: New York): ").strip() or "New York"
            resp = invoke("tool/pincode", {"city": city})
            print()
            print_result(resp)
        elif user_input == "calc":
            expr = input("Enter expression (default: 2 + 2): ").strip() or "2 + 2"
            resp = invoke("tool/calculate", {"expression": expr})
            print()
            print_result(resp)
        elif user_input == "agent":
            query = input("Enter query (default: What's the weather in London?): ").strip() or "What's the weather in London?"
            resp = invoke("agent/invoke", {"query": query})
            print()
            print_result(resp)
        else:
            print("Unknown command. Type 'help' for options.")

def main():
    """Main test runner"""
    import sys
    
    print("\n" + "🤖 Tool Call Agent - Test Suite".center(70))
    print("Version 1.0".center(70))
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_mode()
    else:
        print("\nRunning automated tests...\n")
        try:
            test_list_tools()
            test_direct_weather()
            test_direct_pincode()
            test_direct_calculate()
            test_agent_weather()
            test_agent_pincode()
            test_agent_calculate()
            test_agent_unknown()
            test_error_handling()
            
            print_section("✓ All tests completed!")
            print("Next steps:")
            print("  1. Review the results above")
            print("  2. Try interactive mode: python mcp_test.py interactive")
            print("  3. Modify 5.1_mcp_server.py to add new tools\n")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    main()
