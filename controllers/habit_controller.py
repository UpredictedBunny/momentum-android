"""
habit_controller.py
-------------------
Orchestrates HabitService operations and awards / removes XP via
DashboardService when a habit completion changes.  All DB access goes
through the service layer — no SQL here.
"""

from __future__ import annotations

from services.dashboard_service import DashboardService
from services.habit_service import HabitService
from utils.logger import get_logger

log = get_logger("controllers.habit_controller")


class HabitController:
    def __init__(self) -> None:
        self.habit_svc = HabitService()
        self.dashboard_svc = DashboardService()

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------
    def get_habits_with_stats(self) -> list[dict]:
        """Active habits for today, each enriched with current streak."""
        habits = self.habit_svc.get_today_habits()
        return [
            {**h, "streak": self.habit_svc.get_habit_streak(h["id"]), "is_active": 1}
            for h in habits
        ]

    def get_all_habits_with_stats(self) -> list[dict]:
        """All habits (active + inactive) with today completion and streak.
        Inactive habits always show streak=0 (streak is meaningless if paused).
        """
        habits = self.habit_svc.get_all_habits()
        return [
            {
                **h,
                "streak": (
                    self.habit_svc.get_habit_streak(h["id"]) if h["is_active"] else 0
                ),
            }
            for h in habits
        ]

    def get_today_completion(self) -> tuple[int, int]:
        """Returns (completed_count, total_active_count) for today."""
        return self.habit_svc.get_today_completion()

    # ------------------------------------------------------------------
    # Toggle
    # ------------------------------------------------------------------
    def toggle_habit(self, habit_id: int, current_state: bool) -> bool:
        """Toggle completion, award or remove XP. Returns new state."""
        from config.settings import settings

        new_state = self.habit_svc.toggle_habit(habit_id, current_state)
        xp = settings.gamification.xp_per_habit
        if new_state:
            self.dashboard_svc.award_xp(xp)
        else:
            self.dashboard_svc.remove_xp(xp)
        log.info("Habit %d toggled → %s (XP %s%d)", habit_id, new_state,
                 "+" if new_state else "-", xp)
        return new_state

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    def add_habit(self, name: str) -> bool:
        """Add a new active habit. Returns True on success."""
        return self.habit_svc.add_habit(name)

    def deactivate_habit(self, habit_id: int) -> None:
        """Mark a habit inactive (soft delete)."""
        self.habit_svc.deactivate_habit(habit_id)

    def reactivate_habit(self, habit_id: int) -> None:
        """Restore a previously deactivated habit."""
        self.habit_svc.reactivate_habit(habit_id)
