"""
base_screen.py
--------------
Shared base for every Momentum Android screen.

Provides:
  - StandardLayout: BoxLayout root with optional TopAppBar + BottomNavBar
  - BottomNavBar:   5-button bottom navigation widget
  - show_dialog():  reusable MDDialog helper
  - show_confirm(): destructive-action confirmation
  - make_card():    surface card with Momentum styling
  - section_label(): small uppercase section header
"""

from __future__ import annotations
from typing import Callable

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Rectangle

from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.progressbar import MDProgressBar

from themes.theme import COLORS, PAD, FONT_SIZE, RADIUS

# -----------------------------------------------------------------------
# Navigation items: (icon, screen_name, label)
# -----------------------------------------------------------------------
BOTTOM_NAV_ITEMS = [
    ("home",        "dashboard", "Home"),
    ("checkbox-marked-circle", "habits",    "Habits"),
    ("weather-sunny", "routine",   "Routine"),
    ("timer",       "pomodoro",  "Pomodoro"),
    ("dots-grid",   "menu",      "More"),
]


# -----------------------------------------------------------------------
# BottomNavBar
# -----------------------------------------------------------------------
class BottomNavBar(MDBoxLayout):
    """
    Persistent bottom navigation bar.
    current: page key of the active screen (highlights the correct icon).
    """

    def __init__(self, current: str = "dashboard", **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(60)
        self.md_bg_color = COLORS["surface"]

        for icon, screen_name, label in BOTTOM_NAV_ITEMS:
            is_active = (screen_name == current)
            col = COLORS["accent"] if is_active else COLORS["text_secondary"]
            btn = MDIconButton(
                icon=icon,
                theme_icon_color="Custom",
                icon_color=col,
                size_hint=(1, None),
                height=dp(60),
                on_release=lambda _, sn=screen_name: App.get_running_app().navigate(sn),
            )
            self.add_widget(btn)


# -----------------------------------------------------------------------
# StandardLayout — wraps content + top bar + bottom bar
# -----------------------------------------------------------------------
class StandardLayout(MDBoxLayout):
    """
    Root layout for a screen.
    Usage:
        layout = StandardLayout(
            title="Habit Tracker",
            current_tab="habits",
            right_icons=[("cog", lambda: ...)],
        )
        # add content to layout.content_area (a BoxLayout, orientation="vertical")
    """

    def __init__(
        self,
        title: str = "Momentum",
        current_tab: str = "dashboard",
        right_icons: list | None = None,
        **kwargs,
    ):
        super().__init__(orientation="vertical", **kwargs)
        self.md_bg_color = COLORS["background"]

        # Top app bar
        right = right_icons or []
        self.toolbar = MDTopAppBar(
            title=title,
            md_bg_color=COLORS["surface"],
            specific_text_color=COLORS["text_primary"],
            right_action_items=right,
        )
        self.add_widget(self.toolbar)

        # Scrollable content area
        self.scroll = ScrollView()
        self.content_area = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=[dp(PAD["md"]), dp(PAD["sm"])],
            spacing=dp(PAD["sm"]),
        )
        self.content_area.bind(minimum_height=self.content_area.setter("height"))
        self.scroll.add_widget(self.content_area)
        self.add_widget(self.scroll)

        # Bottom nav
        self.add_widget(BottomNavBar(current=current_tab))


# -----------------------------------------------------------------------
# Card helper
# -----------------------------------------------------------------------
def make_card(padding: int = 16, **kwargs) -> MDCard:
    card = MDCard(
        md_bg_color=COLORS["surface"],
        radius=[dp(RADIUS)],
        padding=dp(padding),
        line_color=COLORS["border"],
        line_width=1,
        **kwargs,
    )
    return card


# -----------------------------------------------------------------------
# Section label (small caps above a group of widgets)
# -----------------------------------------------------------------------
def section_label(text: str) -> MDLabel:
    return MDLabel(
        text=text.upper(),
        font_style="Caption",
        theme_text_color="Custom",
        text_color=COLORS["text_secondary"],
        size_hint_y=None,
        height=dp(28),
    )


# -----------------------------------------------------------------------
# Dialog helpers
# -----------------------------------------------------------------------
def show_dialog(title: str, text: str, ok_text: str = "OK") -> None:
    """Simple informational dialog."""
    d = MDDialog(
        title=title,
        text=text,
        buttons=[MDFlatButton(text=ok_text, on_release=lambda x: d.dismiss())],
    )
    d.open()


def show_confirm(
    title: str,
    text: str,
    on_confirm: Callable,
    confirm_text: str = "CONFIRM",
    cancel_text: str = "CANCEL",
) -> None:
    """Destructive confirmation dialog."""
    d = MDDialog(
        title=title,
        text=text,
        buttons=[
            MDFlatButton(
                text=cancel_text,
                on_release=lambda x: d.dismiss(),
            ),
            MDRaisedButton(
                text=confirm_text,
                md_bg_color=COLORS["danger"],
                on_release=lambda x: (d.dismiss(), on_confirm()),
            ),
        ],
    )
    d.open()


# -----------------------------------------------------------------------
# Stat card (number above label)
# -----------------------------------------------------------------------
def stat_card(value: str, label: str, color: list | None = None) -> MDCard:
    col = color or COLORS["accent"]
    card = make_card(padding=16, size_hint=(1, None), height=dp(90))
    inner = MDBoxLayout(orientation="vertical")
    inner.add_widget(MDLabel(
        text=str(value),
        font_style="H5",
        theme_text_color="Custom",
        text_color=col,
        halign="center",
    ))
    inner.add_widget(MDLabel(
        text=label,
        font_style="Caption",
        theme_text_color="Custom",
        text_color=COLORS["text_secondary"],
        halign="center",
    ))
    card.add_widget(inner)
    return card


# -----------------------------------------------------------------------
# Progress bar row helper
# -----------------------------------------------------------------------
def progress_row(value: float, color: list | None = None) -> MDProgressBar:
    bar = MDProgressBar(
        value=value,
        color=color or COLORS["accent"],
        size_hint_y=None,
        height=dp(6),
    )
    return bar
