import random
from unittest.mock import patch, MagicMock
from django.test import TestCase
from auth_bot.auth import (
    handle_login_command,
    handle_phone_number,
    handle_otp,
    handle_logout_command,
)
from auth_bot.models import BaleUser

class AuthTests(TestCase):

    def setUp(self):
        self.chat_id = "12345"

    @patch("myapp.auth.send_message_to_bale")
    def test_handle_login_command(self, mock_send):
        """
        Test that handle_login_command creates BaleUser if not exists
        and prompts for phone.
        """
        # Ensure no user first
        self.assertFalse(BaleUser.objects.filter(chat_id=self.chat_id).exists())
        handle_login_command(self.chat_id)

        # Check user created
        user = BaleUser.objects.get(chat_id=self.chat_id)
        self.assertIsNotNone(user)
        mock_send.assert_called_with(self.chat_id, "لطفاً شماره موبایل خود را وارد کنید.")

    @patch("myapp.auth.send_message_to_bale")
    @patch("myapp.auth.KavenegarAPI")
    def test_handle_phone_number(self, mock_kaveh, mock_send):
        """
        Test handle_phone_number sets phone_number, generates OTP, and sends it.
        """
        user = BaleUser.objects.create(chat_id=self.chat_id)
        handle_phone_number(self.chat_id, "09123456789")

        user.refresh_from_db()
        self.assertEqual(user.phone_number, "09123456789")
        self.assertTrue(len(user.otp) == 6)  # It's random, but 6 digits
        mock_kaveh.assert_called_once()  # KavenegarAPI was used
        mock_send.assert_called_with(
            self.chat_id,
            "کد تأیید برای شماره موبایل شما ارسال شد. لطفاً کد را وارد کنید."
        )

    @patch("myapp.auth.send_message_to_bale")
    def test_handle_otp_success(self, mock_send):
        """
        Test a successful OTP match.
        """
        user = BaleUser.objects.create(
            chat_id=self.chat_id,
            phone_number="09123456789",
            otp="123456",
            is_authenticated=False
        )
        handle_otp(self.chat_id, "123456")
        user.refresh_from_db()
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.otp, "")
        mock_send.assert_called_with(
            self.chat_id,
            "احراز هویت موفق بود! اکنون می‌توانید از خدمات استفاده کنید. 🌟"
        )

    @patch("myapp.auth.send_message_to_bale")
    def test_handle_otp_failure(self, mock_send):
        """
        Test an invalid OTP.
        """
        BaleUser.objects.create(
            chat_id=self.chat_id,
            phone_number="09123456789",
            otp="999999",
            is_authenticated=False
        )
        handle_otp(self.chat_id, "123456")  # Wrong OTP
        mock_send.assert_called_with(
            self.chat_id,
            "کد واردشده نامعتبر است. لطفاً دوباره تلاش کنید."
        )

    @patch("myapp.auth.send_message_to_bale")
    def test_handle_logout_command(self, mock_send):
        """
        Test handle_logout_command sets is_authenticated=False.
        """
        user = BaleUser.objects.create(
            chat_id=self.chat_id,
            phone_number="09123456789",
            otp="",
            is_authenticated=True
        )
        handle_logout_command(self.chat_id)
        user.refresh_from_db()
        self.assertFalse(user.is_authenticated)
        mock_send.assert_called_with(
            self.chat_id,
            "شما با موفقیت از سیستم خارج شدید. 🌟"
        )

    @patch("myapp.auth.send_message_to_bale")
    def test_handle_logout_command_no_user(self, mock_send):
        """
        Test handle_logout_command if user not found.
        """
        handle_logout_command(self.chat_id)
        mock_send.assert_called_with(
            self.chat_id,
            "شما هنوز ثبت‌نام نکرده‌اید. لطفاً ابتدا دستور /login را وارد کنید."
        )
