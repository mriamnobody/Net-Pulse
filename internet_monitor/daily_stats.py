from datetime import datetime
import logging

logger = logging.getLogger(__name__)

HIGH_PING_THRESHOLD = 150  # ms

class DailyStats:
    """
    Collects daily statistics: uptime, downtime, high ping counts, etc.
    """

    def __init__(self):
        self.uptime_seconds = 0
        self.downtime_seconds = 0
        self.high_ping_count = 0
        self.high_ping_seconds = 0
        self.internet_failures = 0
        self.last_update_time = datetime.now()
        self.is_high_ping = False
        self.is_down = False
        self.total_pings = 0
        self.failed_pings = 0
        self.ping_times = []
        self.longest_downtime = 0
        self.system_downtime_seconds = 0
        self.current_downtime_start = None
        self.server_stats = {
            "1.1.1.1": {"downtime": 0, "high_pings": 0},
            "8.8.8.8": {"downtime": 0, "high_pings": 0}
        }

    def reset(self):
        """
        Reset the daily statistics.
        """
        self.__init__()

    def update(self, is_up, is_high_ping, ping_times, server_status):
        """
        Update the stats with the latest monitor cycle results.
        """
        now = datetime.now()
        elapsed = (now - self.last_update_time).total_seconds()

        # Uptime/Downtime
        if is_up:
            self.uptime_seconds += elapsed
            if self.is_down:
                self.internet_failures += 1
                downtime = (now - self.current_downtime_start).total_seconds()
                self.longest_downtime = max(self.longest_downtime, downtime)
                self.is_down = False
                self.current_downtime_start = None
        else:
            self.downtime_seconds += elapsed
            if not self.is_down:
                self.is_down = True
                self.current_downtime_start = now

        # High ping
        if is_high_ping:
            self.high_ping_seconds += elapsed
            if not self.is_high_ping:
                self.high_ping_count += 1
                self.is_high_ping = True
        else:
            self.is_high_ping = False

        # Ping times
        self.total_pings += len(ping_times)
        self.failed_pings += sum(1 for s in server_status if not s)
        self.ping_times.extend(filter(None, ping_times))

        # Per-server stats
        for server, status in zip(self.server_stats.keys(), server_status):
            if not status:
                self.server_stats[server]["downtime"] += elapsed
            elif any(p is not None and p > HIGH_PING_THRESHOLD for p in ping_times):
                self.server_stats[server]["high_pings"] += 1

        self.last_update_time = now

    def get_summary(self):
        """
        Return a dictionary summarizing the daily stats.
        """
        total_time = self.uptime_seconds + self.downtime_seconds
        uptime_percentage = (self.uptime_seconds / total_time * 100) if total_time > 0 else 0
        downtime_percentage = 100 - uptime_percentage
        packet_loss = (self.failed_pings / self.total_pings * 100) if self.total_pings > 0 else 0
        average_ping = sum(self.ping_times) / len(self.ping_times) if self.ping_times else 0
        max_ping = max(self.ping_times) if self.ping_times else 0
        most_stable_server = min(self.server_stats.items(),
                                 key=lambda x: x[1]["downtime"] + x[1]["high_pings"])[0]

        return {
            "uptime": self.uptime_seconds,
            "downtime": self.downtime_seconds,
            "uptime_percentage": uptime_percentage,
            "downtime_percentage": downtime_percentage,
            "high_ping_count": self.high_ping_count,
            "high_ping_seconds": self.high_ping_seconds,
            "internet_failures": self.internet_failures,
            "total_pings": self.total_pings,
            "failed_pings": self.failed_pings,
            "packet_loss": packet_loss,
            "average_ping": average_ping,
            "max_ping": max_ping,
            "system_downtime": self.system_downtime_seconds,
            "most_stable_server": most_stable_server,
            "longest_downtime": self.longest_downtime
        }
