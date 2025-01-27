import requests
from django.conf import settings

def send_message_to_bale(chat_id, text):
    """
    تابع کمکی برای ارسال پیام به کاربر در پیام‌رسان بله.
    """
    bot_token = settings.BALE_BOT_TOKEN
    url = f"https://tapi.bale.ai/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)
