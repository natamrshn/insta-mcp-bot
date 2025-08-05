import requests
import os
import json
import time

MCP_URL = os.getenv("MCP_URL")
def get_staff_list_from_mcp(mcp_url):
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get_staff_list",
                "arguments": {}
            }
        }
        resp = requests.post(mcp_url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        if "result" in data:
            staff = json.loads(data["result"]["content"][0]["text"])["staff"]
            print("👥 Отримані майстри:", staff)
            return staff
        else:
            print("⚠️ Не удалось получить staff из MCP", data)
            return []
    except Exception as e:
        print("❌ Помилка при отриманні списку майстрів з MCP:", e)
        return None
