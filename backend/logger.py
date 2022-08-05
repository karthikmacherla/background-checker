import logging
import sys
from config import get_config

config = get_config()

logging.root.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(levelname)s: %(name)s: line %(lineno)s, %(message)s")

file_handler = logging.FileHandler(config.log_loc)
file_handler.setFormatter(formatter)
file_handler.setLevel(6999)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)


def create_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger