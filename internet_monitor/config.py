import json
import logging
import os
import sys
from telegram import Bot
from telegram.error import TelegramError

logger = logging.getLogger(__name__)

CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        logger.warning("Configuration file not found. Using empty config.")
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Error reading config.json: {e}")
        return {}

def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        logger.info("Configuration saved successfully.")
    except OSError as e:
        logger.error(f"Error writing config.json: {e}")


async def prompt_and_validate_bot_details():
    """
    Continuously prompt for bot token and chat ID until valid or until user quits.
    If the user enters 'q' for either prompt, we exit the script.
    Returns the (bot_token, chat_id) once validated.
    """
    while True:
        print("\n--- Telegram Bot Credentials Setup/Validation ---")
        print("Type 'q' at any prompt to quit.")

        bot_token = input("Please enter your Telegram Bot Token: ").strip()
        if bot_token.lower() == "q":
            print("Exiting script...")
            sys.exit(0)

        chat_id = input("Please enter your Telegram Chat ID: ").strip()
        if chat_id.lower() == "q":
            print("Exiting script...")
            sys.exit(0)

        # Validate credentials by calling Telegram Bot API
        try:
            bot = Bot(token=bot_token)
            me = await bot.get_me()  # async check for valid token
            await bot.send_message(
                chat_id=chat_id,
                text="Test message: Bot credentials look good!"
            )
            print(f"Credentials validated! Bot username: @{me.username}")
            return bot_token, chat_id

        except TelegramError as e:
            print(f"Invalid credentials or error occurred: {e}")
            print("Please try again or type 'q' to quit.\n")
