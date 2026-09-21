"""
dashboard_service.py
--------------------
Aggregates data from other services into a single DashboardSummary.
Also handles XP read/write and weekly overview.
"""

from __future__ import annotations

from datetime import date, timedelta
from dataclasses import dataclass, field

from config.settings import settings
from database.db_manager import get_db
from services.habit_service import HabitService
from services.routine_service import RoutineService
from services.pomodoro_service import PomodoroService
from services.study_service import StudyService
from utils.logger import get_logger

log = get_logger("services.dashboard_service")


@dataclass
class DashboardSummary:
    greeting: str = ""
    date_str: str = ""
    habits_completed: int = 0
    habits_total: int = 0
    routine_completed: int = 0
    routine_total: int = 0
    xp_today: int = 0
    xp_total: int = 0
    level: int = 1
    streak: int = 0
    pomodoro_sessions: int = 0
    focus_minutes: int = 0
    study_hours: float = 0.0
    habits: list[dict] = field(default_factory=list)
    routine_items: list[dict] = field(default_factory=list)
    weekly_progress: list[dict] = field(default_factory=list)


class DashboardService:
    XP_PER_HABIT = None
    XP_PER_ROUTINE = 5

    def __init__(self) -> None:
        self.db = get_db()
        self.habit_svc = HabitService()
        self.routine_svc = RoutineService()
        self.pomodoro_svc = PomodoroService()
        self.study_svc = StudyService()
        self.XP_PER_HABIT = settings.gamification.xp_per_habit

    # ------------------------------------------------------------------
    # Seed defaults so dashboard isn't empty on first run
    # ------------------------------------------------------------------
    def seed_defaults(self) -> None:
        self.habit_svc.ensure_default_habits()
        self.routine_svc.ensure_default_items()

    # ------------------------------------------------------------------
    # Build full summary
    # ------------------------------------------------------------------
    def get_summary(self) -> DashboardSummary:
        try:
            today = date.today()
            summary = DashboardSummary()
            summary.date_str = today.strftime("%A, %B %d, %Y")
            summary.greeting = self._greeting()

            # Habits
            summary.habits = self.habit_svc.get_today_habits()
            summary.habits_completed, summary.habits_total = (
                self.habit_svc.get_today_completion()
            )

            # Routine
            summary.routine_items = self.routine_svc.get_today_routine()
            summary.routine_completed, summary.routine_total = (
                self.routine_svc.get_today_completion()
            )

            # Streak
            summary.streak = self.habit_svc.get_best_overall_streak()

            # Pomodoro
            pomo = self.pomodoro_svc.get_today_stats()
            summary.pomodoro_sessions = pomo["sessions"]
            summary.focus_minutes = pomo["focus_minutes"]

            # Study
            study = self.study_svc.get_today_stats()
            summary.study_hours = study["total_hours"]

            # XP
            gstate = self._get_gamification_state()
            summary.xp_total = gstate["xp"]
            summary.level = gstate["level"]
            summary.xp_today = self._calculate_today_xp(
                summary.habits_completed,
                summary.routine_completed,
                summary.pomodoro_sessions,
            )

            # Weekly
            summary.weekly_progress = self._weekly_progress()

            return summary
        except Exception:
            log.exception("Error building dashboard summary")
            return DashboardSummary(
                greeting="Good day",
                date_str=date.today().strftime("%A, %B %d, %Y"),
            )

    # ------------------------------------------------------------------
    # XP helpers
    # ------------------------------------------------------------------
    def _calculate_today_xp(
        self, habits_done: int, routine_done: int, pomodoros: int
    ) -> int:
        xp_habit = settings.gamification.xp_per_habit
        xp_pomo = settings.gamification.xp_per_pomodoro
        return habits_done * xp_habit + routine_done * self.XP_PER_ROUTINE + pomodoros * xp_pomo

    def award_xp(self, amount: int) -> None:
        """Add XP and update level."""
        self.db.execute(
            "UPDATE gamification_state SET xp = xp + ? WHERE id = 1", (amount,)
        )
        self._recalculate_level()

    def remove_xp(self, amount: int) -> None:
        self.db.execute(
            "UPDATE gamification_state SET xp = MAX(0, xp - ?) WHERE id = 1", (amount,)
        )
        self._recalculate_level()

    def _recalculate_level(self) -> None:
        row = self.db.fetch_one("SELECT xp FROM gamification_state WHERE id = 1")
        if not row:
            return
        xp = row["xp"]
        level_curve = settings.gamification.level_xp_curve
        level = max(1, xp // level_curve + 1)
        self.db.execute(
            "UPDATE gamification_state SET level = ? WHERE id = 1", (level,)
        )

    def _get_gamification_state(self) -> dict:
        row = self.db.fetch_one("SELECT xp, level, coins FROM gamification_state WHERE id = 1")
        if row:
            return dict(row)
        return {"xp": 0, "level": 1, "coins": 0}

    # ------------------------------------------------------------------
    # Weekly progress (habit completion % for last 7 days)
    # ------------------------------------------------------------------
    def _weekly_progress(self) -> list[dict]:
        today = date.today()
        # Use count of active habits as the denominator so % is always out of
        # the full set, not just whichever habits happen to have a log entry.
        total_row = self.db.fetch_one(
            "SELECT COUNT(*) AS n FROM habits WHERE is_active = 1"
        )
        total_habits = total_row["n"] if total_row else 0

        result = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_str = day.isoformat()
            row = self.db.fetch_one(
                """
                SELECT COALESCE(SUM(is_completed), 0) AS completed
                FROM habit_logs
                WHERE log_date = ?
                """,
                (day_str,),
            )
            completed = row["completed"] if row is not None else 0
            pct = (completed / total_habits * 100) if total_habits > 0 else 0
            result.append({
                "date": day_str,
                "label": day.strftime("%a"),
                "completed": int(completed),
                "total": total_habits,
                "pct": pct,
            })
        return result

    # ------------------------------------------------------------------
    # Greeting
    # ------------------------------------------------------------------
    @staticmethod
    def _greeting() -> str:
        from datetime import datetime
        hour = datetime.now().hour
        if hour < 12:
            return "Good morning"
        elif hour < 17:
            return "Good afternoon"
        elif hour < 21:
            return "Good evening"
        return "Good night"
