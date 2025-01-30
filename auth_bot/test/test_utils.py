from unittest.mock import patch
from django.test import TestCase
from auth_bot.utils import send_message_to_bale

class UtilsTests(TestCase):

    @patch("myapp.utils.requests.post")
    def test_send_message_to_bale(self, mock_post):
        chat_id = "12345"
        text = "Hello from test"

        send_message_to_bale(chat_id, text)
        # Check if requests.post was called with the correct URL and payload
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn("json", kwargs)
        self.assertEqual(kwargs["json"], {"chat_id": chat_id, "text": text})
