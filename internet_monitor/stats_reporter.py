import asyncio
import logging
from datetime import datetime

from internet_monitor.daily_stats import DailyStats
from internet_monitor.db_manager import log_event, DatabaseManager
from internet_monitor.alerts import TelegramAlerts

logger = logging.getLogger(__name__)

DAILY_STATS_FILE = "daily_stats.log"
STATS_ALERT_TIMES = ["07:00", "18:00"]
RESET_TIME = "00:00"

WEEKLY_STATS_ALERT_TIME = "09:00"    # Monday 9 AM
MONTHLY_STATS_ALERT_TIME = "09:00"  # 1st day of month 9 AM

def log_daily_stats_to_file(stats):
    summary = (
        f"Daily Stats Report ({datetime.now().strftime('%Y-%m-%d')}):\n"
        f"✅ Uptime: {stats['uptime'] / 60:.2f} min ({stats['uptime_percentage']:.2f}%)\n"
        f"❌ Downtime: {stats['downtime'] / 60:.2f} min ({stats['downtime_percentage']:.2f}%)\n"
        f"⚠️ High Pings: {stats['high_ping_count']} times\n"
        f"⏱ Time in High Ping: {stats['high_ping_seconds'] / 60:.2f} min\n"
        f"🚨 Internet Failures: {stats['internet_failures']} times\n"
        f"📡 Packet Loss: {stats['packet_loss']:.2f}%\n"
        f"📈 Average Ping: {stats['average_ping']:.2f} ms\n"
        f"📊 Max Ping: {stats['max_ping']:.2f} ms\n"
        f"🏆 Most Stable Server: {stats['most_stable_server']}\n"
        f"⏳ Longest Downtime: {stats['longest_downtime'] / 60:.2f} min\n"
        f"------------------------------------\n"
    )
    with open(DAILY_STATS_FILE, "a", encoding='utf-8') as f:
        f.write(summary)

