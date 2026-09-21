from database.db_manager import get_db

class CalendarController:
    def __init__(self): self.db=get_db()
    def get_day(self,d):
        r=self.db.fetch_one("SELECT * FROM calendar_days WHERE log_date=?",(d,)); return dict(r) if r else {"log_date":d,"mood":"","notes":"","hours_studied":0,"hours_worked":0}
    def save_day(self,d,mood,notes,studied,worked):
        try:
            studied = float(studied)
            worked = float(worked)
        except (TypeError, ValueError):
            return False
        if studied < 0 or worked < 0:
            return False
        self.db.execute(
            """INSERT INTO calendar_days(log_date,mood,notes,hours_studied,hours_worked)
               VALUES(?,?,?,?,?)
               ON CONFLICT(log_date) DO UPDATE SET
                 mood=excluded.mood,
                 notes=excluded.notes,
                 hours_studied=excluded.hours_studied,
                 hours_worked=excluded.hours_worked""",
            (d, mood, notes, studied, worked),
        )
        return True
