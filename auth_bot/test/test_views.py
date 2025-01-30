from django.test import TestCase
from rest_framework.test import APIClient
from auth_bot.models import BaleUser, ChatSession
from django.urls import reverse

class ViewsTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("bale_webhook")  # points to bale_webhook_view

    def test_start_command(self):
        # Simulate /start command
        data = {
            "message": {
                "chat": {"id": "111"},
                "text": "/start"
            }
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_login_command(self):
        data = {
            "message": {
                "chat": {"id": "111"},
                "text": "/login"
            }
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 200)
        # BaleUser should be created
        user = BaleUser.objects.get(chat_id="111")
        self.assertFalse(user.is_authenticated)

    def test_phone_number_input(self):
        BaleUser.objects.create(chat_id="222", is_authenticated=False)
        data = {
            "message": {
                "chat": {"id": "222"},
                "text": "09123456789"
            }
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 200)
        user = BaleUser.objects.get(chat_id="222")
        self.assertEqual(user.phone_number, "09123456789")
        self.assertTrue(len(user.otp) == 6)

    def test_otp_input(self):
        # Prepare user with known OTP
        BaleUser.objects.create(
            chat_id="333",
            phone_number="0912000",
            otp="123456",
            is_authenticated=False
        )
        data = {
            "message": {
                "chat": {"id": "333"},
                "text": "123456"  # correct OTP
            }
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 200)
        user = BaleUser.objects.get(chat_id="333")
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.otp, "")

    def test_logout_command(self):
        BaleUser.objects.create(chat_id="444", is_authenticated=True)
        data = {
            "message": {
                "chat": {"id": "444"},
                "text": "/logout"
            }
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 200)
        user = BaleUser.objects.get(chat_id="444")
        self.assertFalse(user.is_authenticated)

    def test_startchat_without_auth(self):
        BaleUser.objects.create(chat_id="555", is_authenticated=False)
        data = {
            "message": {
                "chat": {"id": "555"},
                "text": "/startchat"
            }
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_startchat_with_auth(self):
        BaleUser.objects.create(chat_id="666", is_authenticated=True)
        data = {
            "message": {
                "chat": {"id": "666"},
                "text": "/startchat"
            }
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_role_selection_invalid(self):
        BaleUser.objects.create(chat_id="777", is_authenticated=True)
        data = {
            "message": {
                "chat": {"id": "777"},
                "text": "999"  # invalid role index
            }
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 200)  # We do respond 200 but send invalid msg

    def test_role_selection_and_confirmation(self):
        user = BaleUser.objects.create(chat_id="888", is_authenticated=True)
        # First select a valid role index (1-based)
        data = {
            "message": {
                "chat": {"id": "888"},
                "text": "1"  # picks the first role from BaleUser.ASSISTANT_ROLES
            }
        }
        resp = self.client.post(self.url, data, format="json")
        self.assertEqual(resp.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.assistant_role)  # set to first in list

        # Then confirm with "1"
        data_confirm = {
            "message": {
                "chat": {"id": "888"},
                "text": "1"
            }
        }
        resp2 = self.client.post(self.url, data_confirm, format="json")
        self.assertEqual(resp2.status_code, 200)

    def test_chat_message_flow(self):
        user = BaleUser.objects.create(
            chat_id="999",
            phone_number="0912xxx",
            is_authenticated=True,
            assistant_role="psychologist"
        )
        # Normal user message
        data = {
            "message": {
                "chat": {"id": "999"},
                "text": "Hello doctor."
            }
        }
        with self.assertNumQueries(6):  # or so, depends on your DB hits
            response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 200)
        # Check if ChatSession is created/updated
        session = ChatSession.objects.filter(user=user, is_active=True).first()
        self.assertIsNotNone(session)
        self.assertIn("Hello doctor.", session.user_message)

    def test_end_chat(self):
        user = BaleUser.objects.create(
            chat_id="1010",
            phone_number="09xxx",
            is_authenticated=True
        )
        ChatSession.objects.create(user=user, is_active=True)
        data = {
            "message": {
                "chat": {"id": "1010"},
                "text": "#"
            }
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 200)
        session = ChatSession.objects.filter(user=user).first()
        self.assertFalse(session.is_active)

    def test_no_message_key(self):
        # If the incoming data does not contain "message", we handle gracefully
        data = {}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 200)
