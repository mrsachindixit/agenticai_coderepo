"""Annotated MCP client demo."""

from __future__ import annotations

import argparse
import asyncio

try:
    from fastmcp import Client
except ImportError as exc:  # pragma: no cover - guidance path
    raise SystemExit(
        "fastmcp is required for this example. Install with: pip install fastmcp"
    ) from exc


async def run_demo(server_url: str) -> None:
    async with Client(server_url) as client:
        tools = await client.list_tools()
        print("\n=== Tools exposed by annotated server ===")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")

        print("\n=== Tool calls ===")
        weather = await client.call_tool("get_weather", {"city": "Bogotá"})
        print("get_weather:", weather)

        pincode = await client.call_tool("get_pincode", {"city": "London"})
        print("get_pincode:", pincode)

        calc = await client.call_tool("calculate", {"expression": "25 + 17 * 3"})
        print("calculate:", calc)


def main() -> None:
    parser = argparse.ArgumentParser(description="Annotated MCP client demo")
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:8003/sse",
        help="SSE endpoint of annotated MCP server",
    )
    args = parser.parse_args()

    asyncio.run(run_demo(args.url))


if __name__ == "__main__":
    main()
