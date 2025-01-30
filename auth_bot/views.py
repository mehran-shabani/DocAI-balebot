import requests
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import BaleUser, ChatSession
from .talkbot import talk_to_bot
from . import auth
from .utils import send_message_to_bale

@api_view(['POST'])
@permission_classes([AllowAny])
def bale_webhook_view(request):
    """
    Main Bale bot webhook to handle all incoming messages.
    """
    update_json = request.data

    if "message" in update_json:
        message = update_json["message"]
        chat_id = str(message["chat"]["id"])
        text = message.get("text", "").strip()

        # 1) /start command
        if text.lower() == "/start":
            return handle_start(chat_id)

        # 2) /login command
        elif text.lower() == "/login":
            auth.handle_login_command(chat_id)
            return Response(status=200)

        # 3) If the user enters something like 09xxxxxxxxx (phone number)
        elif text.isdigit() and len(text) == 11 and text.startswith("09"):
            auth.handle_phone_number(chat_id, text)
            return Response(status=200)

        # 4) If the user enters a 6-digit OTP code
        elif text.isdigit() and len(text) == 6:
            auth.handle_otp(chat_id, text)
            return Response(status=200)

        # 5) /logout command
        elif text.lower() == "/logout":
            auth.handle_logout_command(chat_id)
            return Response(status=200)

        # 6) /startchat command
        elif text.lower() == "/startchat":
            return start_chat(chat_id)

        # 7) '#' symbol to end chat
        elif text == "#":
            return end_chat(chat_id)

        # 8) Check if input is a digit for role selection/confirmation
        elif text.isdigit():
            return handle_role_selection_or_confirmation(chat_id, text)

        # 9) Otherwise, treat this as a normal user message
        else:
            return handle_chat_message(chat_id, text)

    # If the incoming structure isn't what we expect, just respond 200
    return Response(status=200)


def handle_start(chat_id):
    """
    /start command to greet the user and show basic info.
    """
    welcome_message = (
        "به ربات خوش آمدید!\n\n"
        "برای ورود دستور /login را وارد کنید.\n"
        "اگر قبلاً وارد شده‌اید، می‌توانید دستور /startchat را برای شروع مکالمه وارد کنید.\n\n"
        "راهنما:\n"
        "/login - شروع فرآیند لاگین\n"
        "/logout - خروج از سیستم\n"
        "/startchat - شروع یک چت جدید (در صورتی که لاگین کرده باشید)\n"
        "# - پایان چت فعلی"
    )
    send_message_to_bale(chat_id, welcome_message)
    return Response(status=200)

def start_chat(chat_id):
    """
    Start chat if user is authenticated. Sends the list of roles for selection.
    """
    user = BaleUser.objects.filter(chat_id=chat_id).first()
    if not user:
        send_message_to_bale(
            chat_id,
            "شما هنوز ثبت‌نام نکرده‌اید. لطفاً ابتدا دستور /login را وارد کنید."
        )
        return Response(status=400)

    if not user.is_authenticated:
        send_message_to_bale(
            chat_id,
            "ابتدا باید وارد شوید. لطفاً دستور /login را وارد کنید."
        )
        return Response(status=400)

    roles = BaleUser.ASSISTANT_ROLES  # e.g., [('general_physician', 'پزشک عمومی'), ...]
    role_list = "\n".join([f"{i+1}. {r[1]}" for i, r in enumerate(roles)])
    message = (
        "لطفاً یکی از نقش‌های زیر را انتخاب کنید:\n"
        f"{role_list}\n\n"
        "شماره مورد نظر را وارد کنید."
    )
    send_message_to_bale(chat_id, message)
    return Response(status=200)

def handle_role_selection_or_confirmation(chat_id, text):
    """
    If the number is 1 or 0, user might be confirming or rejecting the role.
    If another number, user might be selecting a role from the list.
    """
    user = BaleUser.objects.filter(chat_id=chat_id).first()
    if not user:
        send_message_to_bale(
            chat_id,
            "شما هنوز ثبت‌نام نکرده‌اید. لطفاً ابتدا دستور /login را وارد کنید."
        )
        return Response(status=400)

    if not user.is_authenticated:
        send_message_to_bale(
            chat_id,
            "ابتدا باید وارد شوید. لطفاً دستور /login را وارد کنید."
        )
        return Response(status=400)

    if text == "1":
        # Confirm role
        if user.assistant_role:
            send_message_to_bale(
                chat_id,
                f"نقش «{user.get_assistant_role_display()}» تأیید شد.\n"
                "اکنون می‌توانید چت را آغاز کنید.\n"
                "پیام خود را ارسال کنید و برای پایان چت علامت # را ارسال نمایید."
            )
        else:
            send_message_to_bale(
                chat_id,
                "ابتدا باید نقش را انتخاب کنید. دستور /startchat را بزنید."
            )
        return Response(status=200)

    elif text == "0":
        # Reject role and re-select
        return start_chat(chat_id)

    # Otherwise, user is selecting a role from the list
    roles = BaleUser.ASSISTANT_ROLES
    try:
        role_index = int(text) - 1
        if 0 <= role_index < len(roles):
            role_value, role_label = roles[role_index]
            user.assistant_role = role_value
            user.save()
            send_message_to_bale(
                chat_id,
                f"نقش انتخاب‌شده: {role_label}\n"
                "برای تأیید عدد 1 را ارسال کنید یا برای انتخاب مجدد عدد 0."
            )
        else:
            raise ValueError
    except ValueError:
        send_message_to_bale(
            chat_id,
            "شماره واردشده نامعتبر است. لطفاً شماره‌ای از لیست ارسال کنید."
        )

    return Response(status=200)

