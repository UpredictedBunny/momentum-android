from database.db_manager import get_db
from datetime import date,timedelta

class StatisticsController:
    def __init__(self): self.db=get_db()
    def summary(self):
        h=self.db.fetch_one("SELECT COUNT(*) total, COALESCE(SUM(is_completed),0) done FROM habit_logs WHERE log_date=?",(date.today().isoformat(),))
        p=self.db.fetch_one("SELECT COUNT(*) sessions,COALESCE(SUM(focus_minutes),0) minutes FROM pomodoro_sessions WHERE session_date=?",(date.today().isoformat(),))
        s=self.db.fetch_one("SELECT COALESCE(SUM(hours),0) hours FROM study_logs WHERE log_date=?",(date.today().isoformat(),))
        return {"habit_logs":h["total"] if h else 0,"habit_done":h["done"] if h else 0,"pomodoros":p["sessions"] if p else 0,"focus_minutes":p["minutes"] if p else 0,"study_hours":s["hours"] if s else 0}
    def weekly(self):
        out=[]
        for i in range(6,-1,-1):
            d=(date.today()-timedelta(days=i)).isoformat()
            h=self.db.fetch_one("SELECT COALESCE(SUM(is_completed),0) done FROM habit_logs WHERE log_date=?",(d,))
            s=self.db.fetch_one("SELECT COALESCE(SUM(hours),0) hours FROM study_logs WHERE log_date=?",(d,))
            out.append((d,h["done"] if h else 0,s["hours"] if s else 0))
        return out
