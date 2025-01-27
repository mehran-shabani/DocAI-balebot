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
    وبهوک اصلی ربات بله برای مدیریت تمام پیام‌های دریافتی.
    """
    update_json = request.data

    if "message" in update_json:
        message = update_json["message"]
        chat_id = str(message["chat"]["id"])
        text = message.get("text", "").strip()

        # 1) دستور /start برای خوشامدگویی
        if text.lower() == "/start":
            return handle_start(chat_id)

        # 2) دستور لاگین
        elif text.lower() == "/login":
            auth.handle_login_command(chat_id)
            return Response(status=200)

        # 3) کاربر شماره موبایل را وارد کرده (11 رقمی و شروع با 09)
        elif text.isdigit() and len(text) == 11 and text.startswith("09"):
            auth.handle_phone_number(chat_id, text)
            return Response(status=200)

        # 4) کد OTP (6 رقمی)
        elif text.isdigit() and len(text) == 6:
            auth.handle_otp(chat_id, text)
            return Response(status=200)

        # 5) دستور /logout
        elif text.lower() == "/logout":
            auth.handle_logout_command(chat_id)
            return Response(status=200)

        # 6) دستور شروع چت
        elif text.lower() == "/startchat":
            return start_chat(chat_id)

        # 7) علامت # برای پایان چت
        elif text == "#":
            return end_chat(chat_id)

        # 8) بررسی اینکه آیا ورودی عددی برای انتخاب نقش/تأیید یا رد آن است
        elif text.isdigit():
            return handle_role_selection_or_confirmation(chat_id, text)

        # 9) در نهایت اگر به موارد بالا نخوریم، یعنی پیام عادی کاربر است
        else:
            return handle_chat_message(chat_id, text)

    # اگر ساختار پیام دریافتی غیرمنتظره بود
    return Response(status=200)


def handle_start(chat_id):
    """
    دستور /start برای خوشامدگویی و ارائه‌ی توضیحات اولیه.
    """
    welcome_message = (
        "به ربات خوش آمدید! \n\n"
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
    شروع چت تنها در صورتی ممکن است که کاربر احراز هویت شده باشد.
    سپس لیست نقش‌ها را برای انتخاب ارسال می‌کنیم.
    """
    user = BaleUser.objects.filter(chat_id=chat_id).first()
    if not user:
        send_message_to_bale(chat_id, "شما هنوز ثبت‌نام نکرده‌اید. لطفاً ابتدا دستور /login را وارد کنید.")
        return Response(status=400)

    if not user.is_authenticated:
        send_message_to_bale(chat_id, "ابتدا باید وارد شوید. لطفاً دستور /login را وارد کنید.")
        return Response(status=400)

    roles = BaleUser.ASSISTANT_ROLES  # [('doctor', 'پزشک'), ('psychologist', 'روانشناس'), ...]
    role_list = "\n".join([f"{i+1}. {role[1]}" for i, role in enumerate(roles)])
    message = (
        "لطفاً یکی از نقش‌های زیر را انتخاب کنید:\n"
        f"{role_list}\n\n"
        "شماره مورد نظر را وارد کنید."
    )
    send_message_to_bale(chat_id, message)
    return Response(status=200)


def handle_role_selection_or_confirmation(chat_id, text):
    """
    اگر عدد 1 یا 0 باشد، یعنی کاربر در حال تأیید یا رد نقش انتخاب‌شده است.
    اگر عدد دیگری است، یعنی کاربر در حال انتخاب نقش است.
    """
    user = BaleUser.objects.filter(chat_id=chat_id).first()
    if not user:
        send_message_to_bale(chat_id, "شما هنوز ثبت‌نام نکرده‌اید. لطفاً دستور /login را وارد کنید.")
        return Response(status=400)

    if not user.is_authenticated:
        send_message_to_bale(chat_id, "ابتدا باید وارد شوید. لطفاً دستور /login را وارد کنید.")
        return Response(status=400)

    if text == "1":
        # تأیید نقش
        if user.assistant_role:
            send_message_to_bale(
                chat_id,
                f"نقش «{user.get_assistant_role_display()}» تأیید شد.\n"
                "اکنون می‌توانید چت را آغاز کنید.\n"
                "پیام خود را ارسال کنید و برای پایان چت علامت # را ارسال نمایید."
            )
        else:
            send_message_to_bale(chat_id, "ابتدا باید نقش را انتخاب کنید. دستور /startchat را بزنید.")
        return Response(status=200)

    elif text == "0":
        # رد نقش و انتخاب مجدد
        return start_chat(chat_id)

    # انتخاب نقش با عدد
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
        send_message_to_bale(chat_id, "شماره واردشده نامعتبر است. لطفاً شماره‌ای از لیست ارسال کنید.")

    return Response(status=200)


def handle_chat_message(chat_id, text):
    """
    رسیدگی به پیام عادی کاربر.  
    تنها زمانی اجازه ارسال پیام به بات را داریم که کاربر احراز هویت شده باشد و یک نقش انتخاب و تأیید کرده باشد.
    """
    user = BaleUser.objects.filter(chat_id=chat_id).first()
    if not user:
        send_message_to_bale(chat_id, "شما هنوز ثبت‌نام نکرده‌اید. لطفاً ابتدا دستور /login را وارد کنید.")
        return Response(status=400)

    if not user.is_authenticated:
        send_message_to_bale(chat_id, "ابتدا باید وارد شوید. لطفاً دستور /login را وارد کنید.")
        return Response(status=400)

    if not user.assistant_role:
        send_message_to_bale(chat_id, "شما هنوز نقشی انتخاب نکرده‌اید. دستور /startchat را ارسال کنید.")
        return Response(status=400)

    # اگر همه چیز درست بود، حالا پیام را به بات ارسال می‌کنیم
    # ابتدا سشن فعال را چک کرده یا می‌سازیم
    session, _ = ChatSession.objects.get_or_create(user=user, is_active=True)

    # بررسی محدودیت روزانه
    if user.current_message_count >= user.daily_message_limit:
        send_message_to_bale(chat_id, "شما به حد پیام روزانه خود رسیده‌اید. لطفاً فردا دوباره تلاش کنید.")
        return Response(status=400)

    # ساختار پیام ارسالی به هوش مصنوعی
    messages = [
        {"role": "system", "content": user.get_assistant_description()},
        {"role": "user", "content": text}
    ]

    # فراخوانی تابع هوش مصنوعی (مثلاً GPT)
    bot_response = talk_to_bot(messages)
    answer = bot_response.get("choices", [{}])[0].get("message", {}).get("content", "پاسخی دریافت نشد.")

    # ذخیره پیام کاربر و پاسخ در چت
    session.user_message = text
    session.bot_response = answer
    session.save()

    # افزایش شمارنده پیام کاربر
    user.increment_message_count()
    user.save()

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
    پایان چت فعال با ارسال علامت #.
    """
    user = BaleUser.objects.filter(chat_id=chat_id).first()
    if not user:
        send_message_to_bale(chat_id, "شما هنوز ثبت‌نام نکرده‌اید. لطفاً ابتدا دستور /login را وارد کنید.")
        return Response(status=400)

    session = ChatSession.objects.filter(user=user, is_active=True).first()
    if session:
        session.is_active = False
        session.save()
        send_message_to_bale(chat_id, "چت شما پایان یافت. برای شروع چت جدید دستور /startchat را ارسال کنید.")
    else:
        send_message_to_bale(chat_id, "شما در حال حاضر چت فعالی ندارید.")
    return Response(status=200)
