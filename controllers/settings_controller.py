"""
settings_controller.py  (Android-adapted)
-------------------------------------------
Identical interface to the desktop version, but info() returns the
Android-safe storage path rather than a Windows filesystem path.
"""

from database.db_manager import get_db
from config.settings import settings, APP_DATA_DIR


class SettingsController:
    def backup(self) -> str:
        dest = get_db().backup_now()
        return str(dest)

    def info(self) -> dict:
        db_path = settings.resolve_path(settings.database.path)
        return {
            "name": settings.app.name,
            "version": settings.app.version,
            "database": str(db_path),
            "data_dir": str(APP_DATA_DIR),
        }
