"""
menu_screen.py
---------------
"More" hub screen — a grid of cards that navigate to secondary screens.
Replaces the desktop sidebar entries that don't fit in the bottom nav bar.
"""

from __future__ import annotations

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.gridlayout import GridLayout

from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard

from screens.base_screen import (
    StandardLayout, make_card, COLORS, PAD, RADIUS
)
from themes.theme import COLORS, RADIUS


# (icon_emoji, title, subtitle, screen_name)
MENU_ENTRIES = [
    ("📅", "Calendar",     "Daily notes & mood",      "calendar"),
    ("📚", "Study Tracker","Log your study hours",    "study"),
    ("📊", "Statistics",   "7-day productivity view", "statistics"),
    ("🎯", "Goals",        "Track what matters",      "goals"),
    ("⚙️", "Projects",    "Monitor progress",        "projects"),
    ("🎯", "Focus Mode",   "25-min deep work",        "focus"),
    ("🔧", "Settings",     "App info & backup",       "settings"),
]


class MenuScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build()

    # ------------------------------------------------------------------
    def _build(self) -> None:
        self._layout = StandardLayout(
            title="More",
            current_tab="menu",
        )
        self.add_widget(self._layout)
        ca = self._layout.content_area

        # Intro label
        ca.add_widget(MDLabel(
            text="All Features",
            font_style="H6",
            theme_text_color="Custom",
            text_color=COLORS["text_primary"],
            size_hint_y=None, height=dp(36),
        ))

        for icon, title, subtitle, screen_name in MENU_ENTRIES:
            ca.add_widget(self._menu_card(icon, title, subtitle, screen_name))

        ca.add_widget(MDBoxLayout(size_hint_y=None, height=dp(16)))

    # ------------------------------------------------------------------
    def _menu_card(self, icon: str, title: str, subtitle: str, screen_name: str):
        card = MDCard(
            md_bg_color=COLORS["surface"],
            radius=[dp(RADIUS)],
            padding=dp(16),
            line_color=COLORS["border"],
            line_width=1,
            size_hint_y=None,
            height=dp(76),
            ripple_behavior=True,
            on_release=lambda x, sn=screen_name: App.get_running_app().navigate(sn),
        )
        row = MDBoxLayout(orientation="horizontal", spacing=dp(16))

        # Emoji icon
        row.add_widget(MDLabel(
            text=icon,
            font_style="H5",
            size_hint=(None, None),
            size=(dp(48), dp(44)),
            halign="center",
        ))

        # Text column
        text_col = MDBoxLayout(orientation="vertical")
        text_col.add_widget(MDLabel(
            text=title,
            font_style="Body1",
            theme_text_color="Custom",
            text_color=COLORS["text_primary"],
            size_hint_y=None, height=dp(28),
        ))
        text_col.add_widget(MDLabel(
            text=subtitle,
            font_style="Caption",
            theme_text_color="Custom",
            text_color=COLORS["text_secondary"],
            size_hint_y=None, height=dp(22),
        ))
        row.add_widget(text_col)

        # Chevron
        row.add_widget(MDLabel(
            text="›",
            font_style="H5",
            theme_text_color="Custom",
            text_color=COLORS["text_secondary"],
            size_hint=(None, None), size=(dp(24), dp(44)),
            halign="center",
        ))

        card.add_widget(row)
        return card
