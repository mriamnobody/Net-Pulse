import logging
import sys

def setup_logger(log_file: str = "internet_monitor.log"):
    """
    Configure the root logger to log to both console and a file.
    """
    logger = logging.getLogger()
    # You can adjust the logging level here (e.g., DEBUG, INFO, WARNING)
    logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter(
        "%(asctime)s - [%(levelname)s] %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_formatter = logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s - [Line: %(lineno)d]"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
