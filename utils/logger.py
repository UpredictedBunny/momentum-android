"""
logger.py  (Android-adapted)
------------------------------
Same as the desktop version but writes the log file to APP_DATA_DIR
(Android private storage) rather than PROJECT_ROOT/logs/.

On Android, stdout/stderr are readable via adb logcat, so we also
keep the console handler for development.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from config.settings import settings, APP_DATA_DIR

_configured = False


def _configure_root_logger() -> None:
    global _configured
    if _configured:
        return

    log_cfg = settings.logging
    log_path = APP_DATA_DIR / log_cfg.file
    log_path.parent.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger("momentum")
    root.setLevel(getattr(logging, log_cfg.level, logging.INFO))

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Rotating file handler — writes to Android private storage
    file_handler = RotatingFileHandler(
        str(log_path),
        maxBytes=log_cfg.max_bytes,
        backupCount=log_cfg.backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    # Console handler — visible via `adb logcat` during development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)

    _configured = True


def get_logger(module_name: str) -> logging.Logger:
    _configure_root_logger()
    return logging.getLogger(f"momentum.{module_name}")
