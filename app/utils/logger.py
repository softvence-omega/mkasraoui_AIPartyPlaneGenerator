import logging
import os
from datetime import datetime

from app.config import LOG_DIR

# make dir
os.makedirs(LOG_DIR, exist_ok=True)

# log file name
LOG_FILE = os.path.join(LOG_DIR, f"log_{datetime.now().strftime('%Y_%m_%d-%H_%M_%S')}.log")

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

## Function
def get_logger(name : str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        logging.basicConfig(
            filename=LOG_FILE,
            format=LOG_FORMAT,
            datefmt=DATE_FORMAT,
            level = logging.INFO
        )

    return logger

