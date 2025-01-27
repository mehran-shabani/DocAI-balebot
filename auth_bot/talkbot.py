import requests
import json
from django.conf import settings

def talk_to_bot(messages):
    """
    تعامل با سرویس TalkBot.ir برای دریافت پاسخ از مدل هوش مصنوعی.
    پارامتر messages باید آرایه‌ای از دیالوگ‌ها باشد، مانند:
    [
      {"role": "system", "content": "..."},
      {"role": "user", "content": "..."}
    ]
    """
    url = 'https://api.talkbot.ir/v1/chat/completions'
    payload = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "max-token": 400,
        "temperature": 0.3,
        "stream": False,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {settings.TALKBOT_API_KEY}'  # یا توکن TalkBot
    }

    response = requests.post(url, data=json.dumps(payload), headers=headers)

    if response.ok:
        return response.json()
    else:
        return {"error": f"{response.status_code} - {response.text}"}