def handle_chat_message(chat_id, text):
    """
    Handle a normal user message.
    Only allowed if the user is authenticated and has selected/confirmed a role.
    """
    user = BaleUser.objects.filter(chat_id=chat_id).first()
    if not user:
        send_message_to_bale(
            chat_id,
            "شما هنوز ثبت‌نام نکرده‌اید. لطفاً ابتدا دستور /login را وارد کنید."
        )
        return Response(status=400)

    if not user.is_authenticated:
        send_message_to_bale(
            chat_id,
            "ابتدا باید وارد شوید. لطفاً دستور /login را وارد کنید."
        )
        return Response(status=400)

    if not user.assistant_role:
        send_message_to_bale(
            chat_id,
            "شما هنوز نقشی انتخاب نکرده‌اید. دستور /startchat را ارسال کنید."
        )
        return Response(status=400)

    # Check daily limit
    if user.current_message_count >= user.daily_message_limit:
        send_message_to_bale(
            chat_id,
            "شما به حد پیام روزانه خود رسیده‌اید. لطفاً فردا دوباره تلاش کنید."
        )
        return Response(status=400)

    # Gather recent conversation history to provide memory
    # Let's say we want the last 5 sessions for short-term memory.
    # You can customize as needed:
    recent_sessions = ChatSession.objects.filter(user=user).order_by('-created_at')[:5]
    # We reverse them (oldest -> newest) for correct order
    recent_sessions = reversed(recent_sessions)

    user_messages = []
    assistant_messages = []

    for s in recent_sessions:
        # Each session has user_message, bot_response
        user_messages.append({
            "role": "user",
            "content": s.user_message
        })
        assistant_messages.append({
            "role": "assistant",
            "content": s.bot_response
        })

    # We'll provide a system prompt that includes the user's assistant role description
    system_prompt = (
        f"{user.get_assistant_description()}\n"
        "شما یک دستیار هوشمند هستید؛ لطفاً ابتدا گام‌به‌گام فکر کنید ولی در نهایت خلاصه و مفید پاسخ دهید."
    )

    # Now call talk_to_bot with the new user message appended (if needed).
    # We'll pass the history + new user message as the last item in user_messages.
    # We'll do that by just appending the new text to user_messages:
    user_messages.append({"role": "user", "content": text})

    bot_response_data = talk_to_bot(
        user_messages=user_messages,
        assistant_messages=assistant_messages,
        system_role_description=system_prompt,
        model="gpt-4o-mini",
        max_tokens=user.token_limit,
        temperature=0.3
    )

    # Extract final answer
    if "error" in bot_response_data:
        answer = f"خطایی رخ داد: {bot_response_data['error']}"
    else:
        answer = (
            bot_response_data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "پاسخی دریافت نشد.")
        )

    # Create/Update the active chat session
    session, _ = ChatSession.objects.get_or_create(user=user, is_active=True)
    session.user_message = text
    session.bot_response = answer
    # Use the roles from BaleUser
    session.assistant_role = user.assistant_role
    session.system_role = user.system_role
    session.save()

    # Increment message count
    user.increment_message_count()

    # Send response to Bale
    remaining = user.daily_message_limit - user.current_message_count
    final_text = (
        f"{answer}\n\n"
        f"پیام‌های باقی‌مانده امروز شما: {remaining}\n"
        "برای پایان چت علامت # را ارسال کنید."
    )
    send_message_to_bale(chat_id, final_text)
    return Response(status=200)

def end_chat(chat_id):
    """
    End the active chat session when user sends '#'.
    """
    user = BaleUser.objects.filter(chat_id=chat_id).first()
    if not user:
        send_message_to_bale(
            chat_id,
            "شما هنوز ثبت‌نام نکرده‌اید. لطفاً ابتدا دستور /login را وارد کنید."
        )
        return Response(status=400)

    session = ChatSession.objects.filter(user=user, is_active=True).first()
    if session:
        session.is_active = False
        session.save()
        send_message_to_bale(
            chat_id,
            "چت شما پایان یافت. برای شروع چت جدید دستور /startchat را ارسال کنید."
        )
    else:
        send_message_to_bale(chat_id, "شما در حال حاضر چت فعالی ندارید.")
    return Response(status=200)
