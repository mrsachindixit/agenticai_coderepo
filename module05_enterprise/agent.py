"""
Tool Call Agent - Self-contained educational implementation

This module demonstrates core agent concepts:
- Tool definition with schemas
- Heuristic-based tool selection
- Tool execution and error handling
- Response composition

NOTE: This uses heuristic-based tool selection for clarity and learning.
Production systems typically use LLM-based selection. The core concepts
remain the same regardless of how tools are selected.
"""

import ast
import re
from typing import Any, Dict, List


class ToolCallAgent:
    """Self-contained tool call agent for student learning.
    
    Educational implementation that demonstrates:
    1. Tool Definition: Using OpenAI function calling format
    2. Tool Selection: Heuristic pattern matching on keywords
    3. Tool Execution: Safe invocation with parameter handling
    4. Response Composition: Collecting and formatting results
    
    This agent uses keyword-based heuristics to decide which tools to call.
    Production agents would typically use LLM-based selection instead.
    """
    
    def __init__(self):
        """Initialize agent with tools and schemas."""
        self.tools = {
            "get_weather": self._get_weather,
            "get_pincode": self._get_pincode,
            "calculate": self._calculate,
        }
        self.tool_schemas = {
            "get_weather": {
                "name": "get_weather",
                "description": "Get weather for a city",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string", "description": "City name"}
                    },
                    "required": ["city"]
                }
            },
            "get_pincode": {
                "name": "get_pincode",
                "description": "Get postal code for a city",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string", "description": "City name"}
                    },
                    "required": ["city"]
                }
            },
            "calculate": {
                "name": "calculate",
                "description": "Perform arithmetic calculation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "Math expression (e.g., '2+3*4')"}
                    },
                    "required": ["expression"]
                }
            }
        }
    
    # ==================== TOOL IMPLEMENTATIONS ====================
    
    def _get_weather(self, city: str) -> str:
        """Mock weather tool - retrieves weather for a city.
        
        Args:
            city: City name
            
        Returns:
            Weather information string
        """
        temps = {
            "bogotá": "12°C",
            "new york": "18°C",
            "london": "8°C",
            "tokyo": "22°C"
        }
        temp = temps.get(city.lower(), "15°C")
        return f"{city}: {temp}, Partly cloudy"
    
    def _get_pincode(self, city: str) -> str:
        """Mock pincode tool - retrieves postal code for a city.
        
        Args:
            city: City name
            
        Returns:
            Postal code information string
        """
        pincodes = {
            "bogotá": "110111",
            "new york": "10001",
            "london": "SW1A1AA",
            "tokyo": "100-0001"
        }
        pincode = pincodes.get(city.lower(), "000000")
        return f"{city}: {pincode}"
    
    def _calculate(self, expression: str) -> str:
        """Safe arithmetic calculator - evaluates math expressions securely.
        
        Uses AST (Abstract Syntax Tree) parsing to safely evaluate
        arithmetic expressions while blocking dangerous operations.
        
        Allowed: +, -, *, /, (), **, %
        Blocked: function calls, variable access
        
        Args:
            expression: Math expression string (e.g., "2+3*4")
            
        Returns:
            Calculation result or error message
        """
        try:
            node = ast.parse(expression, mode="eval")
            # Security check: block function calls and variable access
            for n in ast.walk(node):
                if isinstance(n, ast.Call):
                    return "Error: Function calls not allowed"
                if isinstance(n, ast.Name):
                    return "Error: Variable names not allowed"
            # Safely evaluate the expression
            code = compile(node, '<string>', 'eval')
            result = eval(code, {"__builtins__": {}}, {})
            return str(result)
        except Exception as e:
            return f"Calculation error: {str(e)}"
    
    # ==================== AGENT INTERFACE ====================
    
    def invoke_tool(self, tool_name: str, params: Dict[str, Any]) -> str:
        """Execute a tool by name with given parameters.
        
        Args:
            tool_name: Name of the tool to invoke
            params: Parameters for the tool
            
        Returns:
            Tool execution result or error message
        """
        if tool_name not in self.tools:
            return f"Unknown tool: {tool_name}"
        tool_func = self.tools[tool_name]
        return tool_func(**params)
    
    def run_agent_loop(self, user_query: str, max_iterations: int = 5) -> Dict[str, Any]:
        """Main agent orchestration loop.
        
        This method demonstrates the core agent pattern:
        1. Parse user query
        2. Decide which tools to use (heuristic-based)
        3. Execute selected tools
        4. Collect and compose results
        
        Args:
            user_query: User's natural language query
            max_iterations: Maximum tool calls (for safety)
            
        Returns:
            Agent state dict containing:
            - query: Original user query
            - iterations: List of tool calls and results
            - final_answer: Composed response
            - tools_available: Available tools (if no match)
        """
        agent_state = {
            "query": user_query,
            "iterations": [],
            "final_answer": None
        }
        
        # STEP 1: Extract keywords from query
        query_lower = user_query.lower()
        tools_to_call = []
        
        # STEP 2: Heuristic-based tool selection
        # NOTE: Production systems would use LLM here instead
        
        # Weather tool selection
        if any(w in query_lower for w in ["weather", "temperature", "climate", "hot", "cold"]):
            cities = ["bogotá", "new york", "london", "tokyo"]
            for city in cities:
                if city in query_lower:
                    tools_to_call.append(("get_weather", {"city": city}))
                    break
        
        # Pincode tool selection
        if any(w in query_lower for w in ["pincode", "postal", "zip", "code"]):
            cities = ["bogotá", "new york", "london", "tokyo"]
            for city in cities:
                if city in query_lower:
                    tools_to_call.append(("get_pincode", {"city": city}))
                    break
        
        # Calculator tool selection
        if any(w in query_lower for w in ["calculate", "math", "compute", "plus", "minus"]):
            # Try to extract arithmetic expression from query
            match = re.search(r'(\d+\s*[\+\-\*/]\s*\d+)', query_lower)
            if match:
                tools_to_call.append(("calculate", {"expression": match.group(1)}))
        
        # STEP 3: Graceful fallback for unknown queries
        if not tools_to_call:
            return {
                "query": user_query,
                "iterations": [],
                "final_answer": "I can help with weather, pincode, or calculation queries. Try asking: 'What's the weather in Bogotá?' or 'What is the pincode for London?'",
                "tools_available": list(self.tool_schemas.keys())
            }
        
        # STEP 4: Execute selected tools and collect results
        tool_results = []
        for tool_name, params in tools_to_call:
            result = self.invoke_tool(tool_name, params)
            tool_results.append({
                "tool": tool_name,
                "params": params,
                "result": result
            })
            # Track decision steps
            agent_state["iterations"].append({
                "step": len(agent_state["iterations"]) + 1,
                "action": f"Called {tool_name}",
                "result": result
            })
        
        # STEP 5: Compose final response from results
        answer_parts = ["Based on the tools called:"]
        for tr in tool_results:
            answer_parts.append(f"- {tr['tool']}: {tr['result']}")
        
        agent_state["final_answer"] = "\n".join(answer_parts)
        return agent_state
