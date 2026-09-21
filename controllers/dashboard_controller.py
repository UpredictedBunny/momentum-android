"""
dashboard_controller.py
-----------------------
Sits between DashboardView and the service layer.
All business logic stays in the services; this just orchestrates calls.
"""

from __future__ import annotations

from services.dashboard_service import DashboardService, DashboardSummary
from services.habit_service import HabitService
from services.routine_service import RoutineService
from config.settings import settings
from utils.logger import get_logger

log = get_logger("controllers.dashboard_controller")


class DashboardController:
    def __init__(self) -> None:
        self.dashboard_svc = DashboardService()
        self.habit_svc = HabitService()
        self.routine_svc = RoutineService()
        # Seed defaults on first run so dashboard isn't empty
        self.dashboard_svc.seed_defaults()

    def get_summary(self) -> DashboardSummary:
        return self.dashboard_svc.get_summary()

    def toggle_habit(self, habit_id: int, current_state: bool) -> bool:
        """Toggle habit, award/remove XP, return new state."""
        new_state = self.habit_svc.toggle_habit(habit_id, current_state)
        xp = settings.gamification.xp_per_habit
        if new_state:
            self.dashboard_svc.award_xp(xp)
            log.info("Awarded %d XP for habit %d", xp, habit_id)
        else:
            self.dashboard_svc.remove_xp(xp)
            log.info("Removed %d XP for habit %d", xp, habit_id)
        return new_state

    def toggle_routine_item(self, item_id: int, current_state: bool) -> bool:
        """Toggle routine item, award/remove XP, return new state."""
        new_state = self.routine_svc.toggle_item(item_id, current_state)
        xp = DashboardService.XP_PER_ROUTINE
        if new_state:
            self.dashboard_svc.award_xp(xp)
        else:
            self.dashboard_svc.remove_xp(xp)
        return new_state
