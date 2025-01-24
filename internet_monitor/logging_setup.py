# logging_setup.py
import logging
import os

def setup_logger():
    # Create a directory for logs if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    log_file = os.path.join("logs", "netpulse.log")

    # Get the root logger and set its overall level to DEBUG
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Remove any default handlers
    while logger.handlers:
        logger.handlers.pop()

    # --- File Handler (writes all levels to netpulse.log) ---
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # --- Console Handler (only WARNING and above) ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_formatter = logging.Formatter(
        "%(asctime)s - [%(levelname)s] %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
