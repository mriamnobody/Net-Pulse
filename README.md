# NetPulse – Precision Internet Monitoring Redefined 🚀

**NetPulse** isn’t just another internet monitoring tool—it's your vigilant digital watchdog, meticulously tracking connectivity and latency to ensure uninterrupted online experiences. With instant Telegram alerts, detailed performance logs, and insightful reports, NetPulse turns raw data into actionable insights.

---

## 🌟 Why NetPulse Stands Out

- **Hyper-Accurate Connectivity Tracking**  
  NetPulse detects even fleeting connectivity hiccups, ensuring you’re always aware of network performance.

- **Tailored Alerts for Proactive Monitoring**  
  Receive real-time Telegram alerts for downtime, high ping, or unusual patterns—customized to your thresholds.

- **Crystal-Clear Reports**  
  Gain valuable insights with daily, weekly, and monthly summaries, empowering informed decisions about your network's health.

- **System Downtime Accountability**  
  Unique tracking of the monitor’s own offline periods ensures no gap in your performance data.

---

## 🔧 Key Features

### **Automated Real-Time Alerts**
- Instant Telegram notifications for downtime or high latency.
- Configurable thresholds ensure you're only alerted when it matters.

### **Comprehensive Logging**
- Local SQLite database stores all logs, events, and performance summaries for historical analysis.

### **Customizable Configurations**
- Intuitive setup process for Telegram Bot Token and Chat ID validation—get up and running in minutes.

### **Periodic Performance Summaries**
- Scheduled daily, weekly, and monthly reports sent directly to Telegram, highlighting uptime, downtime, and latency trends.

### **Downtime Transparency**
- Tracks and logs system inactivity separately, providing a complete picture of your monitoring reliability.

---

## 📂 Project Breakdown

- **`alerts.py`**  
  Handles Telegram notifications using the `python-telegram-bot` library, ensuring reliable delivery of alerts.

- **`config.py`**  
  Simplifies configuration management, including interactive Telegram credential validation.

- **`db_manager.py`**  
  Manages the SQLite database, creating tables for event logging, daily stats, and system heartbeat tracking.

- **`daily_stats.py`**  
  Tracks detailed daily metrics like uptime, downtime, ping performance, and failure events.

- **`monitor.py`**  
  Continuously pings servers, evaluates network health, and triggers alerts in case of connectivity issues.

- **`stats_reporter.py`**  
  Aggregates data for scheduled summaries and logs them to both the database and Telegram.

- **`logging_setup.py`**  
  Robust logging configuration for debugging and detailed runtime logs.

- **`main.py`**  
  The orchestrator of the system, handling initialization, validation, and async task management.

---

## 🎯 Who Should Use NetPulse?

Whether you're a tech enthusiast, IT professional, or a business relying on stable internet, **NetPulse** offers unmatched insights and peace of mind. Stay informed, act faster, and optimize your online reliability.

---

## 🚀 Get Started

1. Clone the repository:  
   ```bash
   git clone https://github.com/your-repo/NetPulse.git

2. 📦 Install Dependencies
   ```
   pip install -r requirements.txt
   ```
3. 🤖 Set Up Telegram Bot
- Create a new Telegram bot via BotFather.
- Save the Bot Token provided by BotFather.
- Get your Chat ID by messaging your bot and using the /start command.

  
