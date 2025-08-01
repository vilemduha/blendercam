"""Fabex 'logging_utils.py' © 2025
"""

from datetime import datetime
import logging
from pathlib import Path

current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

log = log.info = log.error = log.warning = print

# log = logging.getLogger("fabex_logger")
# log.setLevel(logging.CRITICAL + 1)

# # Create file handler for logging
# log_path = Path(__file__).parent.parent / "logs" / f"{current_time}.log"
# file_handler = logging.FileHandler(log_path)
# file_handler.setLevel(logging.DEBUG)

# # Create another file handler for error logging
# error_log_path = Path(__file__).parent.parent / "logs" / f"Error_{current_time}.log"
# error_handler = logging.FileHandler(error_log_path)
# error_handler.setLevel(logging.ERROR)

# # Create console handler to pass messages to console
# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.INFO)

# # Define custom format for the log messages
# file_formatter = logging.Formatter(
#     "%(asctime)s | %(levelname)8s: %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
# )
# error_formatter = logging.Formatter(
#     "%(asctime)s | %(levelname)s: %(message)s | File '%(pathname)s', line %(lineno)d in %(funcName)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
# )
# console_formatter = logging.Formatter(
#     "%(message)s",
# )

# file_handler.setFormatter(file_formatter)
# error_handler.setFormatter(error_formatter)
# console_handler.setFormatter(console_formatter)

# # Adding handlers to the logger
# log.addHandler(file_handler)
# log.addHandler(error_handler)
# log.addHandler(console_handler)
