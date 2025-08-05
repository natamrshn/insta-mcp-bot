import json
import time
import requests
from mcp.client import MCP_URL
from utils.logger import log

def call_mcp(method, arguments=None):
    payload = {
        "jsonrpc": "2.0",
        "id": int(time.time()),
        "method": method,
        "params": arguments or {}
    }
    log("→ MCP request:", json.dumps(payload, ensure_ascii=False, indent=2))
    response = requests.post(MCP_URL, json=payload)
    log("← MCP raw response:", response.text)
    response.raise_for_status()
    data = response.json()
    if "error" in data:
        log("⛔️ MCP error:", data["error"])
        raise Exception(f"MCP Error: {data['error']['message']}")
    log("✅ MCP parsed result:", json.dumps(data["result"], ensure_ascii=False, indent=2))
    return data["result"]
