"""
settings.py  (Android-adapted)
-------------------------------
Identical logic to the desktop version but resolves writable paths
to Android app-private storage instead of PROJECT_ROOT.

On Android:  /data/data/com.upredictedbunny.momentum/files/
On desktop:  ~/.momentum/  (development fallback)

PROJECT_ROOT is only used for read-only bundled assets (config.json,
schema.sql). All writable paths (DB, logs, backups) go to APP_DATA_DIR.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

# -----------------------------------------------------------------------
# Bundled asset root — lives inside the APK / source tree (read-only)
# -----------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "config.json"

# -----------------------------------------------------------------------
# Writable data root — Android private storage or dev fallback
# -----------------------------------------------------------------------
def _get_app_data_dir() -> Path:
    """Return a writable directory that works on Android and on a PC.

    Priority order:
      1. android.storage.app_storage_path()  — preferred (python-for-android >= 2020)
      2. ANDROID_PRIVATE env var             — always set by p4a bootstrap
      3. ~/.momentum_android                 — desktop dev fallback
    """
    # 1 — python-for-android android.storage module
    try:
        from android.storage import app_storage_path  # type: ignore
        return Path(app_storage_path())
    except ImportError:
        pass

    # 2 — ANDROID_PRIVATE is set by the p4a bootstrap on every p4a app
    android_private = os.environ.get("ANDROID_PRIVATE")
    if android_private:
        return Path(android_private)

    # 3 — Desktop / CI fallback
    dev_dir = Path.home() / ".momentum_android"
    dev_dir.mkdir(parents=True, exist_ok=True)
    return dev_dir


APP_DATA_DIR: Path = _get_app_data_dir()


class _DotDict(dict):
    """Dict with attribute access: settings.theme.accent instead of settings['theme']['accent']."""

    def __getattr__(self, key: str) -> Any:
        try:
            value = self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc
        if isinstance(value, dict):
            value = _DotDict(value)
        return value


class Settings:
    """Singleton configuration manager — reads config.json once."""

    _instance: "Settings | None" = None

    def __new__(cls) -> "Settings":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self) -> None:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            self._data: dict[str, Any] = json.load(f)

    def reload(self) -> None:
        self._load()

    def __getattr__(self, key: str) -> Any:
        try:
            value = self._data[key]
        except KeyError as exc:
            raise AttributeError(f"No config section '{key}'") from exc
        if isinstance(value, dict):
            return _DotDict(value)
        return value

    def get(self, dotted_path: str, default: Any = None) -> Any:
        node: Any = self._data
        for part in dotted_path.split("."):
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                return default
        return node

    def resolve_path(self, relative_path: str) -> Path:
        """
        Resolve a config-relative path to the correct location.

        Writable paths (data/, logs/, backups/) → APP_DATA_DIR
        Everything else               → PROJECT_ROOT (bundled)
        """
        WRITABLE_PREFIXES = ("data", "logs", "backups")
        parts = Path(relative_path).parts
        if parts and parts[0] in WRITABLE_PREFIXES:
            return APP_DATA_DIR / relative_path
        return PROJECT_ROOT / relative_path


# Shared singleton
settings = Settings()


def ensure_runtime_dirs() -> None:
    """Create data/, logs/, backups/ under APP_DATA_DIR if missing."""
    for rel_dir in ("data", "logs", "backups"):
        (APP_DATA_DIR / rel_dir).mkdir(parents=True, exist_ok=True)
