import os
import logging
from logging.handlers import RotatingFileHandler
from app.config import settings

def setup_logger():
    """
    Sets up a logger with both console and rotating file handlers.
    Creates a 'logs' directory if it doesn't exist.
    """
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger("campuspilot")
    # Set logging level from settings
    log_level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    level = log_level_map.get(settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)

    # Prevent duplicate handlers if setup is called multiple times
    if logger.handlers:
        return logger

    # Formatter for log entries
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(name)s:%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler (rotating logs, max 5MB per file, keep 3 backups)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "campuspilot.log"),
        maxBytes=5*1024*1024,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Single logger instance
logger = setup_logger()
