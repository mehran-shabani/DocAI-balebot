import random
from django.conf import settings
from kavenegar import KavenegarAPI, APIException, HTTPException

from .models import BaleUser
from .utils import send_message_to_bale

def handle_login_command(chat_id):
    """
    When the user sends the /login command, prompt them for their phone number.
    """
    user, _ = BaleUser.objects.get_or_create(chat_id=chat_id)
    # Ensure the user is saved in the DB, even if newly created
    user.save()
    send_message_to_bale(chat_id, "لطفاً شماره موبایل خود را وارد کنید.")

def handle_phone_number(chat_id, phone_number):
    """
    Upon receiving a phone number (e.g., '09xxxxxxxxx'),
    generate an OTP and send it to the user via Kavenegar.
    """
    user, _ = BaleUser.objects.get_or_create(chat_id=chat_id)
    user.phone_number = phone_number

    # Generate OTP
    otp = str(random.randint(100000, 999999))
    user.otp = otp
    user.is_authenticated = False
    user.save()

    # Send OTP via Kavenegar
    try:
        api = KavenegarAPI(settings.KAVEH_NEGAR_API_KEY)
        params = {
            'receptor': phone_number,
            'token': otp,
            'template': 'users'
        }
        api.verify_lookup(params)
        send_message_to_bale(
            chat_id,
            "کد تأیید برای شماره موبایل شما ارسال شد. لطفاً کد را وارد کنید."
        )
    except (APIException, HTTPException) as e:
        send_message_to_bale(
            chat_id,
            "خطایی در ارسال کد OTP رخ داد. لطفاً دوباره تلاش کنید."
        )
        print(f"Error sending OTP: {e}")

def handle_otp(chat_id, otp):
    """
    Verify the given OTP matches the user's stored code.
    """
    try:
        user = BaleUser.objects.get(chat_id=chat_id, otp=otp)
        user.is_authenticated = True
        user.otp = ''
        user.save()
        send_message_to_bale(
            chat_id,
            "احراز هویت موفق بود! اکنون می‌توانید از خدمات استفاده کنید. 🌟"
        )
    except BaleUser.DoesNotExist:
        send_message_to_bale(
            chat_id,
            "کد واردشده نامعتبر است. لطفاً دوباره تلاش کنید."
        )

def handle_logout_command(chat_id):
    """
    When the user sends /logout, mark them as logged out.
    """
    user = BaleUser.objects.filter(chat_id=chat_id).first()
    if user:
        user.is_authenticated = False
        user.save()
        send_message_to_bale(
            chat_id,
            "شما با موفقیت از سیستم خارج شدید. 🌟"
        )
    else:
        send_message_to_bale(
            chat_id,
            "شما هنوز ثبت‌نام نکرده‌اید. لطفاً ابتدا دستور /login را وارد کنید."
        )
