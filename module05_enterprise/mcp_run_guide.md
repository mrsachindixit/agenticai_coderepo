# MCP Inspector Quick Guide (5.3 only)

From repo root:

```powershell
cd agenticai_coderepo
```

## 1) Run MCP server (5.3)

```powershell
uv run python module05_enterprise/5.3_mcp_sdk_server.py
```

Server endpoint:
- `http://localhost:8000/mcp`

## 2) Run official MCP Inspector (separate terminal)

```powershell
npx @modelcontextprotocol/inspector
```

## 3) Connect Inspector to server

- Transport: **Streamable HTTP**
- URL: `http://localhost:8000/mcp`
- Click initialize, then inspect tools/resources/prompts.

Note: Inspector runs as a separate process and connects to the already-running `5.3` server.

## 4) Single command (teaching shortcut)

Run server and Inspector together in one line:

**PowerShell:**
```powershell
Start-Process powershell -ArgumentList '-NoExit', '-Command', 'uv run python module05_enterprise/5.3_mcp_sdk_server.py'; Start-Sleep 2; npx @modelcontextprotocol/inspector
```

**bash / Git Bash:**
```bash
uv run python module05_enterprise/5.3_mcp_sdk_server.py &
sleep 2 && npx @modelcontextprotocol/inspector
```

Both start the server in the background, wait 2 seconds for it to be ready, then open the Inspector.
After Inspector opens, use transport `http` and URL `http://localhost:8000/mcp`.
