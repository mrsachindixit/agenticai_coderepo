"""
Annotated MCP server example using @mcp.tool.

Purpose:
- Keep 5.1_mcp_server.py as the from-first-principles manual MCP example.
- Provide this file as the "framework ergonomics" version with decorators.

Tools exposed (same as agent.py):
- get_weather(city)
- get_pincode(city)
- calculate(expression)

Run (stdio, default):
    python 5.1.1_mcp_server_annotated.py

Run (SSE transport):
    python 5.1.1_mcp_server_annotated.py --transport sse --host 127.0.0.1 --port 8003

Dependency:
    pip install fastmcp
"""

from __future__ import annotations

import argparse

try:
    from fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover - guidance path
    raise SystemExit(
        "fastmcp is required for this example. Install with: pip install fastmcp"
    ) from exc


mcp = FastMCP("Module05 Annotated MCP Tools")


@mcp.tool(description="Get weather for a city")
def get_weather(city: str) -> str:
    temps = {"bogotá": "12°C", "new york": "18°C", "london": "8°C", "tokyo": "22°C"}
    temp = temps.get(city.lower(), "15°C")
    return f"{city}: {temp}, Partly cloudy"


@mcp.tool(description="Get postal code for a city")
def get_pincode(city: str) -> str:
    pincodes = {"bogotá": "110111", "new york": "10001", "london": "SW1A1AA", "tokyo": "100-0001"}
    pincode = pincodes.get(city.lower(), "000000")
    return f"{city}: {pincode}"


@mcp.tool(description="Safely evaluate arithmetic expression")
def calculate(expression: str) -> str:
    import ast
    try:
        node = ast.parse(expression, mode="eval")
        for n in ast.walk(node):
            if isinstance(n, ast.Call):
                return "Error: Function calls not allowed"
            if isinstance(n, ast.Name):
                return "Error: Variable names not allowed"
        code = compile(node, "<string>", "eval")
        result = eval(code, {"__builtins__": {}}, {})
        return str(result)
    except Exception as exc:
        return f"Calculation error: {exc}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Annotated MCP server using @mcp.tool")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport mode: stdio (default) or sse",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host for SSE mode")
    parser.add_argument("--port", type=int, default=8003, help="Port for SSE mode")
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run()
        return

    mcp.run(transport="sse", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
