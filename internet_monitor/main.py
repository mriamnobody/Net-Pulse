# main.py
import asyncio
import time  # For sleep delays in user messages
from internet_monitor.alerts import TelegramAlerts
from internet_monitor.daily_stats import DailyStats
from internet_monitor.monitor import monitor_internet
from internet_monitor.db_manager import DatabaseManager, init_db, get_last_heartbeat, log_event
from internet_monitor.logging_setup import logging, setup_logger
from internet_monitor.stats_reporter import periodic_stats_report
from internet_monitor.config import (
    load_config,
    save_config,
    prompt_and_validate_bot_details
)
from telegram import Bot
from telegram.error import TelegramError

async def main():
    setup_logger()

    # This log message goes into the file (netpulse.log) but not the console
    logging.info("Internet Monitor script started.")

    # ---- Friendly print messages (with emojis) that won't be logged ----
    print("🚀 NetPulse started 🚀")  # (1) Start message
    
    # Load config
    config = load_config()
    
    # Check if config has BOT_TOKEN & CHAT_ID
    if config.get("BOT_TOKEN") and config.get("CHAT_ID"):
        # (2) Found existing credentials
        print("🤖✅ Bot token and chat ID found!")
        
        choice = input("❓ Do you want to use them or add new ones? (use/add): ").strip().lower()
        
        if choice == "use":
            # (3) "Loading configuration..." with emojis
            print("⚙️ Loading configuration...")
            time.sleep(1)
            
            # (4) "Validating configuration..."
            print("🔎 Validating configuration...")
            
            # Attempt to validate
            bot_token = config["BOT_TOKEN"]
            chat_id = config["CHAT_ID"]
            try:
                bot = Bot(token=bot_token)
                me = await bot.get_me()  # Check if token is valid
                await bot.send_message(chat_id=chat_id, text="Test message: Bot credentials look good!")
                
                # (5) "Bot token and chat ID valid"
                print("✅ Bot token and chat ID valid!")
                time.sleep(1)
                
                # (6) "Beginning internet status monitor..."
                print("🌐 Beginning internet status monitor...")
                time.sleep(1)
                
            except TelegramError as e:
                logging.error(f"Stored credentials invalid or error occurred: {e}")
                # If invalid, fallback to the prompt
                print("❌ Existing token/chat ID invalid. Let's set them up.")
                bot_token, chat_id = await prompt_and_validate_bot_details()
                config["BOT_TOKEN"] = bot_token
                config["CHAT_ID"] = chat_id
                save_config(config)
                
        else:
            # User wants to add new ones
            bot_token, chat_id = await prompt_and_validate_bot_details()
            config["BOT_TOKEN"] = bot_token
            config["CHAT_ID"] = chat_id
            save_config(config)
            
    else:
        # If no token/chat ID, prompt user for them
        bot_token, chat_id = await prompt_and_validate_bot_details()
        config["BOT_TOKEN"] = bot_token
        config["CHAT_ID"] = chat_id
        save_config(config)

    # By here we definitely have a valid BOT_TOKEN and CHAT_ID
    bot_token = config["BOT_TOKEN"]
    chat_id = config["CHAT_ID"]

    # Initialize DB
    db_manager = DatabaseManager()
    init_db(db_manager)

    # Check system downtime on startup
    last_heartbeat_str = get_last_heartbeat(db_manager)
    if last_heartbeat_str:
        from datetime import datetime
        fmt = "%Y-%m-%d %H:%M:%S"
        try:
            last_heartbeat_time = datetime.strptime(last_heartbeat_str, fmt)
        except ValueError:
            # If your DB’s default datetime format is different, adjust accordingly
            last_heartbeat_time = datetime.fromisoformat(last_heartbeat_str)
        
        now = datetime.now()
        difference = (now - last_heartbeat_time).total_seconds()
        
        # For example, if difference > 60, we consider it a real system downtime
        if difference > 60:  # 1 minute threshold
            # This is system downtime. We'll log it and notify
            downtime_minutes = difference / 60.0
            message = (
                f"⛔ *System Offline Detected*\n"
                f"Last heartbeat was at: {last_heartbeat_time}\n"
                f"System was likely down for ~{downtime_minutes:.1f} minutes."
            )

            # Log event
            log_event(db_manager, "System Down", message)

            # We also add it to daily_stats
            # But daily_stats isn't created yet - do that now:
            daily_stats = DailyStats()
            daily_stats.db_manager = db_manager
            daily_stats.system_downtime_seconds += difference

            # Alternatively, store it, and re-use the same `daily_stats` instance after creation
            # but let's just keep going:
            
            # Possibly send an immediate Telegram alert
            # But you need your "alerts" object for that. So let's create that early:
            alerts = TelegramAlerts(bot_token, chat_id)
            await alerts.send_alert(message)
        else:
            # No large gap, or the difference is negligible
            daily_stats = DailyStats()
            daily_stats.db_manager = db_manager
    else:
        # No recorded heartbeat in DB, so just create a fresh daily_stats
        daily_stats = DailyStats()
        daily_stats.db_manager = db_manager

    # Create Telegram alerts instance
    alerts = TelegramAlerts(bot_token, chat_id)

    # Create tasks
    monitor_task = asyncio.create_task(monitor_internet(alerts, daily_stats))
    stats_task = asyncio.create_task(periodic_stats_report(alerts, daily_stats, db_manager))

    # Run forever (or until an error/KeyboardInterrupt)
    await asyncio.gather(monitor_task, stats_task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Script interrupted by user.")
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
