def handle_show_service_list(user_id, chat_histories, mcp_url):
    import requests
    import json

    # 1. Получаем сервисы через MCP
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "get_service_list",
            "arguments": {}
        }
    }
    resp = requests.post(mcp_url, json=payload, timeout=15)
    print("[DEBUG] MCP raw response:", resp.text)
    data = resp.json()
    services = []
    try:
        text = data["result"]["content"][0]["text"]
        services = json.loads(text)["services"]
    except Exception as e:
        print("Ошибка разбора сервисов:", e)
        return "Не вдалося отримати список послуг, спробуйте пізніше."

    if not services:
        return "Наразі немає жодних послуг для запису."

    # Только названия
    lines = ["Ось наші основні послуги:\n"]
    for svc in services:
        lines.append(f"• {svc['title']}")
    lines.append("\nБажаєте дізнатися більше або записатись на якусь із послуг?")
    return "\n".join(lines)
