import sqlite3
import logging

logger = logging.getLogger(__name__)

DATABASE_FILE = "internet_monitor.db"

class DatabaseManager:
    def __init__(self, db_file=DATABASE_FILE):
        self.db_file = db_file
        self.conn = None

    def connect(self):
        """
        Establish a SQLite database connection (if not already connected).
        """
        if self.conn is None:
            try:
                self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
                logger.info("Database connection established.")
            except sqlite3.Error as e:
                logger.error(f"Failed to connect to database: {e}")
        return self.conn

    def close(self):
        """
        Close the SQLite connection.
        """
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Database connection closed.")

def init_db(db_manager: DatabaseManager):
    """
    Create the required tables if they do not already exist.
    """
    conn = db_manager.connect()
    try:
        cursor = conn.cursor()
        # Event log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        """)
        # Daily stats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                date DATE,
                time TIME,
                uptime_seconds REAL,
                downtime_seconds REAL,
                high_ping_count INTEGER,
                high_ping_seconds REAL,
                internet_failures INTEGER,
                total_pings INTEGER,
                failed_pings INTEGER,
                average_ping REAL,
                max_ping REAL,
                longest_downtime REAL,
                PRIMARY KEY (date, time)
            )
        """)
        conn.commit()
        logger.info("Database initialized successfully.")
    except sqlite3.Error as e:
        logger.error(f"Failed to initialize database: {e}")

def log_event(db_manager: DatabaseManager, event_type, details):
    """
    Log an event into the event_log table.
    """
    try:
        conn = db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO event_log (event_type, details) VALUES (?, ?)", (event_type, details))
        conn.commit()
        logger.info(f"Event: {event_type} | Details: {details}")
    except sqlite3.Error as e:
        logger.error(f"Failed to log event to database: {e}")
