"""
This module sets up a logger for the wizard application.
"""

import os
import logging
from logging.handlers import RotatingFileHandler

# Define log directory and file
LOG_DIR = "logs"
LOG_FILE = "wizard.log"
os.makedirs(LOG_DIR, exist_ok=True)
log_path = os.path.join(LOG_DIR, LOG_FILE)

# Create a logger
logger = logging.getLogger("wizard")
logger.setLevel(logging.INFO)

# Avoid adding handlers multiple times
if not logger.handlers:
    # Formatter
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler (rotates at 5MB, keeps 3 backups)
    file_handler = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=3)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
