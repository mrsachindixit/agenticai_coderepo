import ast
import os

import requests
from mcp.server.fastmcp import FastMCP, Context

OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


def ollama_chat(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": 0.3},
    }
    r = requests.post(f"{OLLAMA_BASE}/api/chat", json=payload, timeout=120)
    r.raise_for_status()
    return r.json().get("message", {}).get("content", "")

mcp = FastMCP("demo", stateless_http=True, json_response=True)


@mcp.tool()
def get_weather(city: str) -> str:
    temps = {"london": "8°C", "tokyo": "22°C", "new york": "18°C", "bogotá": "12°C"}
    return f"{city}: {temps.get(city.lower(), '15°C')}, partly cloudy"


@mcp.tool()
def calculate(expression: str) -> str:
    try:
        node = ast.parse(expression, mode="eval")
        for n in ast.walk(node):
            if isinstance(n, (ast.Call, ast.Name)):
                return "Error: only arithmetic allowed"
        return str(eval(compile(node, "<string>", "eval"), {"__builtins__": {}}, {}))
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
async def describe_city(city: str, ctx: Context) -> str:
    """Call a real LLM to describe the city."""
    await ctx.info(f"Calling LLM for {city}")
    await ctx.report_progress(0.5, 1.0, "querying LLM")
    answer = ollama_chat(f"Describe {city} in exactly two sentences.")
    await ctx.report_progress(1.0, 1.0, "done")
    return answer


@mcp.resource("data://cities")
def list_cities() -> str:
    return "london, tokyo, new york, bogotá"


@mcp.resource("data://city/{name}")
def city_detail(name: str) -> str:
    details = {"london": "Capital of UK", "tokyo": "Capital of Japan"}
    return details.get(name.lower(), f"{name}: no details available")


@mcp.prompt()
def weather_prompt(city: str) -> str:
    return f"Get the weather for {city} and summarize it in one sentence."


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
