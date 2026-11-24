"""Fabex 'logging_utils.py' © 2025"""

import logging
from datetime import UTC, datetime
from pathlib import Path

LOG_WIDTH = 60


class ConsoleFormatter(logging.Formatter):
    def format(self, record):
        if ":" in str(record.msg):
            record.msg = record.msg.split(":")
            record.msg = f"{record.msg[0]:>28}:{record.msg[1]:<30}"
        return super().format(record)


def heading(text):
    border = int((LOG_WIDTH - len(text) - 4) / 2) * "~"
    text = f"\n[{border} {text} {border}]"
    if len(text) == 60:
        text = text.replace("~]", "~~]")
    return text


current_time = datetime.now(tz=UTC).strftime("%Y%m%d_%H%M%S")

log = logging.getLogger("fabex_logger")
log.setLevel(logging.DEBUG)

# Create file handler for logging
log_folder = Path(__file__).parent.parent / "logs"
log_folder.mkdir(parents=True, exist_ok=True)
log_path = Path(log_folder, f"{current_time}.log")
file_handler = logging.FileHandler(log_path)
file_handler.setLevel(logging.DEBUG)

# Create another file handler for error logging
error_log_folder = Path(__file__).parent.parent / "logs"
error_log_folder.mkdir(parents=True, exist_ok=True)
error_log_path = Path(error_log_folder, f"Error_{current_time}.log")
error_handler = logging.FileHandler(error_log_path)
error_handler.setLevel(logging.ERROR)

# Create another file handler for test logging
test_log_folder = Path(__file__).parent.parent / "logs"
test_log_folder.mkdir(parents=True, exist_ok=True)
test_log_path = Path(error_log_folder, f"Test_{current_time}.log")
test_handler = logging.FileHandler(error_log_path)
test_handler.setLevel(logging.ERROR)

# Create console handler to pass messages to console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Define custom format for the log messages
file_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)8s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
error_formatter = test_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s: %(message)s | File '%(pathname)s', line %(lineno)d in %(funcName)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
console_formatter = ConsoleFormatter(
    "%(message)s",
)

file_handler.setFormatter(file_formatter)
error_handler.setFormatter(error_formatter)
test_handler.setFormatter(test_formatter)
console_handler.setFormatter(console_formatter)

# Adding handlers to the logger
log.addHandler(file_handler)
log.addHandler(error_handler)
log.addHandler(test_handler)
log.addHandler(console_handler)
