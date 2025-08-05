from llm.call_llm import call_llm
from mcp.client import get_staff_list_from_mcp

def handle_show_staff_list(user_id, chat_histories, mcp_url):
    staff = get_staff_list_from_mcp(mcp_url)
    print("👥 staff:", staff)
    if not staff:
        return "⚠️ Не вдалося отримати список майстрів."

    formatted_staff = ", ".join(f"{emp['name']} – {emp.get('specialization', '')}".strip() for emp in staff)
    system_prompt = (
        "Ти — адміністраторка салону краси Beauty Club 💇‍♀️✨.\n"
        "Користувач просить показати реальний список майстрів. Відповідай живо, кокетливо, коротко, не вигадуй імен.\n\n"
        f"Список: {formatted_staff}.\n"
        "Не додавай зайвого, просто переліч реальних майстрів.\n"
        "Запитай, чи хоче користувач записатись до когось із них."
    )

    chat_histories[user_id].append({"role": "system", "content": system_prompt})
    chat_histories[user_id].append({"role": "user", "content": "Покажи список майстрів"})

    try:
        reply = call_llm(user_id, chat_histories, temperature=0.55)
        print("🤖 LLM-відповідь:", reply)
        chat_histories[user_id].append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        print("❌ GPT error у show_staff_list:", e)
        return "⚠️ Не вдалося згенерувати відповідь зі списком майстрів."
