import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": text}

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            print(f"Ошибка Telegram: {response.status_code} | {response.text}")
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")
