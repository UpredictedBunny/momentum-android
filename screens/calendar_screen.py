"""
calendar_screen.py
-------------------
Calendar screen: navigate days with ‹ › buttons, log mood / notes /
study-worked hours for any date. CalendarController unchanged from desktop.
"""

from __future__ import annotations

from datetime import date, timedelta

from kivy.metrics import dp

from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu

from controllers.calendar_controller import CalendarController
from screens.base_screen import (
    StandardLayout, make_card, section_label,
    show_dialog, COLORS, PAD
)

MOODS = ["", "great", "good", "okay", "bad"]
MOOD_EMOJI = {"great": "😄", "good": "🙂", "okay": "😐", "bad": "😞", "": "—"}


class CalendarScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = CalendarController()
        self._current = date.today()
        self._selected_mood = ""
        self._mood_label: MDLabel | None = None
        self._notes_field: MDTextField | None = None
        self._studied_field: MDTextField | None = None
        self._worked_field: MDTextField | None = None
        self._date_label: MDLabel | None = None
        self._mood_menu: MDDropdownMenu | None = None
        self._build()

    # ------------------------------------------------------------------
    def _build(self) -> None:
        self._layout = StandardLayout(
            title="Calendar",
            current_tab="menu",
        )
        self.add_widget(self._layout)
        ca = self._layout.content_area

        # Date navigation row
        nav_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(52), spacing=dp(8))
        nav_row.add_widget(MDIconButton(
            icon="chevron-left",
            theme_icon_color="Custom",
            icon_color=COLORS["accent"],
            size_hint=(None, None), size=(dp(48), dp(48)),
            on_release=lambda x: self._move(-1),
        ))
        self._date_label = MDLabel(
            text="",
            font_style="Body1",
            theme_text_color="Custom",
            text_color=COLORS["text_primary"],
            halign="center",
        )
        nav_row.add_widget(self._date_label)
        nav_row.add_widget(MDIconButton(
            icon="chevron-right",
            theme_icon_color="Custom",
            icon_color=COLORS["accent"],
            size_hint=(None, None), size=(dp(48), dp(48)),
            on_release=lambda x: self._move(1),
        ))
        ca.add_widget(nav_row)

        # Daily snapshot card
        snapshot_card = make_card(padding=16, size_hint_y=None)
        snap_inner = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(12), padding=[0, 0, 0, 8])
        snap_inner.bind(minimum_height=snap_inner.setter("height"))

        # Mood row
        mood_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48), spacing=dp(8))
        mood_row.add_widget(MDLabel(
            text="Mood:",
            theme_text_color="Custom",
            text_color=COLORS["text_secondary"],
            size_hint=(None, None), size=(dp(56), dp(48)),
        ))
        self._mood_label = MDLabel(
            text="—",
            theme_text_color="Custom",
            text_color=COLORS["text_primary"],
        )
        mood_row.add_widget(self._mood_label)
        mood_row.add_widget(MDFlatButton(
            text="Set Mood",
            on_release=self._open_mood_menu,
        ))
        snap_inner.add_widget(mood_row)

        # Notes
        self._notes_field = MDTextField(
            hint_text="Notes for this day…",
            mode="rectangle",
            multiline=True,
            size_hint_y=None,
            height=dp(120),
        )
        snap_inner.add_widget(self._notes_field)

        # Hours row
        hours_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(56), spacing=dp(8))
        self._studied_field = MDTextField(
            hint_text="Hours studied",
            mode="rectangle",
            input_filter="float",
            size_hint_x=1,
        )
        self._worked_field = MDTextField(
            hint_text="Hours worked",
            mode="rectangle",
            input_filter="float",
            size_hint_x=1,
        )
        hours_row.add_widget(self._studied_field)
        hours_row.add_widget(self._worked_field)
        snap_inner.add_widget(hours_row)

        # Save button
        snap_inner.add_widget(MDRaisedButton(
            text="Save Day",
            md_bg_color=COLORS["accent"],
            size_hint_y=None, height=dp(44),
            on_release=lambda x: self._save(),
        ))

        snapshot_card.add_widget(snap_inner)
        ca.add_widget(snapshot_card)
        ca.add_widget(MDBoxLayout(size_hint_y=None, height=dp(16)))

        self._load_day()

    # ------------------------------------------------------------------
    def _move(self, days: int) -> None:
        self._current += timedelta(days=days)
        self._load_day()

    def _load_day(self) -> None:
        if self._date_label:
            self._date_label.text = self._current.strftime("%A, %b %d, %Y")
        data = self.controller.get_day(self._current.isoformat())
        self._selected_mood = data.get("mood") or ""
        if self._mood_label:
            self._mood_label.text = MOOD_EMOJI.get(self._selected_mood, "—") + f" {self._selected_mood or 'Not set'}"
        if self._notes_field:
            self._notes_field.text = data.get("notes") or ""
        if self._studied_field:
            self._studied_field.text = str(data.get("hours_studied") or 0)
        if self._worked_field:
            self._worked_field.text = str(data.get("hours_worked") or 0)

    def _open_mood_menu(self, button) -> None:
        items = [
            {
                "text": f"{MOOD_EMOJI.get(m, '—')} {m.capitalize() if m else 'Not set'}",
                "on_release": (lambda x, m=m: self._pick_mood(m)),
            }
            for m in MOODS
        ]
        self._mood_menu = MDDropdownMenu(caller=button, items=items, width_mult=4)
        self._mood_menu.open()

    def _pick_mood(self, mood: str) -> None:
        if self._mood_menu:
            self._mood_menu.dismiss()
        self._selected_mood = mood
        if self._mood_label:
            self._mood_label.text = MOOD_EMOJI.get(mood, "—") + f" {mood or 'Not set'}"

    def _save(self) -> None:
        try:
            studied = float(self._studied_field.text or 0)
            worked = float(self._worked_field.text or 0)
        except (ValueError, TypeError):
            show_dialog("Invalid Input", "Study and work hours must be valid numbers.")
            return
        notes = self._notes_field.text.strip() if self._notes_field else ""
        ok = self.controller.save_day(
            self._current.isoformat(),
            self._selected_mood,
            notes,
            studied,
            worked,
        )
        if not ok:
            show_dialog("Invalid", "Hours cannot be negative.")
        else:
            show_dialog("Saved", f"Day saved for {self._current.strftime('%b %d')} ✓")

    def on_enter(self) -> None:
        self._load_day()
