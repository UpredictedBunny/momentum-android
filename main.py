"""
main.py  —  Momentum Android v1.0.0
-------------------------------------
Entry point for the Kivy/KivyMD Android application.

Run for development:
    python main.py

Build APK:
    buildozer android debug
    buildozer android release   (requires keystore)

The frozen Windows v1.0.0 source is NOT modified by this project.
This file is Android-only and lives in a separate project tree.
"""

from __future__ import annotations

import os

# Suppress Kivy's default environment probing noise before imports
os.environ.setdefault("KIVY_NO_ENV_CONFIG", "1")

# -----------------------------------------------------------------------
# Runtime-dir bootstrap & DB init must happen before any widget creation
# -----------------------------------------------------------------------
from config.settings import ensure_runtime_dirs
from database.db_manager import get_db
from utils.logger import get_logger

# -----------------------------------------------------------------------
# Kivy / KivyMD imports
# -----------------------------------------------------------------------
from kivy.config import Config

# Portrait-first on mobile, resizable window on desktop dev
Config.set("graphics", "width", "400")
Config.set("graphics", "height", "800")
Config.set("kivy", "keyboard_mode", "systemanddock")

from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivymd.app import MDApp

from themes.theme import apply_theme
from screens.dashboard_screen import DashboardScreen
from screens.habits_screen import HabitsScreen
from screens.routine_screen import RoutineScreen
from screens.pomodoro_screen import PomodoroScreen
from screens.focus_screen import FocusScreen
from screens.calendar_screen import CalendarScreen
from screens.study_screen import StudyScreen
from screens.statistics_screen import StatisticsScreen
from screens.goals_screen import GoalsScreen
from screens.projects_screen import ProjectsScreen
from screens.settings_screen import SettingsScreen
from screens.menu_screen import MenuScreen

log = get_logger("main")


class MomentumApp(MDApp):
    """Root application class."""

    # Current page key — screens can read this to know which nav icon to highlight
    current_screen_name: str = "dashboard"

    def build(self):
        # ---- Application setup ----
        ensure_runtime_dirs()
        get_db()           # opens SQLite + applies schema.sql on first run
        apply_theme(self)  # KivyMD dark palette

        self.title = "Momentum"
        self.icon = ""   # replace with path to .png icon asset when available

        # ---- Screen manager ----
        self.sm = ScreenManager(transition=FadeTransition(duration=0.12))

        self.sm.add_widget(DashboardScreen(name="dashboard"))
        self.sm.add_widget(HabitsScreen(name="habits"))
        self.sm.add_widget(RoutineScreen(name="routine"))
        self.sm.add_widget(PomodoroScreen(name="pomodoro"))
        self.sm.add_widget(FocusScreen(name="focus"))
        self.sm.add_widget(CalendarScreen(name="calendar"))
        self.sm.add_widget(StudyScreen(name="study"))
        self.sm.add_widget(StatisticsScreen(name="statistics"))
        self.sm.add_widget(GoalsScreen(name="goals"))
        self.sm.add_widget(ProjectsScreen(name="projects"))
        self.sm.add_widget(SettingsScreen(name="settings"))
        self.sm.add_widget(MenuScreen(name="menu"))

        log.info("Momentum Android v1.0.0 starting up.")
        return self.sm

    # ------------------------------------------------------------------
    def navigate(self, screen_name: str) -> None:
        """
        Navigate to a named screen.  Called by BottomNavBar buttons and
        MenuScreen cards.  Triggers on_enter() on the target screen so
        data refreshes every visit.
        """
        if not self.sm.has_screen(screen_name):
            log.warning("Unknown screen: %s", screen_name)
            return

        self.current_screen_name = screen_name
        self.sm.current = screen_name
        log.info("Navigated to: %s", screen_name)

    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # Android lifecycle — REQUIRED to prevent the OS from force-quitting
    # the app every time the user switches away from it.
    def on_pause(self):
        """Called when Android suspends the app (home button, incoming call, etc.)"""
        log.info("App paused — Android lifecycle.")
        return True   # returning True tells Android: keep this app in memory

    def on_resume(self):
        """Called when Android brings the app back to the foreground."""
        log.info("App resumed — Android lifecycle.")

    # ------------------------------------------------------------------
    def on_stop(self):
        try:
            from database.db_manager import get_db
            get_db().close()
        except Exception:
            pass
        log.info("Momentum Android shut down cleanly.")


if __name__ == "__main__":
    MomentumApp().run()
