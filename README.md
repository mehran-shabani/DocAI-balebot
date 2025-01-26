# DocAI-balebot

We embed **DocAI** in a bot on the **Bale platform**! 🎉  
It's completely **free** to use! 🚀

---

## Features
- **AI-powered messaging**: DocAI can provide intelligent responses and interact with users efficiently.
- **Easy integration**: Runs seamlessly on the Bale platform.
- **Free usage**: No cost to use the bot in Bale Messenger.

---

## How It Works
1. **Start the Bot**: Add the bot to your Bale Messenger.
2. **Send a Message**: The bot understands your queries and provides helpful responses.
3. **Enjoy the Experience**: Powered by DocAI for smarter interactions.

---

## Technologies Used
- **Django**: Backend framework for API and bot management.
- **Bale API**: For integrating the bot into the Bale Messenger platform.
- **DocAI**: AI engine for intelligent responses.

---

## Installation Guide
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/DocAI-balebot.git
   cd DocAI-balebot
2. Install dependencies:
   ```bash
   pip install -r requirements.txt


3. Set up your environment variables:
	•	Create a .env file in the root directory.
	•	Add the following variables:

BALE_BOT_TOKEN=your_bale_bot_token
TALKBOT_API_KEY=your_docai_api_key
KAVEH_NEGAR_API_KEY=your_kaveh_negar_api_key

4.	Run the server:
   ```bash
   python manage.py runserver


5.	Set the webhook for your bot:
   ```bash
   curl "https://tapi.bale.ai/bot<BALE_BOT_TOKEN>/setWebhook?url=https://yourdomain.com/auth/bale-webhook/"

## Endpoints
	•	Webhook: /auth/bale-webhook/
Handles all messages and interactions with the bot.

## How to Contribute
	1.	Fork the repository.
	2.	Create a new branch for your feature:
   ```bash
   git checkout -b feature-name


	3.	Commit your changes and push them to your fork:
   ```bash
   git push origin feature-name


	4.	Create a pull request to the main branch.

## License

This project is licensed under the MIT License. Feel free to use, modify, and share it as you like!

## Support

For questions or support, feel free to open an issue or contact us via Bale Messenger.

Enjoy using DocAI on Bale! It’s free and smart! 😜

