"""
routine_service.py
------------------
Business logic for daily routine items and their completion logs.
"""

from __future__ import annotations

from datetime import date

from database.db_manager import get_db
from utils.logger import get_logger

log = get_logger("services.routine_service")


class RoutineService:
    def __init__(self) -> None:
        self.db = get_db()

    # ------------------------------------------------------------------
    # Seed default routine items from config if table is empty
    # ------------------------------------------------------------------
    def ensure_default_items(self) -> None:
        from config.settings import settings
        # Seed only when the table has never had routine items. Re-seeding when
        # all items are inactive would create duplicate default rows.
        existing = self.db.fetch_all("SELECT id FROM routine_items LIMIT 1")
        if not existing:
            for i, name in enumerate(settings.routine.morning_items):
                self.db.execute(
                    """
                    INSERT OR IGNORE INTO routine_items
                        (name, period, est_minutes, priority, sort_order, is_active)
                    VALUES (?, 'morning', 30, 'medium', ?, 1)
                    """,
                    (name, i),
                )
            log.info("Seeded default routine items from config.")

    # ------------------------------------------------------------------
    # Today's routine with completion state
    # ------------------------------------------------------------------
    def get_today_routine(self) -> list[dict]:
        today = date.today().isoformat()
        rows = self.db.fetch_all(
            """
            SELECT ri.id, ri.name, ri.period, ri.est_minutes, ri.priority, ri.sort_order,
                   COALESCE(rl.is_completed, 0) AS is_completed,
                   rl.completed_at
            FROM routine_items ri
            LEFT JOIN routine_logs rl
                   ON rl.routine_item_id = ri.id AND rl.log_date = ?
            WHERE ri.is_active = 1
            ORDER BY ri.sort_order, ri.id
            """,
            (today,),
        )
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Completion toggle
    # ------------------------------------------------------------------
    def complete_item(self, item_id: int) -> None:
        today = date.today().isoformat()
        from datetime import datetime
        now = datetime.now().isoformat(timespec="seconds")
        self.db.execute(
            """
            INSERT INTO routine_logs (routine_item_id, log_date, is_completed, completed_at)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(routine_item_id, log_date)
            DO UPDATE SET is_completed = 1, completed_at = excluded.completed_at
            """,
            (item_id, today, now),
        )
        log.info("Routine item %d marked complete for %s", item_id, today)

    def uncomplete_item(self, item_id: int) -> None:
        today = date.today().isoformat()
        self.db.execute(
            """
            INSERT INTO routine_logs (routine_item_id, log_date, is_completed)
            VALUES (?, ?, 0)
            ON CONFLICT(routine_item_id, log_date)
            DO UPDATE SET is_completed = 0, completed_at = NULL
            """,
            (item_id, today),
        )
        log.info("Routine item %d marked incomplete for %s", item_id, today)

    def toggle_item(self, item_id: int, current_state: bool) -> bool:
        if current_state:
            self.uncomplete_item(item_id)
            return False
        else:
            self.complete_item(item_id)
            return True

    # ------------------------------------------------------------------
    # Completion count
    # ------------------------------------------------------------------
    def get_today_completion(self) -> tuple[int, int]:
        items = self.get_today_routine()
        total = len(items)
        completed = sum(1 for it in items if it["is_completed"])
        return completed, total

    def add_item(self, name, period="morning", est_minutes=0, priority="medium"):
        name = name.strip()
        if not name:
            return False
        try:
            minutes = int(est_minutes)
        except (TypeError, ValueError):
            return False
        if minutes < 0 or period not in {"morning", "afternoon", "evening", "night"}:
            return False
        if priority not in {"low", "medium", "high"}:
            return False
        self.db.execute(
            "INSERT INTO routine_items(name,period,est_minutes,priority,sort_order,is_active) VALUES(?,?,?,?,?,1)",
            (name, period, minutes, priority, 9999),
        )
        return True

    def deactivate_item(self,item_id): self.db.execute("UPDATE routine_items SET is_active=0 WHERE id=?",(item_id,))
