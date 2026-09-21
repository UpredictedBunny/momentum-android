"""
statistics_screen.py
---------------------
Statistics screen: today's headline numbers as cards, then a 7-day
table with inline progress bars — no Matplotlib required on mobile.

The StatisticsController is reused unchanged. Chart rendering uses
Kivy Canvas primitives for a lightweight native feel.
"""

from __future__ import annotations

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle

from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton

from controllers.statistics_controller import StatisticsController
from screens.base_screen import (
    StandardLayout, make_card, section_label, stat_card, progress_row,
    COLORS, PAD
)


class StatisticsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = StatisticsController()
        self._build()

    # ------------------------------------------------------------------
    def _build(self) -> None:
        self._layout = StandardLayout(
            title="Statistics",
            current_tab="menu",
            right_icons=[["refresh", lambda x: self.on_enter()]],
        )
        self.add_widget(self._layout)
        self._refresh()

    # ------------------------------------------------------------------
    def _refresh(self) -> None:
        ca = self._layout.content_area
        ca.clear_widgets()

        # Today stats
        ca.add_widget(section_label("Today"))
        try:
            s = self.controller.summary()
        except Exception:
            ca.add_widget(MDLabel(text="Could not load statistics.", halign="center"))
            return

        row1 = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(96), spacing=dp(8))
        row1.add_widget(stat_card(s["habit_done"], "Habits Done", COLORS["secondary"]))
        row1.add_widget(stat_card(s["pomodoros"], "Pomodoros", COLORS["accent"]))
        ca.add_widget(row1)

        row2 = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(96), spacing=dp(8))
        row2.add_widget(stat_card(f"{s['focus_minutes']}m", "Focus Time", COLORS["accent"]))
        row2.add_widget(stat_card(f"{s['study_hours']:.1f}h", "Study Hours", COLORS["accent_alt"]))
        ca.add_widget(row2)

        # 7-day history
        ca.add_widget(section_label("Last 7 Days"))
        weekly = self.controller.weekly()  # [(date_str, habits_done, study_hours), ...]

        # Determine max values for normalising progress bars
        max_habits = max((h for _, h, _ in weekly), default=1) or 1
        max_study = max((sh for _, _, sh in weekly), default=0.1) or 0.1

        for day_str, habits, study in weekly:
            card = make_card(padding=12, size_hint_y=None, height=dp(80))
            inner = MDBoxLayout(orientation="vertical", spacing=dp(4))

            # Date label
            inner.add_widget(MDLabel(
                text=day_str,
                font_style="Caption",
                theme_text_color="Custom",
                text_color=COLORS["text_secondary"],
                size_hint_y=None, height=dp(20),
            ))

            # Habits bar
            h_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(20), spacing=dp(6))
            h_row.add_widget(MDLabel(
                text=f"✓ {habits}",
                font_style="Caption",
                theme_text_color="Custom",
                text_color=COLORS["secondary"],
                size_hint=(None, None), size=(dp(40), dp(20)),
            ))
            h_row.add_widget(progress_row(habits / max_habits * 100, COLORS["secondary"]))
            inner.add_widget(h_row)

            # Study bar
            s_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(20), spacing=dp(6))
            s_row.add_widget(MDLabel(
                text=f"📚 {study:.1f}h",
                font_style="Caption",
                theme_text_color="Custom",
                text_color=COLORS["accent_alt"],
                size_hint=(None, None), size=(dp(52), dp(20)),
            ))
            s_row.add_widget(progress_row(study / max_study * 100, COLORS["accent_alt"]))
            inner.add_widget(s_row)

            card.add_widget(inner)
            ca.add_widget(card)

        ca.add_widget(MDBoxLayout(size_hint_y=None, height=dp(16)))

    def on_enter(self) -> None:
        self._refresh()
