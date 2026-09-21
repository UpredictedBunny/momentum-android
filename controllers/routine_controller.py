from services.routine_service import RoutineService
from services.dashboard_service import DashboardService

class RoutineController:
    def __init__(self):
        self.service=RoutineService()
        self.dashboard_service=DashboardService()
    def items(self): self.service.ensure_default_items(); return self.service.get_today_routine()
    def toggle(self,item_id,current):
        new_state=self.service.toggle_item(item_id,current)
        xp=DashboardService.XP_PER_ROUTINE
        if new_state: self.dashboard_service.award_xp(xp)
        else: self.dashboard_service.remove_xp(xp)
        return new_state
