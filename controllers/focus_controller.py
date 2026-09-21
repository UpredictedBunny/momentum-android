from services.pomodoro_service import PomodoroService
from services.dashboard_service import DashboardService
from config.settings import settings

class FocusController:
    def __init__(self):
        self.service = PomodoroService()
        self.dashboard_service = DashboardService()
    def record(self,focus,break_minutes):
        self.service.record_session("Focus Mode",focus,break_minutes)
        self.dashboard_service.award_xp(settings.gamification.xp_per_pomodoro)
