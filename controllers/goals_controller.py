from database.db_manager import get_db

class GoalsController:
    def __init__(self): self.db=get_db()
    def all(self): return [dict(r) for r in self.db.fetch_all("SELECT * FROM goals WHERE is_active=1 ORDER BY id DESC")]
    def add(self,name,deadline):
        name=name.strip();
        if not name:return False
        self.db.execute("INSERT INTO goals(name,progress_pct,deadline,is_active) VALUES(?,0,?,1)",(name,deadline or None)); return True
    def update_progress(self,gid,p):
        try:
            value = max(0, min(100, float(p)))
        except (TypeError, ValueError):
            return False
        self.db.execute("UPDATE goals SET progress_pct=? WHERE id=?",(value,gid))
        return True
    def deactivate(self,gid): self.db.execute("UPDATE goals SET is_active=0 WHERE id=?",(gid,))
