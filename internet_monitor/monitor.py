import asyncio
import logging
from datetime import datetime
import subprocess

from internet_monitor.alerts import TelegramAlerts
from internet_monitor.db_manager import log_event
from internet_monitor.daily_stats import DailyStats, HIGH_PING_THRESHOLD

logger = logging.getLogger(__name__)

PING_INTERVAL = 1  # seconds

async def ping(host):
    """
    Perform one ping to a host and return (is_up, ping_time_in_ms or None).
    This uses an async subprocess call to the system 'ping'.
    """
    try:
        proc = await asyncio.create_subprocess_exec(
            "ping", "-n", "1", "-w", "1000", host,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0:
            output = stdout.decode('utf-8', errors='ignore')
            time_index = output.find("time=")
            if time_index != -1:
                time_end_index = output.find("ms", time_index)
                if time_end_index != -1:
                    ping_time = float(output[time_index + 5:time_end_index].strip())
                    return True, ping_time
            return True, None
        else:
            return False, None
    except Exception as e:
        logger.error(f"Ping failed for host {host}: {e}")
        return False, None

class InternetMonitor:
    """
    Responsible for tracking up/down state changes and sending immediate alerts.
    """
    def __init__(self):
        self.is_down = False
        self.is_high_ping = False
        self.last_down_time = None
        self.lock = asyncio.Lock()

    async def update_state(self, status, ping_times, alerts: TelegramAlerts, daily_stats: DailyStats):
        """
        Check if the internet went down or high ping started,
        and send immediate alerts if so.
        """
        async with self.lock:
            all_servers_down = all(not s for s in status)

            # Internet down
            if all_servers_down:
                if not self.is_down:
                    self.is_down = True
                    self.last_down_time = datetime.now()
                    logger.info("Internet Down: All servers unresponsive.")
                    await alerts.send_alert("🚨 Internet is DOWN on all servers!")
            else:
                if self.is_down:
                    # We just restored
                    self.is_down = False
                    restore_time = datetime.now()
                    downtime = restore_time - self.last_down_time
                    formatted_downtime = str(downtime).split(".")[0]  # remove microseconds
                    message = (
                        f"**✅ Internet Restored**\n"
                        f"❌ Outage started at: {self.last_down_time.strftime('%H:%M:%S')}\n"
                        f"🕒 Restored at: {restore_time.strftime('%H:%M:%S')}\n"
                        f"⏱ Total Downtime: {formatted_downtime}"
                    )
                    log_event(
                        db_manager=daily_stats.db_manager,  # We'll see how we pass this
                        event_type="Internet Restored",
                        details=message
                    )
                    await alerts.send_alert(message)

            # High ping (if all servers are up but ping is above threshold)
            all_high_ping = all(pt is not None and pt > HIGH_PING_THRESHOLD for pt in ping_times if pt is not None)
            if all_high_ping and not all_servers_down:
                if not self.is_high_ping:
                    self.is_high_ping = True
                    logger.info("High Ping Detected.")
                    await alerts.send_alert("⚠️ High Ping Alert.")
            else:
                self.is_high_ping = False

async def monitor_internet(alerts: TelegramAlerts, daily_stats: DailyStats):
    """
    Repeatedly ping the servers, update daily stats, and let the InternetMonitor
    decide if we should send immediate alerts.
    """
    servers = ["1.1.1.1", "8.8.8.8"]
    net_monitor = InternetMonitor()

    while True:
        ping_tasks = [ping(server) for server in servers]
        results = await asyncio.gather(*ping_tasks)
        status, ping_times = zip(*results)  # status -> tuple of bool, ping_times -> tuple of float or None

        # Determine if any server is up
        is_up = any(status)
        # Determine if high ping
        is_high_ping = all(pt is not None and pt > HIGH_PING_THRESHOLD for pt in ping_times if pt is not None)

        # Update daily stats
        daily_stats.update(is_up, is_high_ping, ping_times, status)

        # Update immediate state changes
        await net_monitor.update_state(status, ping_times, alerts, daily_stats)

        await asyncio.sleep(PING_INTERVAL)
