import asyncio
import logging
import sys

from internet_monitor.config import load_config, save_config
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

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter("%(asctime)s - [%(levelname)s] %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler("internet_monitor.log", encoding="utf-8")
    file_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s - [Line: %(lineno)d]")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)


async def main():
    setup_logger()
    logging.info("Internet Monitor script started.")

    # Load or create config
    config = load_config()

    # Ask user for BOT_TOKEN if not present
    if "BOT_TOKEN" not in config or not config["BOT_TOKEN"]:
        config["BOT_TOKEN"] = input("Please enter your Telegram Bot Token: ").strip()
        save_config(config)
    bot_token = config["BOT_TOKEN"]

    # Ask user for CHAT_ID if not present
    if "CHAT_ID" not in config or not config["CHAT_ID"]:
        config["CHAT_ID"] = input("Please enter the Telegram Chat ID to send alerts: ").strip()
        save_config(config)
    chat_id = config["CHAT_ID"]

    # Initialize DB
    db_manager = DatabaseManager()
    init_db(db_manager)

    # Create a DailyStats object
    daily_stats = DailyStats()
    # Associate the db_manager if needed:
    daily_stats.db_manager = db_manager  # so we can log events from it

    # Create an alerts instance
    alerts = TelegramAlerts(bot_token, chat_id)

    # Create tasks
    monitor_task = asyncio.create_task(monitor_internet(alerts, daily_stats))
    stats_task = asyncio.create_task(periodic_stats_report(alerts, daily_stats, db_manager))

    # Wait for them
    await asyncio.gather(monitor_task, stats_task)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Script interrupted by user.")
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
