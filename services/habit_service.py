"""
habit_service.py
----------------
Business logic for habits: today's list, completion toggle, streaks.
"""

from __future__ import annotations

from datetime import date, timedelta

from database.db_manager import get_db
from utils.logger import get_logger

log = get_logger("services.habit_service")


class HabitService:
    def __init__(self) -> None:
        self.db = get_db()

    # ------------------------------------------------------------------
    # Seed default habits from config if table is empty
    # ------------------------------------------------------------------
    def ensure_default_habits(self) -> None:
        from config.settings import settings
        existing = self.db.fetch_all("SELECT id FROM habits WHERE is_active = 1")
        if not existing:
            for name in settings.habits:
                self.db.execute(
                    "INSERT OR IGNORE INTO habits (name, icon, is_active) VALUES (?, '', 1)",
                    (name,),
                )
            log.info("Seeded default habits from config.")

    # ------------------------------------------------------------------
    # Today's habits with completion state
    # ------------------------------------------------------------------
    def get_today_habits(self) -> list[dict]:
        today = date.today().isoformat()
        rows = self.db.fetch_all(
            """
            SELECT h.id, h.name, h.icon,
                   COALESCE(hl.is_completed, 0) AS is_completed
            FROM habits h
            LEFT JOIN habit_logs hl
                   ON hl.habit_id = h.id AND hl.log_date = ?
            WHERE h.is_active = 1
            ORDER BY h.id
            """,
            (today,),
        )
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Toggle completion
    # ------------------------------------------------------------------
    def complete_habit(self, habit_id: int) -> None:
        today = date.today().isoformat()
        self.db.execute(
            """
            INSERT INTO habit_logs (habit_id, log_date, is_completed)
            VALUES (?, ?, 1)
            ON CONFLICT(habit_id, log_date) DO UPDATE SET is_completed = 1
            """,
            (habit_id, today),
        )
        log.info("Habit %d marked complete for %s", habit_id, today)

    def uncomplete_habit(self, habit_id: int) -> None:
        today = date.today().isoformat()
        self.db.execute(
            """
            INSERT INTO habit_logs (habit_id, log_date, is_completed)
            VALUES (?, ?, 0)
            ON CONFLICT(habit_id, log_date) DO UPDATE SET is_completed = 0
            """,
            (habit_id, today),
        )
        log.info("Habit %d marked incomplete for %s", habit_id, today)

    def toggle_habit(self, habit_id: int, current_state: bool) -> bool:
        if current_state:
            self.uncomplete_habit(habit_id)
            return False
        else:
            self.complete_habit(habit_id)
            return True

    # ------------------------------------------------------------------
    # Completion counts
    # ------------------------------------------------------------------
    def get_today_completion(self) -> tuple[int, int]:
        """Returns (completed, total) for today."""
        habits = self.get_today_habits()
        total = len(habits)
        completed = sum(1 for h in habits if h["is_completed"])
        return completed, total

    # ------------------------------------------------------------------
    # Streaks — longest consecutive streak ending today (or yesterday)
    # ------------------------------------------------------------------
    def get_habit_streak(self, habit_id: int) -> int:
        """Return consecutive days this habit was completed up to today."""
        rows = self.db.fetch_all(
            """
            SELECT log_date FROM habit_logs
            WHERE habit_id = ? AND is_completed = 1
            ORDER BY log_date DESC
            """,
            (habit_id,),
        )
        if not rows:
            return 0

        dates = [date.fromisoformat(r["log_date"]) for r in rows]
        today = date.today()
        # Must be completed today or yesterday to have an active streak
        if dates[0] < today - timedelta(days=1):
            return 0

        streak = 0
        check = dates[0]
        for d in dates:
            if d == check:
                streak += 1
                check -= timedelta(days=1)
            else:
                break
        return streak

    def get_best_overall_streak(self) -> int:
        """Max streak across all active habits today."""
        rows = self.db.fetch_all("SELECT id FROM habits WHERE is_active = 1")
        if not rows:
            return 0
        return max(self.get_habit_streak(r["id"]) for r in rows)

    # ------------------------------------------------------------------
    # CRUD — called from HabitController only
    # ------------------------------------------------------------------
    def get_all_habits(self) -> list[dict]:
        """All habits (active + inactive) with today's completion state."""
        today = date.today().isoformat()
        rows = self.db.fetch_all(
            """
            SELECT h.id, h.name, h.icon, h.is_active,
                   COALESCE(hl.is_completed, 0) AS is_completed
            FROM habits h
            LEFT JOIN habit_logs hl
                   ON hl.habit_id = h.id AND hl.log_date = ?
            ORDER BY h.is_active DESC, h.id
            """,
            (today,),
        )
        return [dict(r) for r in rows]

    def add_habit(self, name: str) -> bool:
        """Insert a new active habit. Returns False if name is blank or already exists."""
        name = name.strip()
        if not name:
            return False
        try:
            self.db.execute(
                "INSERT INTO habits (name, icon, is_active) VALUES (?, '', 1)",
                (name,),
            )
            log.info("Added new habit: %s", name)
            return True
        except Exception:
            log.warning("Could not add habit %r (duplicate or DB error)", name)
            return False

    def deactivate_habit(self, habit_id: int) -> None:
        self.db.execute("UPDATE habits SET is_active = 0 WHERE id = ?", (habit_id,))
        log.info("Habit %d deactivated", habit_id)

    def reactivate_habit(self, habit_id: int) -> None:
        self.db.execute("UPDATE habits SET is_active = 1 WHERE id = ?", (habit_id,))
        log.info("Habit %d reactivated", habit_id)
