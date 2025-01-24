import logging
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError

logger = logging.getLogger(__name__)


class TelegramAlerts:
    """
    A simple class to encapsulate sending alerts using python-telegram-bot.
    You only need the bot_token and the chat_id.
    """

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id

    async def send_alert(self, message: str):
        """
        Sends an alert message to the specified chat_id using bot_token.
        Uses python-telegram-bot in asynchronous style.
        """
        try:
            bot = Bot(token=self.bot_token)
            # python-telegram-bot v20+ has async methods, so we can await send_message
            await bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
        except TelegramError as e:
            logger.error(f"Failed to send alert: {e}")
