import json
import logging
import os

logger = logging.getLogger(__name__)

CONFIG_FILE = "config.json"

def load_config():
    """
    Load configuration from config.json if it exists.
    Otherwise return an empty dict.
    """
    if not os.path.exists(CONFIG_FILE):
        logger.warning("Configuration file not found. Using empty config.")
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Error reading config.json: {e}")
        return {}

def save_config(config):
    """
    Save configuration dictionary to config.json.
    """
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        logger.info("Configuration saved successfully.")
    except OSError as e:
        logger.error(f"Error writing config.json: {e}")
