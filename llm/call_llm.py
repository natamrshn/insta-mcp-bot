# llm/call_llm.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # <--- обязательно, ДО os.getenv!!!

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
print("OPENROUTER_API_KEY:", repr(OPENROUTER_API_KEY))

def call_llm(
    chat_id,
    chat_histories,
    model="anthropic/claude-3-haiku",
    max_tokens=None,
    temperature=0.5,
    timeout=30
):
    """
    Запрос к OpenRouter API с историей чата.
    Возвращает текст ответа LLM или None.
    """
    payload = {
        "model": model,
        "messages": chat_histories[chat_id],
        "temperature": temperature
    }
    if max_tokens:
        payload["max_tokens"] = max_tokens

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://t.me/your_bot_username",
        "X-Title": "Beauty Club Bot"
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=timeout
        )
        response.raise_for_status()
        resp_json = response.json()

        if "choices" in resp_json and resp_json["choices"]:
            content = resp_json["choices"][0]["message"]["content"]
            return content.strip()
        else:
            print("⚠️ Неожиданный формат ответа LLM:", resp_json)
            return None

    except requests.exceptions.Timeout:
        print("⏰ Ошибка: LLM таймаут запроса.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка HTTP LLM: {e}")
        return None
    except Exception as e:
        print("❌ LLM request failed:", e)
        return None
