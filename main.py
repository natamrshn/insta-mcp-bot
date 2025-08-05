from dotenv import load_dotenv
import os
import time
from instagrapi import Client
import json

from intents.dispatcher import handle_intent
from utils.state import load_answered, save_answered

# --- ENV
load_dotenv()
USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")
MCP_URL = os.getenv("MCP_URL")

print(f"[DEBUG] MCP_URL = {MCP_URL}")

if not USERNAME or not PASSWORD or not MCP_URL:
    print("❗️Ошибка: Не найдены все необходимые переменные в .env (IG_USERNAME, IG_PASSWORD, MCP_URL)")
    exit(1)

# --- Client
cl = Client()
cl.login(USERNAME, PASSWORD)
print("✅ Успешный вход в Instagram")
print(f"Мой user_id: {cl.user_id}")

# --- State
ANSWERED_MSGS_FILE = "answered_messages.json"
AUTO_REPLY_TEXTS = [
    "Я поки що можу показати тільки список майстрів. Напишіть, якщо хочете його побачити!",
    "Не вдалося отримати список майстрів, спробуйте пізніше.",
    # Добавляй сюда все свои автоответы
]

# --- Первый запуск: очистить ВСЮ историю сообщений и начать с чистого листа
answered_messages = set()
print("🧹 Очищаю историю сообщений (first run, отмечаю все существующие как обработанные)...")
threads = cl.direct_threads(amount=50)  # Можно взять больше, если много историй
for thread in threads:
    for msg in thread.messages:
        answered_messages.add(msg.id)
save_answered(ANSWERED_MSGS_FILE, answered_messages)
print(f"✅ Отмечено {len(answered_messages)} сообщений в истории. Теперь бот будет реагировать только на новые!")

chat_histories = {}

# --- Main loop
while True:
    try:
        threads = cl.direct_threads(amount=10)
        for thread in threads:
            # Читаем только последние 10 сообщений (чтобы не лезть в архив)
            for msg in reversed(thread.messages[-10:]):
                # 1. Пропустить свои исходящие
                if msg.user_id == cl.user_id:
                    continue
                # 2. Пропустить уже обработанные по id
                if msg.id in answered_messages:
                    continue
                # 3. Пропустить автоответы — и сразу занести их id в обработанные!
                if msg.text and msg.text.strip() in AUTO_REPLY_TEXTS:
                    print(f"[SKIP] Автоответ: {msg.text.strip()}")
                    answered_messages.add(msg.id)
                    save_answered(ANSWERED_MSGS_FILE, answered_messages)
                    continue

                # 4. Всё остальное — обработка
                print(f"[НОВОЕ] Входящее от {msg.user_id}: {msg.text}")
                sent_id = handle_intent(cl, msg, chat_histories, answered_messages, ANSWERED_MSGS_FILE, MCP_URL)
                # В любом случае, помечаем входящее сообщение как обработанное!
                answered_messages.add(msg.id)
                if sent_id:  # Если handle_intent возвращает id отправленного сообщения, тоже добавим!
                    answered_messages.add(sent_id)
                save_answered(ANSWERED_MSGS_FILE, answered_messages)
        time.sleep(10)
    except Exception as e:
        print("❗️Ошибка в основном цикле:", e)
        time.sleep(30)
