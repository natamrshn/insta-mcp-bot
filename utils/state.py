import json

def load_answered(filename):
    try:
        with open(filename, "r") as f:
            answered = set(json.load(f))
        print(f"✅ Загружено {len(answered)} обработанных сообщений")
        return answered
    except Exception:
        print("ℹ️ Нет файла с историей, начинаем с нуля")
        return set()

def save_answered(filename, answered_messages):
    with open(filename, "w") as f:
        json.dump(list(answered_messages), f)
