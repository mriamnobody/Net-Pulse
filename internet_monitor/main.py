import asyncio
import logging
import sys

from internet_monitor.config import (
    load_config,
    save_config,
    prompt_and_validate_bot_details
)
from internet_monitor.db_manager import DatabaseManager, init_db
from internet_monitor.daily_stats import DailyStats
from internet_monitor.monitor import monitor_internet
from internet_monitor.stats_reporter import periodic_stats_report
from internet_monitor.alerts import TelegramAlerts


def setup_logger():
    """
    Configure root logger to log to both console and file.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter("%(asctime)s - [%(levelname)s] %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler("internet_monitor.log", encoding="utf-8")
    file_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s - [Line: %(lineno)d]")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)


async def main():
    setup_logger()
    logging.info("Internet Monitor script started.")

    config = load_config()

    # Check if config has BOT_TOKEN & CHAT_ID. Otherwise, prompt for them.
    if not config.get("BOT_TOKEN") or not config.get("CHAT_ID"):
        bot_token, chat_id = await prompt_and_validate_bot_details()   # <--- Notice the "await"!
        config["BOT_TOKEN"] = bot_token
        config["CHAT_ID"] = chat_id
        save_config(config)
    else:
        # If we already have them, verify they actually work:
        bot_token = config["BOT_TOKEN"]
        chat_id = config["CHAT_ID"]
        print("Validating existing Telegram Bot Token and Chat ID from config...")
        from telegram import Bot
        from telegram.error import TelegramError
        try:
            bot = Bot(token=bot_token)
            me = await bot.get_me()  # Check if token is valid
            await bot.send_message(
                chat_id=chat_id,
                text="Test message: Bot credentials look good!"
            )
            print(f"Credentials validated! Bot username: @{me.username}")
        except TelegramError as e:
            logging.error(f"Stored credentials invalid or error occurred: {e}")
            # Prompt again if invalid
            bot_token, chat_id = await prompt_and_validate_bot_details()
            config["BOT_TOKEN"] = bot_token
            config["CHAT_ID"] = chat_id
            save_config(config)

    # Now we definitely have a valid BOT_TOKEN and CHAT_ID
    bot_token = config["BOT_TOKEN"]
    chat_id = config["CHAT_ID"]

    # Initialize DB
    db_manager = DatabaseManager()
    init_db(db_manager)

    # Create a DailyStats object
    daily_stats = DailyStats()
    daily_stats.db_manager = db_manager  # if you need it inside daily_stats

    # Create alerts instance
    alerts = TelegramAlerts(bot_token, chat_id)

    # Create tasks
    monitor_task = asyncio.create_task(monitor_internet(alerts, daily_stats))
    stats_task = asyncio.create_task(periodic_stats_report(alerts, daily_stats, db_manager))

    # Wait for them (run forever unless interrupted)
    await asyncio.gather(monitor_task, stats_task)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Script interrupted by user.")
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
