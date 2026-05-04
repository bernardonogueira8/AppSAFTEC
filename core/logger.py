import logging
import sys
import os
from pathlib import Path

APP_NAME = "SAFTEC"

def is_frozen():
    return getattr(sys, "frozen", False)


def is_android():
    return sys.platform == "android"


def get_log_dir():
    if is_android():
        return Path(os.getcwd()) / "files" / "logs"
    if is_frozen():
        # Usar APPDATA (Roaming) em vez de LOCALAPPDATA
        base = Path(os.getenv("APPDATA", Path.home()))
        return base / APP_NAME / "logs"
    # DESENVOLVIMENTO
    return Path.cwd() / "logs"

LOG_DIR = get_log_dir()
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "saftec.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)


def get_logger(name: str):
    return logging.getLogger(name)
