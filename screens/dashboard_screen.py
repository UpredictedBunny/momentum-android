"""
dashboard_screen.py
--------------------
Mobile dashboard: greeting, date, stat cards (XP/level/streak/pomodoro/
study), today's habits checklist, today's routine checklist, weekly
progress bars.

Data: DashboardController (unchanged from desktop).
"""

from __future__ import annotations

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout

from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.selectioncontrol import MDCheckbox

from controllers.dashboard_controller import DashboardController
from screens.base_screen import (
    StandardLayout, make_card, section_label, stat_card, progress_row,
    COLORS, PAD, FONT_SIZE
)
from themes.theme import COLORS, PAD


class DashboardScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = DashboardController()
        self._layout: StandardLayout | None = None
        self._build()

    # ------------------------------------------------------------------
    def _build(self) -> None:
        self._layout = StandardLayout(
            title="Momentum",
            current_tab="dashboard",
        )
        self.add_widget(self._layout)
        self._populate()

    def _populate(self) -> None:
        ca = self._layout.content_area
        ca.clear_widgets()
        try:
            summary = self.controller.get_summary()
        except Exception:
            ca.add_widget(MDLabel(text="Could not load dashboard.", halign="center"))
            return

        # ---- Header ----
        greeting_card = make_card(padding=20, size_hint_y=None, height=dp(90))
        inner = MDBoxLayout(orientation="vertical")
        inner.add_widget(MDLabel(
            text=f"{summary.greeting} 👋",
            font_style="H6",
            theme_text_color="Custom",
            text_color=COLORS["text_primary"],
        ))
        inner.add_widget(MDLabel(
            text=summary.date_str,
            font_style="Caption",
            theme_text_color="Custom",
            text_color=COLORS["text_secondary"],
        ))
        greeting_card.add_widget(inner)
        ca.add_widget(greeting_card)

        # ---- Stat cards row 1: XP / Level / Streak ----
        row1 = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(96), spacing=dp(8))
        row1.add_widget(stat_card(summary.xp_today, "XP Today", COLORS["accent"]))
        row1.add_widget(stat_card(f"Lv {summary.level}", "Level", COLORS["accent_alt"]))
        row1.add_widget(stat_card(f"🔥{summary.streak}", "Streak", COLORS["warning"]))
        ca.add_widget(row1)

        # ---- Stat cards row 2: Pomodoro / Focus / Study ----
        row2 = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(96), spacing=dp(8))
        row2.add_widget(stat_card(summary.pomodoro_sessions, "Pomodoros", COLORS["secondary"]))
        row2.add_widget(stat_card(f"{summary.focus_minutes}m", "Focus", COLORS["secondary"]))
        row2.add_widget(stat_card(f"{summary.study_hours:.1f}h", "Study", COLORS["accent_alt"]))
        ca.add_widget(row2)

        # ---- Habits summary ----
        ca.add_widget(section_label("Today's Habits"))
        habit_card = make_card(padding=16, size_hint_y=None)
        habit_inner = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4), padding=[0, 0, 0, 8])
        habit_inner.bind(minimum_height=habit_inner.setter("height"))

        h_done, h_total = summary.habits_completed, summary.habits_total
        habit_inner.add_widget(MDLabel(
            text=f"{h_done}/{h_total} completed",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=COLORS["text_secondary"],
            size_hint_y=None, height=dp(24),
        ))
        if h_total > 0:
            habit_inner.add_widget(progress_row(h_done / h_total * 100, COLORS["secondary"]))

        for h in summary.habits[:6]:  # show max 6 on dashboard
            row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(44))
            chk = MDCheckbox(
                active=bool(h["is_completed"]),
                color_active=COLORS["secondary"],
                size_hint=(None, None), size=(dp(40), dp(40)),
            )
            hid = h["id"]
            state = bool(h["is_completed"])
            chk.bind(active=lambda widget, val, _id=hid, _s=state: self._toggle_habit(_id, _s, widget, val))
            row.add_widget(chk)
            row.add_widget(MDLabel(
                text=h["name"],
                theme_text_color="Custom",
                text_color=COLORS["text_secondary"] if h["is_completed"] else COLORS["text_primary"],
                size_hint_y=None, height=dp(44),
            ))
            habit_inner.add_widget(row)

        if h_total > 6:
            habit_inner.add_widget(MDFlatButton(
                text=f"+ {h_total - 6} more — go to Habits",
                on_release=lambda x: App.get_running_app().navigate("habits"),
            ))

        habit_card.add_widget(habit_inner)
        ca.add_widget(habit_card)

        # ---- Routine summary ----
        ca.add_widget(section_label("Daily Routine"))
        routine_card = make_card(padding=16, size_hint_y=None)
        r_inner = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4), padding=[0, 0, 0, 8])
        r_inner.bind(minimum_height=r_inner.setter("height"))

        r_done, r_total = summary.routine_completed, summary.routine_total
        r_inner.add_widget(MDLabel(
            text=f"{r_done}/{r_total} completed",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=COLORS["text_secondary"],
            size_hint_y=None, height=dp(24),
        ))
        if r_total > 0:
            r_inner.add_widget(progress_row(r_done / r_total * 100, COLORS["accent"]))

        for item in summary.routine_items[:5]:
            rlabel = MDLabel(
                text=("✓ " if item["is_completed"] else "○ ") + item["name"],
                font_style="Body1",
                theme_text_color="Custom",
                text_color=COLORS["text_secondary"] if item["is_completed"] else COLORS["text_primary"],
                size_hint_y=None, height=dp(36),
            )
            r_inner.add_widget(rlabel)

        routine_card.add_widget(r_inner)
        ca.add_widget(routine_card)

        # ---- Weekly Progress ----
        ca.add_widget(section_label("Last 7 Days"))
        week_card = make_card(padding=16, size_hint_y=None)
        week_inner = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        week_inner.bind(minimum_height=week_inner.setter("height"))

        for day in summary.weekly_progress:
            day_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(28), spacing=dp(8))
            day_row.add_widget(MDLabel(
                text=day["label"],
                font_style="Caption",
                theme_text_color="Custom",
                text_color=COLORS["text_secondary"],
                size_hint=(None, None), size=(dp(32), dp(28)),
            ))
            pct = day["pct"] if day["total"] > 0 else 0
            bar = progress_row(pct, COLORS["secondary"])
            bar.size_hint_x = 1
            day_row.add_widget(bar)
            day_row.add_widget(MDLabel(
                text=f"{int(pct)}%",
                font_style="Caption",
                theme_text_color="Custom",
                text_color=COLORS["text_secondary"],
                size_hint=(None, None), size=(dp(36), dp(28)),
                halign="right",
            ))
            week_inner.add_widget(day_row)

        week_card.add_widget(week_inner)
        ca.add_widget(week_card)

        # Bottom spacer
        ca.add_widget(MDBoxLayout(size_hint_y=None, height=dp(16)))

    def _toggle_habit(self, habit_id: int, old_state: bool, widget, new_active: bool) -> None:
        try:
            self.controller.toggle_habit(habit_id, old_state)
        except Exception:
            pass

    def on_enter(self) -> None:
        """Refresh data every time the user navigates to this screen."""
        self._populate()
