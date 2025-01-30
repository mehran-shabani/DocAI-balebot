import requests
import json
from django.conf import settings

def talk_to_bot(
    user_messages,
    assistant_messages=None,
    system_role_description=None,
    model="gpt-4o-mini",
    max_tokens=400,
    temperature=0.3,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0
):
    """
    Interact with the TalkBot.ir service in an extended way:
    1) We pass in a short "memory" (history) of user_messages and assistant_messages.
    2) We optionally include a system prompt with role="system".
    3) Model parameters (temperature, top_p, etc.) are configurable.

    :param user_messages: List[Dict], e.g. [{"role": "user", "content": "..."}]
    :param assistant_messages: List[Dict], e.g. [{"role": "assistant", "content": "..."}]
    :param system_role_description: (str) The system message content, typically combining
                                    assistant role, system role, and instructions for the model.
    :param model: (str) Model name, e.g. "gpt-4o-mini"
    :param max_tokens: (int) Maximum tokens in the response
    :param temperature: (float) "Creativity" factor (0.0 - 1.0+)
    :param top_p: (float) Probability threshold for sampling
    :param frequency_penalty: (float) Repetition penalty
    :param presence_penalty: (float) Presence penalty
    :return: Dictionary containing the TalkBot response or an error key.
    """
    messages = []

    # 1) Optional system message
    if system_role_description:
        messages.append({
            "role": "system",
            "content": system_role_description
        })

    # 2) Merge user and assistant messages from prior turns
    if user_messages and assistant_messages:
        # If we store them in pairs, we can zip them
        # so the conversation flows: user -> assistant -> user -> assistant, ...
        for u_msg, a_msg in zip(user_messages, assistant_messages):
            messages.append(u_msg)  # {"role": "user", "content": ...}
            messages.append(a_msg)  # {"role": "assistant", "content": ...}

        # If there's one extra user message (unanswered) at the end
        if len(user_messages) > len(assistant_messages):
            messages.append(user_messages[-1])

    else:
        # If we only have user_messages
        if user_messages:
            for um in user_messages:
                messages.append(um)

    # Prepare payload for TalkBot
    payload = {
        "model": model,
        "messages": messages,
        "max-token": max_tokens,
        "temperature": temperature,
        "stream": False,  # Typically false unless streaming is supported
        "top_p": top_p,
        "frequency_penalty": frequency_penalty,
        "presence_penalty": presence_penalty
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {settings.TALKBOT_API_KEY}'
    }

    url = 'https://api.talkbot.ir/v1/chat/completions'
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
    except requests.exceptions.RequestException as e:
        return {"error": f"Request error: {e}"}

    if response.ok:
        return response.json()
    else:
        return {"error": f"{response.status_code} - {response.text}"}
