from services.pomodoro_service import PomodoroService
from services.dashboard_service import DashboardService
from config.settings import settings

class PomodoroController:
    def __init__(self):
        self.service = PomodoroService()
        self.dashboard_service = DashboardService()
    def stats(self): return self.service.get_today_stats()
    def record(self,name,focus,break_minutes):
        self.service.record_session(name,focus,break_minutes)
        self.dashboard_service.award_xp(settings.gamification.xp_per_pomodoro)
