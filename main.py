import datetime
from dotenv import load_dotenv
import os
import time
from instagrapi import Client
import json

from intents.dispatcher import handle_intent

# --- ENV
load_dotenv()
USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")
MCP_URL = os.getenv("MCP_URL")

print(f"[DEBUG] MCP_URL = {MCP_URL}")

if not USERNAME or not PASSWORD or not MCP_URL:
    print("❗️[FATAL] Не найдены все необходимые переменные в .env (IG_USERNAME, IG_PASSWORD, MCP_URL)")
    exit(1)

# --- Client
cl = Client()
try:
    cl.login(USERNAME, PASSWORD)
except Exception as e:
    print(f"❗️[FATAL] Ошибка входа в Instagram: {e}")
    exit(1)
print("✅ [INFO] Успешный вход в Instagram")
print(f"[INFO] Мой user_id: {cl.user_id}")

# --- State
LAST_PROCESSED_FILE = "last_processed.json"
AUTO_REPLY_TEXTS = [
    "Я поки що можу показати тільки список майстрів. Напишіть, якщо хочете його побачити!",
    "Не вдалося отримати список майстрів, спробуйте пізніше.",
    # Добавляй сюда все свои автоответы
]

# --- Загружаем last_processed_per_chat (или инициализируем)
if os.path.exists(LAST_PROCESSED_FILE):
    with open(LAST_PROCESSED_FILE, "r") as f:
        last_processed_per_chat = json.load(f)
else:
    last_processed_per_chat = {}

chat_histories = {}

# --- При первом запуске: записываем по каждому чату последнее входящее сообщение
threads = cl.direct_threads(amount=50)
for thread in threads:
    if not thread.messages:
        continue
    msgs = sorted(thread.messages, key=lambda m: m.timestamp)
    last_incoming = None
    for msg in reversed(msgs):
        if msg.user_id != cl.user_id:
            last_incoming = msg
            break
    if last_incoming:
        last_processed_per_chat[str(thread.id)] = last_incoming.id
with open(LAST_PROCESSED_FILE, "w") as f:
    json.dump(last_processed_per_chat, f)
print(f"✅ [DEBUG] Отмечены последние входящие по {len(last_processed_per_chat)} чатам. Теперь бот будет реагировать только на новые!")

# --- Main loop
last_alive_log = 0

last_logged_msg_ids = set()  # чтобы не дублировались даже в логах

while True:
    try:
        now = time.time()
        if now - last_alive_log > 30:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [ALIVE] Бот жив! Проверяю новые сообщения...")
            last_alive_log = now

        threads = cl.direct_threads(amount=15)
        for thread in threads:
            if not thread.messages:
                continue

            msgs = sorted(thread.messages, key=lambda m: m.timestamp)
            last_id = last_processed_per_chat.get(str(thread.id))

            # Ищем только ПЕРВОЕ новое валидное входящее сообщение (НЕ своё, НЕ автоответ)
            for msg in msgs:
                if msg.user_id == cl.user_id:
                    continue  # свои сообщения вообще не логируем и не обрабатываем

                if last_id and msg.id <= last_id:
                    continue  # уже обработанные пропускаем

                if msg.text and msg.text.strip() in AUTO_REPLY_TEXTS:
                    # Просто молча отмечаем как обработанное
                    last_processed_per_chat[str(thread.id)] = msg.id
                    with open(LAST_PROCESSED_FILE, "w") as f:
                        json.dump(last_processed_per_chat, f)
                    continue

                # --- Только здесь логируем новое валидное входящее! ---
                if msg.id not in last_logged_msg_ids:
                    print(f"\n[НОВОЕ] {msg.user_id} ({thread.id}): {msg.text}")
                    last_logged_msg_ids.add(msg.id)

                try:
                    handle_intent(
                        cl, msg, chat_histories,
                        last_processed_per_chat, LAST_PROCESSED_FILE, MCP_URL
                    )
                    # handle_intent сам печатает INTENT, LLM-ответ, ОТПРАВЛЕНО
                except Exception as inner_e:
                    print(f"❗️[ERROR] Ошибка при обработке intent (msg id={msg.id}): {inner_e}")

                # Всегда после обработки — отмечаем это сообщение как последнее!
                last_processed_per_chat[str(thread.id)] = msg.id
                with open(LAST_PROCESSED_FILE, "w") as f:
                    json.dump(last_processed_per_chat, f)
                print(f"[OK] Сообщение id={msg.id} отмечено как обработанное")
                break  # ТОЛЬКО одно сообщение на чат за цикл

        time.sleep(10)
    except Exception as e:
        print("❗️[FATAL] Ошибка в основном цикле:", e)
        time.sleep(30)
