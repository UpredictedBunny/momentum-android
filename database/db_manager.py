"""
db_manager.py  (Android-adapted)
----------------------------------
Identical to the desktop DatabaseManager but uses settings.resolve_path()
which now routes writable paths (data/) to Android private storage.

All SQL queries, schema init, backup, and the singleton pattern are
preserved exactly as in the frozen Windows v1.0.0 release.
"""

from __future__ import annotations

import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from config.settings import settings, PROJECT_ROOT
from utils.logger import get_logger

log = get_logger("database.db_manager")

# schema.sql is bundled inside the APK as a read-only asset
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


class DatabaseManager:
    """Thin wrapper around sqlite3 with schema init, queries, and backups."""

    _instance: "DatabaseManager | None" = None

    def __new__(cls) -> "DatabaseManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connect()
            cls._instance._initialize_schema()
        return cls._instance

    # ------------------------------------------------------------------
    def _connect(self) -> None:
        db_path = settings.resolve_path(settings.database.path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON;")
        log.info("Connected to database at %s", db_path)

    def _initialize_schema(self) -> None:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            self._conn.executescript(f.read())
        self._conn.commit()
        log.info("Schema initialized/verified.")

    # ------------------------------------------------------------------
    def execute(self, query: str, params: Iterable[Any] = ()) -> sqlite3.Cursor:
        cur = self._conn.cursor()
        cur.execute(query, params)
        self._conn.commit()
        return cur

    def executemany(self, query: str, seq_of_params: Iterable[Iterable[Any]]) -> None:
        cur = self._conn.cursor()
        cur.executemany(query, seq_of_params)
        self._conn.commit()

    def fetch_one(self, query: str, params: Iterable[Any] = ()) -> sqlite3.Row | None:
        cur = self._conn.cursor()
        cur.execute(query, params)
        return cur.fetchone()

    def fetch_all(self, query: str, params: Iterable[Any] = ()) -> list[sqlite3.Row]:
        cur = self._conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()

    # ------------------------------------------------------------------
    def backup_now(self) -> Path:
        """Copy the live .db file to backups/ with a timestamp suffix."""
        db_path = settings.resolve_path(settings.database.path)
        backup_dir = settings.resolve_path(settings.database.backup_dir)
        backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        dest = backup_dir / f"momentum_{stamp}.db"
        shutil.copy2(str(db_path), str(dest))
        log.info("Backup created at %s", dest)
        return dest

    def close(self) -> None:
        self._conn.close()
        log.info("Database connection closed.")


def get_db() -> DatabaseManager:
    return DatabaseManager()
