from prompts.system_prompt_ua import SYSTEM_PROMPT
from intents.handler import INTENT_HANDLERS
from llm.call_llm import call_llm

def parse_intent_llm(user_id, chat_histories):
    prompt = (
        "Проаналізуй повідомлення користувача і поверни назву інтенції з цього списку (show_staff_list, show_service_list, book, other) одним словом без коментарів. "
        "Приклад: Якщо користувач хоче побачити список майстрів, поверни show_staff_list."
    )
    messages = chat_histories[user_id][:]
    messages.append({"role": "system", "content": prompt})
    intent = call_llm(user_id, {user_id: messages}, temperature=0)
    return intent.strip().split()[0] if intent else "other"

def handle_intent(cl, msg, chat_histories, answered_messages, answered_msgs_file, mcp_url):
    user_id = msg.user_id
    message_id = msg.id
    user_message = msg.text.strip()

    # 1. История
    if user_id not in chat_histories:
        chat_histories[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    chat_histories[user_id].append({"role": "user", "content": user_message})

    # 2. Интент
    intent = parse_intent_llm(user_id, chat_histories)
    print(f"✨ INTENT = {intent}")

    # 3. Routing через словарь (switch-case)
    handler = INTENT_HANDLERS.get(intent)
    if handler:
        reply = handler(user_id, chat_histories, mcp_url)
    else:
        reply = "Я поки що можу показати тільки список майстрів. Напишіть, якщо хочете його побачити!"

    # 4. Отправка
    try:
        sent_msg = cl.direct_send(reply, [user_id])
        print(f"[ОТПРАВЛЕНО] user_id={user_id}, msg_id={message_id} → {reply}")
        answered_messages.add(message_id)
        from utils.state import save_answered
        save_answered(answered_msgs_file, answered_messages)
        # Важно: возвращаем id отправленного сообщения, если нужно отслеживать в будущем!
        return getattr(sent_msg, 'id', None)
    except Exception as e:
        print("❗️Ошибка отправки в Direct:", e)
        return None
