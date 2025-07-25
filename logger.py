import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)

console_handler = logging.StreamHandler()
file_handler = RotatingFileHandler("logs/latest.log", maxBytes=1000000, backupCount=3)

formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[console_handler, file_handler]
)

open("logs/latest.log", "w").close()