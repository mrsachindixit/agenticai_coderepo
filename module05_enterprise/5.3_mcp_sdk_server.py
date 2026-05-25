

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from mcp.server.fastmcp import FastMCP
import uvicorn
import os

mcp = FastMCP("annotation-demo", stateless_http=True, json_response=True)


@mcp.tool()
def get_weather(city: str) -> str:
    temps = {"london": "8°C", "tokyo": "22°C", "new york": "18°C", "bogotá": "12°C"}
    return f"{city}: {temps.get(city.lower(), '15°C')}, partly cloudy"


@mcp.tool()
def get_pincode(city: str) -> str:
    pincodes = {"london": "SW1A1AA", "tokyo": "100-0001", "new york": "10001", "bogotá": "110111"}
    return f"{city}: {pincodes.get(city.lower(), '000000')}"


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


@mcp.prompt()
def pincode_prompt(city: str) -> str:
        return f"Find the postal code for {city} and return only one line."


TOOL_SCHEMAS = [
        {
                "name": "get_weather",
                "description": "Get weather for a city",
                "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
        },
        {
                "name": "get_pincode",
                "description": "Get pincode/postal code for a city",
                "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
        },
]

PROMPT_SCHEMAS = [
        {
                "name": "weather_prompt",
                "description": "Prompt template for weather lookup",
                "template": "Get the weather for {city} and summarize it in one sentence.",
        },
        {
                "name": "pincode_prompt",
                "description": "Prompt template for pincode lookup",
                "template": "Find the postal code for {city} and return only one line.",
        },
]

RESOURCE_SCHEMAS = [
        {"uri": "data://cities", "description": "List supported cities"},
        {"uri": "data://city/{name}", "description": "City detail by name"},
]


# ==================== DEMO-ONLY WRAPPER (KEEP LAST) ====================
demo = FastAPI(title="MCP Annotation Teaching Server")


@demo.get("/catalog")
async def mcp_catalog():
        return {
                "server": {
                        "name": "annotation-demo",
                        "version": "1.0.0",
                        "transport": "streamable-http",
                    "endpoint": "/mcp",
                        "disclaimer": "This browser inspector is demo-only. Real applications typically use MCP clients/SDKs.",
                },
                "annotations": {
                        "tools": "@mcp.tool",
                        "resources": "@mcp.resource",
                        "prompts": "@mcp.prompt",
                },
                "tools": TOOL_SCHEMAS,
                "resources": RESOURCE_SCHEMAS,
                "prompts": PROMPT_SCHEMAS,
        }


@demo.get("/", response_class=HTMLResponse)
async def inspector_home():
        return """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>MCP Annotation Inspector</title>
    <style>
        :root {
            --bg:#0b1020; --panel:#131a2d; --panel2:#0f1526; --text:#e5e7eb;
            --muted:#9ca3af; --accent:#60a5fa; --ok:#34d399; --border:#25314f;
        }
        *{box-sizing:border-box} body{margin:0;font-family:Segoe UI,Arial,sans-serif;background:var(--bg);color:var(--text)}
        .layout{display:grid;grid-template-columns:250px 1fr;min-height:100vh}
        .side{background:#0a0f1f;border-right:1px solid var(--border);padding:16px}
        .main{padding:18px}.card{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:14px;margin-bottom:12px}
        .mono{font-family:Consolas,monospace;background:var(--panel2);border:1px solid var(--border);padding:2px 6px;border-radius:6px}
        .muted{color:var(--muted)} .badge{color:var(--ok);font-weight:600}
        ul{margin:8px 0 0;padding-left:18px} li{margin:6px 0}
        .grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
    </style>
</head>
<body>
    <div class="layout">
        <aside class="side">
            <h3 style="margin-top:0">MCP Inspector</h3>
            <p class="muted">Annotation-first teaching view</p>
            <p class="muted" style="font-size:12px">Production apps usually use MCP clients/SDKs directly.</p>
        </aside>
        <main class="main">
            <div class="card">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <h2 style="margin:0">Server Catalog</h2>
                    <span id="status" class="badge">Loading...</span>
                </div>
                <div class="muted" style="margin-top:8px">MCP endpoint (real mode): <span class="mono">/mcp</span></div>
            </div>

            <div class="grid">
                <section class="card"><h3 style="margin:0">Tools <span class="mono">@mcp.tool</span></h3><ul id="tools"></ul></section>
                <section class="card"><h3 style="margin:0">Resources <span class="mono">@mcp.resource</span></h3><ul id="resources"></ul></section>
            </div>
            <section class="card"><h3 style="margin:0">Prompts <span class="mono">@mcp.prompt</span></h3><ul id="prompts"></ul></section>
        </main>
    </div>

    <script>
        async function boot() {
            const res = await fetch('/catalog');
            const data = await res.json();
            document.getElementById('status').textContent = 'Connected';

            const tools = document.getElementById('tools');
            data.tools.forEach(t => {
                const li = document.createElement('li');
                li.innerHTML = '<span class="mono">' + t.name + '</span> - ' + t.description;
                tools.appendChild(li);
            });

            const resources = document.getElementById('resources');
            data.resources.forEach(r => {
                const li = document.createElement('li');
                li.innerHTML = '<span class="mono">' + r.uri + '</span> - ' + r.description;
                resources.appendChild(li);
            });

            const prompts = document.getElementById('prompts');
            data.prompts.forEach(p => {
                const li = document.createElement('li');
                li.innerHTML = '<span class="mono">' + p.name + '</span> - ' + p.template;
                prompts.appendChild(li);
            });
        }

        boot().catch(() => {
            document.getElementById('status').textContent = 'Error';
        });
    </script>
</body>
</html>
"""


if __name__ == "__main__":
    if os.getenv("MCP_DEMO_UI", "0") == "1":
        uvicorn.run(demo, host="127.0.0.1", port=8001)
    else:
        mcp.run(transport="streamable-http")
