from database.db_manager import get_db

class ProjectsController:
    def __init__(self): self.db=get_db()
    def all(self): return [dict(r) for r in self.db.fetch_all("SELECT * FROM projects ORDER BY id DESC")]
    def add(self,name,deadline,link,notes):
        name=name.strip();
        if not name:return False
        self.db.execute("INSERT INTO projects(name,progress_pct,deadline,github_link,notes) VALUES(?,0,?,?,?)",(name,deadline or None,link.strip(),notes.strip())); return True
    def update_progress(self,pid,p):
        try:
            value = max(0, min(100, float(p)))
        except (TypeError, ValueError):
            return False
        self.db.execute("UPDATE projects SET progress_pct=? WHERE id=?",(value,pid))
        return True
