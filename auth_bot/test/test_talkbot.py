import json
from unittest.mock import patch, MagicMock
from django.test import TestCase
from auth_bot.talkbot import talk_to_bot

class TalkbotTests(TestCase):

    @patch("myapp.talkbot.requests.post")
    def test_talk_to_bot_success(self, mock_post):
        # Mock a successful response
        mock_post.return_value.ok = True
        mock_post.return_value.json.return_value = {
            "choices": [
                {
                    "message": {"role": "assistant", "content": "Test response"}
                }
            ]
        }

        response = talk_to_bot(
            user_messages=[{"role": "user", "content": "Hello"}],
            assistant_messages=None,
            system_role_description="System prompt here",
            model="gpt-4o-mini",
            max_tokens=400,
            temperature=0.3
        )

        self.assertIn("choices", response)
        self.assertEqual(response["choices"][0]["message"]["content"], "Test response")
        self.assertTrue(mock_post.called)

    @patch("myapp.talkbot.requests.post")
    def test_talk_to_bot_error(self, mock_post):
        # Mock an error response
        mock_post.return_value.ok = False
        mock_post.return_value.status_code = 400
        mock_post.return_value.text = "Bad request"

        response = talk_to_bot(
            user_messages=[{"role": "user", "content": "Hello"}]
        )
        self.assertIn("error", response)
        self.assertIn("400", response["error"])
        self.assertTrue(mock_post.called)

    @patch("myapp.talkbot.requests.post")
    def test_talk_to_bot_request_exception(self, mock_post):
        # Mock an exception in requests
        mock_post.side_effect = Exception("Connection error")

        response = talk_to_bot(
            user_messages=[{"role": "user", "content": "Hello"}]
        )
        self.assertIn("error", response)
        self.assertIn("Connection error", response["error"])
