# NetPulse – Real-Time Internet Monitoring & Alerts

NetPulse continuously checks internet connectivity and latency, storing logs in a local SQLite database. It automatically sends Telegram alerts for downtime, high latency, and daily/weekly/monthly status summaries.

## Key Features
- **Automated Alerts**  
  Notifies via Telegram when the internet goes down or when ping times exceed a configurable threshold.

- **Detailed Logging**  
  Stores event logs and daily statistics in a local SQLite database for historical insight.

- **Configurable Bot Credentials**  
  Interactive setup to validate and save Telegram Bot Token and Chat ID.

- **Daily/Weekly/Monthly Reports**  
  Periodic scripts generate usage summaries and uptime percentages, delivered to Telegram.

- **System Downtime Detection**  
  Detects periods when the monitoring script itself was offline and logs this separately.

## Project Structure
- **`alerts.py`**  
  Defines a class for sending Telegram alerts asynchronously using `python-telegram-bot`.

- **`config.py`**  
  Handles loading, saving, and validating configuration (bot token, chat ID).

- **`db_manager.py`**  
  Manages the SQLite database connection and provides helper functions to log events and initialize tables.

- **`daily_stats.py`**  
  Tracks daily uptime, downtime, high ping durations, and other network performance metrics.

- **`monitor.py`**  
  Continuously pings servers, updates statistics, and triggers Telegram alerts on status changes.

- **`stats_reporter.py`**  
  Sends scheduled (daily, weekly, monthly) reports, aggregating data from the database.

- **`logging_setup.py`**  
  Configures both file and console logging, capturing detailed output in `logs/netpulse.log`.

- **`main.py`**  
  The entry point, orchestrating configuration validation, database initialization, and async tasks.

## Why This Matters
NetPulse provides a lightweight but robust solution for anyone needing to track internet reliability. By logging outages and high latency incidents in real-time, you gain a historical record and instant alerts to maintain smooth online operations.

---