def log_daily_stats_to_db(db_manager: DatabaseManager, stats):
    conn = db_manager.connect()
    try:
        cursor = conn.cursor()
        date_str = datetime.now().strftime('%Y-%m-%d')
        time_str = datetime.now().strftime('%H:%M:%S')
        cursor.execute("""
            INSERT INTO daily_stats (
                date, time, uptime_seconds, downtime_seconds, high_ping_count,
                high_ping_seconds, internet_failures, total_pings, failed_pings,
                average_ping, max_ping, longest_downtime
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            date_str, time_str,
            stats['uptime'],
            stats['downtime'],
            stats['high_ping_count'],
            stats['high_ping_seconds'],
            stats['internet_failures'],
            stats['total_pings'],
            stats['failed_pings'],
            stats['average_ping'],
            stats['max_ping'],
            stats['longest_downtime']
        ))
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to log daily stats to DB: {e}")
    finally:
        db_manager.close()

def get_aggregated_stats(db_manager: DatabaseManager, period):
    """
    Aggregates weekly or monthly data from daily_stats table.
    """
    conn = db_manager.connect()
    cursor = conn.cursor()

    try:
        if period == 'weekly':
            cursor.execute("""
                SELECT
                    SUM(uptime_seconds) as uptime_seconds,
                    SUM(downtime_seconds) as downtime_seconds,
                    SUM(high_ping_count) as high_ping_count,
                    SUM(high_ping_seconds) as high_ping_seconds,
                    SUM(internet_failures) as internet_failures,
                    SUM(total_pings) as total_pings,
                    SUM(failed_pings) as failed_pings,
                    AVG(average_ping) as average_ping,
                    MAX(max_ping) as max_ping,
                    MAX(longest_downtime) as longest_downtime
                FROM daily_stats
                WHERE date >= date('now', '-6 days')
            """)
        elif period == 'monthly':
            cursor.execute("""
                SELECT
                    SUM(uptime_seconds) as uptime_seconds,
                    SUM(downtime_seconds) as downtime_seconds,
                    SUM(high_ping_count) as high_ping_count,
                    SUM(high_ping_seconds) as high_ping_seconds,
                    SUM(internet_failures) as internet_failures,
                    SUM(total_pings) as total_pings,
                    SUM(failed_pings) as failed_pings,
                    AVG(average_ping) as average_ping,
                    MAX(max_ping) as max_ping,
                    MAX(longest_downtime) as longest_downtime
                FROM daily_stats
                WHERE date >= date('now', 'start of month')
            """)
        else:
            return None

        result = cursor.fetchone()
        if result and any(result):
            aggregated_stats = {
                'uptime': result[0] or 0,
                'downtime': result[1] or 0,
                'high_ping_count': result[2] or 0,
                'high_ping_seconds': result[3] or 0,
                'internet_failures': result[4] or 0,
                'total_pings': result[5] or 0,
                'failed_pings': result[6] or 0,
                'average_ping': result[7] or 0,
                'max_ping': result[8] or 0,
                'longest_downtime': result[9] or 0
            }
            total_time = aggregated_stats['uptime'] + aggregated_stats['downtime']
            uptime_percentage = (aggregated_stats['uptime'] / total_time * 100) if total_time > 0 else 0
            downtime_percentage = 100 - uptime_percentage
            packet_loss = (aggregated_stats['failed_pings'] / aggregated_stats['total_pings'] * 100) if aggregated_stats['total_pings'] > 0 else 0
            aggregated_stats['uptime_percentage'] = uptime_percentage
            aggregated_stats['downtime_percentage'] = downtime_percentage
            aggregated_stats['packet_loss'] = packet_loss
            return aggregated_stats
        else:
            logger.warning(f"No data available for {period} stats.")
            return None
    finally:
        db_manager.close()

def log_weekly_stats_to_file(stats):
    summary = (
        f"Weekly Stats Report ({datetime.now().strftime('%Y-%m-%d')}):\n"
        f"✅ Uptime: {stats['uptime'] / 60:.2f} min ({stats['uptime_percentage']:.2f}%)\n"
        f"❌ Downtime: {stats['downtime'] / 60:.2f} min ({stats['downtime_percentage']:.2f}%)\n"
        f"⚠️ High Pings: {stats['high_ping_count']} times\n"
        f"⏱ Time in High Ping: {stats['high_ping_seconds'] / 60:.2f} min\n"
        f"🚨 Internet Failures: {stats['internet_failures']} times\n"
        f"📡 Packet Loss: {stats['packet_loss']:.2f}%\n"
        f"📈 Average Ping: {stats['average_ping']:.2f} ms\n"
        f"📊 Max Ping: {stats['max_ping']:.2f} ms\n"
        f"⏳ Longest Downtime: {stats['longest_downtime'] / 60:.2f} min\n"
        f"------------------------------------\n"
    )
    with open(DAILY_STATS_FILE, "a", encoding='utf-8') as f:
        f.write(summary)

def log_monthly_stats_to_file(stats):
    summary = (
        f"Monthly Stats Report ({datetime.now().strftime('%Y-%m-%d')}):\n"
        f"✅ Uptime: {stats['uptime'] / 60:.2f} min ({stats['uptime_percentage']:.2f}%)\n"
        f"❌ Downtime: {stats['downtime'] / 60:.2f} min ({stats['downtime_percentage']:.2f}%)\n"
        f"⚠️ High Pings: {stats['high_ping_count']} times\n"
        f"⏱ Time in High Ping: {stats['high_ping_seconds'] / 60:.2f} min\n"
        f"🚨 Internet Failures: {stats['internet_failures']} times\n"
        f"📡 Packet Loss: {stats['packet_loss']:.2f}%\n"
        f"📈 Average Ping: {stats['average_ping']:.2f} ms\n"
        f"📊 Max Ping: {stats['max_ping']:.2f} ms\n"
        f"⏳ Longest Downtime: {stats['longest_downtime'] / 60:.2f} min\n"
        f"------------------------------------\n"
    )
    with open(DAILY_STATS_FILE, "a", encoding='utf-8') as f:
        f.write(summary)

async def send_daily_stats(alerts: TelegramAlerts, stats):
    summary = (
        f"**📊 Daily Internet Stats Report ({datetime.now().strftime('%Y-%m-%d')}):**\n"
        f"✅ Uptime: {stats['uptime'] / 60:.2f} min ({stats['uptime_percentage']:.2f}%)\n"
        f"❌ Downtime: {stats['downtime'] / 60:.2f} min ({stats['downtime_percentage']:.2f}%)\n"
        f"⚠️ High Pings: {stats['high_ping_count']} times\n"
        f"⏱ Time in High Ping: {stats['high_ping_seconds'] / 60:.2f} min\n"
        f"🚨 Total number of Internet Failures: {stats['internet_failures']} times\n"
        f"⏱ Time in Internet Failure: {stats['downtime'] / 60:.2f} min\n"
        f"⏳ Longest Downtime: {stats['longest_downtime'] / 60:.2f} min\n"
    )
    await alerts.send_alert(summary)

async def send_weekly_stats(alerts: TelegramAlerts, stats):
    summary = (
        f"**📊 Weekly Internet Stats Report ({datetime.now().strftime('%Y-%m-%d')}):**\n"
        f"✅ Uptime: {stats['uptime'] / 3600:.2f} hrs ({stats['uptime_percentage']:.2f}%)\n"
        f"❌ Downtime: {stats['downtime'] / 3600:.2f} hrs ({stats['downtime_percentage']:.2f}%)\n"
        f"⚠️ High Pings: {stats['high_ping_count']} times\n"
        f"⏱ Time in High Ping: {stats['high_ping_seconds'] / 3600:.2f} hrs\n"
        f"🚨 Internet Failures: {stats['internet_failures']} times\n"
        f"📡 Packet Loss: {stats['packet_loss']:.2f}%\n"
        f"📈 Average Ping: {stats['average_ping']:.2f} ms\n"
        f"📊 Max Ping: {stats['max_ping']:.2f} ms\n"
        f"⏳ Longest Downtime: {stats['longest_downtime'] / 60:.2f} min\n"
    )
    await alerts.send_alert(summary)

async def send_monthly_stats(alerts: TelegramAlerts, stats):
    summary = (
        f"**📊 Monthly Internet Stats Report ({datetime.now().strftime('%Y-%m-%d')}):**\n"
        f"✅ Uptime: {stats['uptime'] / 3600:.2f} hrs ({stats['uptime_percentage']:.2f}%)\n"
        f"❌ Downtime: {stats['downtime'] / 3600:.2f} hrs ({stats['downtime_percentage']:.2f}%)\n"
        f"⚠️ High Pings: {stats['high_ping_count']} times\n"
        f"⏱ Time in High Ping: {stats['high_ping_seconds'] / 3600:.2f} hrs\n"
        f"🚨 Internet Failures: {stats['internet_failures']} times\n"
        f"📡 Packet Loss: {stats['packet_loss']:.2f}%\n"
        f"📈 Average Ping: {stats['average_ping']:.2f} ms\n"
        f"📊 Max Ping: {stats['max_ping']:.2f} ms\n"
        f"⏳ Longest Downtime: {stats['longest_downtime'] / 60:.2f} min\n"
    )
    await alerts.send_alert(summary)

async def periodic_stats_report(
    alerts: TelegramAlerts,
    daily_stats: DailyStats,
    db_manager: DatabaseManager
):
    """
    Periodically sends daily/weekly/monthly stats reports at specified times.
    Resets daily stats at midnight.
    """
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_weekday = now.weekday()  # Monday=0
        current_day = now.day

        # Daily Stats
        if current_time in STATS_ALERT_TIMES:
            stats = daily_stats.get_summary()
            log_daily_stats_to_file(stats)
            # We need daily_stats to know db_manager or pass it in:
            log_daily_stats_to_db(db_manager, stats)
            await send_daily_stats(alerts, stats)

        # Reset daily stats at midnight
        if current_time == RESET_TIME:
            daily_stats.reset()

        # Weekly Stats on Monday
        if current_time == WEEKLY_STATS_ALERT_TIME and current_weekday == 0:
            weekly_stats = get_aggregated_stats(db_manager, 'weekly')
            if weekly_stats:
                log_weekly_stats_to_file(weekly_stats)
                log_event(db_manager, "Weekly Stats", "Weekly Stats Recorded")
                await send_weekly_stats(alerts, weekly_stats)

        # Monthly Stats on 1st day
        if current_time == MONTHLY_STATS_ALERT_TIME and current_day == 1:
            monthly_stats = get_aggregated_stats(db_manager, 'monthly')
            if monthly_stats:
                log_monthly_stats_to_file(monthly_stats)
                log_event(db_manager, "Monthly Stats", "Monthly Stats Recorded")
                await send_monthly_stats(alerts, monthly_stats)

        await asyncio.sleep(60)  # check every minute
