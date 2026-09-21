"""
pomodoro_service.py
-------------------
Statistics queries for Pomodoro sessions.
"""

from __future__ import annotations

from datetime import date

from database.db_manager import get_db
from utils.logger import get_logger

log = get_logger("services.pomodoro_service")


class PomodoroService:
    def __init__(self) -> None:
        self.db = get_db()

    def get_today_stats(self) -> dict:
        today = date.today().isoformat()
        row = self.db.fetch_one(
            """
            SELECT COUNT(*) AS sessions,
                   COALESCE(SUM(focus_minutes), 0) AS focus_minutes
            FROM pomodoro_sessions
            WHERE session_date = ?
            """,
            (today,),
        )
        if row:
            return {"sessions": row["sessions"], "focus_minutes": row["focus_minutes"]}
        return {"sessions": 0, "focus_minutes": 0}

    def record_session(self, preset_name, focus_minutes, break_minutes):
        from datetime import datetime
        self.db.execute("INSERT INTO pomodoro_sessions(session_date,preset_name,focus_minutes,break_minutes,completed_at) VALUES(?,?,?,?,?)",(date.today().isoformat(),preset_name,int(focus_minutes),int(break_minutes),datetime.now().isoformat(timespec="seconds")))

    def get_recent(self, limit=10):
        return [dict(r) for r in self.db.fetch_all("SELECT * FROM pomodoro_sessions ORDER BY id DESC LIMIT ?",(limit,))]
