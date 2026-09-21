from services.study_service import StudyService

class StudyController:
    def __init__(self): self.service=StudyService()
    def stats(self): return self.service.get_today_stats()
    def add(self,category,hours): return self.service.add_log(category,hours)
    def recent(self): return self.service.get_recent()
