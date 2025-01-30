from django.test import TestCase
from auth_bot.models import BaleUser, ChatSession

class ModelsTestCase(TestCase):

    def test_bale_user_creation(self):
        user = BaleUser.objects.create(
            chat_id="123",
            phone_number="09123456789",
            is_authenticated=False
        )
        self.assertEqual(str(user), "09123456789 - Auth: False")
        self.assertEqual(user.daily_message_limit, 23)
        self.assertEqual(user.current_message_count, 0)
        self.assertEqual(user.token_limit, 300)

    def test_get_assistant_description(self):
        user = BaleUser.objects.create(
            chat_id="abc",
            phone_number="09120000000",
            assistant_role="cardiologist"
        )
        desc = user.get_assistant_description()
        self.assertIn("متخصص قلب", desc)

    def test_increment_message_count(self):
        user = BaleUser.objects.create(chat_id="xyz", phone_number="09test")
        self.assertTrue(user.increment_message_count())
        user.daily_message_limit = 1
        user.current_message_count = 1
        user.save()
        # Now limit is reached
        self.assertFalse(user.increment_message_count())

    def test_reset_daily_count(self):
        user = BaleUser.objects.create(chat_id="xyz", phone_number="09test")
        user.current_message_count = 5
        user.save()
        user.reset_daily_count()
        user.refresh_from_db()
        self.assertEqual(user.current_message_count, 0)

    def test_chat_session_creation(self):
        user = BaleUser.objects.create(chat_id="abc", phone_number="09120000000")
        session = ChatSession.objects.create(
            user=user,
            is_active=True,
            user_message="Hi doc",
            bot_response="Hello, how can I help?",
            assistant_role="general_physician",
            system_role="therapeutic"
        )
        self.assertIn("Session", str(session))
        self.assertTrue(session.is_active)
        self.assertEqual(session.user_message, "Hi doc")
        self.assertEqual(session.bot_response, "Hello, how can I help?")
        self.assertEqual(session.assistant_role, "general_physician")
        self.assertEqual(session.system_role, "therapeutic")
