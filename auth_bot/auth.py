import random
from django.conf import settings
from kavenegar import KavenegarAPI, APIException, HTTPException

from .models import BaleUser
from .utils import send_message_to_bale

def handle_login_command(chat_id):
    """
    وقتی کاربر دستور /login را وارد می‌کند،
    پیام درخواست شماره موبایل را برایش ارسال می‌کنیم.
    """
    user, _ = BaleUser.objects.get_or_create(chat_id=chat_id)
    user.save()
    send_message_to_bale(chat_id, "لطفاً شماره موبایل خود را وارد کنید.")

def handle_phone_number(chat_id, phone_number):
    """
    پس از دریافت شماره موبایل (مثلاً 09xxxxxxxxx)،
    OTP ایجاد و با کاوه‌نگار ارسال می‌کنیم.
    """
    user, _ = BaleUser.objects.get_or_create(chat_id=chat_id)
    user.phone_number = phone_number

    # تولید OTP
    otp = str(random.randint(100000, 999999))
    user.otp = otp
    user.is_authenticated = False
    user.save()

    # ارسال OTP با کاوه‌نگار
    try:
        api = KavenegarAPI(settings.KAVEH_NEGAR_API_KEY)
        params = {
            'receptor': phone_number,
            'token': otp,
            'template': 'users'
        }
        api.verify_lookup(params)
        send_message_to_bale(chat_id, "کد تأیید برای شماره موبایل شما ارسال شد. لطفاً کد را وارد کنید.")
    except (APIException, HTTPException) as e:
        send_message_to_bale(chat_id, "خطایی در ارسال کد OTP رخ داد. لطفاً دوباره تلاش کنید.")
        print(f"Error sending OTP: {e}")


def handle_otp(chat_id, otp):
    """
    بررسی درست بودن کد OTP.
    """
    try:
        user = BaleUser.objects.get(chat_id=chat_id, otp=otp)
        user.is_authenticated = True
        user.otp = ''
        user.save()
        send_message_to_bale(chat_id, "احراز هویت موفق بود! اکنون می‌توانید از خدمات استفاده کنید. 🌟")
    except BaleUser.DoesNotExist:
        send_message_to_bale(chat_id, "کد واردشده نامعتبر است. لطفاً دوباره تلاش کنید.")


def handle_logout_command(chat_id):
    """
    دستور /logout کاربر را از حالت ورود خارج می‌کند.
    """
    user = BaleUser.objects.filter(chat_id=chat_id).first()
    if user:
        user.is_authenticated = False
        user.save()
        send_message_to_bale(chat_id, "شما با موفقیت از سیستم خارج شدید. 🌟")
    else:
        send_message_to_bale(chat_id, "شما هنوز ثبت‌نام نکرده‌اید. لطفاً ابتدا دستور /login را وارد کنید.")
