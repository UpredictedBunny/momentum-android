"""
base_model.py
-------------
Every table in the app gets a corresponding Model class (RoutineItem,
Habit, Goal, Project, ...). They all inherit from BaseModel, which
holds the shared DatabaseManager reference and common helpers.

This keeps feature modules "dumb" -- a HabitController just calls
Habit.get_all() or Habit.create(...) without knowing any SQL.
"""

from __future__ import annotations

from database.db_manager import get_db
from utils.logger import get_logger


class BaseModel:
    """Common base class for all data models. Not meant to be instantiated directly."""

    table_name: str = ""  # overridden by each subclass

    def __init__(self) -> None:
        self.db = get_db()
        self.log = get_logger(f"models.{self.__class__.__name__}")

    def _row_to_dict(self, row) -> dict:
        """Convert a sqlite3.Row into a plain dict (rows aren't JSON-serializable)."""
        return dict(row) if row is not None else {}
