"""
study_service.py
----------------
Statistics queries for study logs.
"""

from __future__ import annotations

from datetime import date

from database.db_manager import get_db
from utils.logger import get_logger

log = get_logger("services.study_service")


class StudyService:
    def __init__(self) -> None:
        self.db = get_db()

    def get_today_stats(self) -> dict:
        today = date.today().isoformat()
        row = self.db.fetch_one(
            """
            SELECT COALESCE(SUM(hours), 0) AS total_hours
            FROM study_logs
            WHERE log_date = ?
            """,
            (today,),
        )
        total = row["total_hours"] if row else 0.0
        return {"total_hours": total}

    def add_log(self, category, hours):
        try: hours=float(hours)
        except (TypeError,ValueError): return False
        if hours <= 0 or not category.strip(): return False
        self.db.execute("INSERT INTO study_logs(log_date,category,hours) VALUES(?,?,?)",(date.today().isoformat(),category.strip(),hours)); return True

    def get_recent(self, limit=10):
        return [dict(r) for r in self.db.fetch_all("SELECT * FROM study_logs ORDER BY rowid DESC LIMIT ?",(limit,))]
