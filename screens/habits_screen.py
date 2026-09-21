"""
habits_screen.py
-----------------
Full Habit Tracker screen for Android.

- Today's completion progress bar
- Active / All habits toggle
- Each habit row: checkbox + name + 🔥streak badge
- Add habit dialog
- Deactivate / reactivate swipe actions replaced by icon buttons
"""

from __future__ import annotations

from kivy.app import App
from kivy.metrics import dp

from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from controllers.habit_controller import HabitController
from screens.base_screen import (
    StandardLayout, make_card, section_label, progress_row,
    show_dialog, COLORS, PAD
)


class HabitsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = HabitController()
        self._show_all = False
        self._add_dialog: MDDialog | None = None
        self._name_field: MDTextField | None = None
        self._build()

    # ------------------------------------------------------------------
    def _build(self) -> None:
        self._layout = StandardLayout(
            title="Habit Tracker",
            current_tab="habits",
            right_icons=[["plus", lambda x: self._open_add_dialog()]],
        )
        self.add_widget(self._layout)
        self._refresh()

    # ------------------------------------------------------------------
    def _refresh(self) -> None:
        ca = self._layout.content_area
        ca.clear_widgets()

        done, total = self.controller.get_today_completion()

        # Progress card
        prog_card = make_card(padding=16, size_hint_y=None, height=dp(80))
        prog_inner = MDBoxLayout(orientation="vertical", spacing=dp(6))
        prog_inner.add_widget(MDLabel(
            text=f"{done} of {total} habits completed today",
            font_style="Body1",
            theme_text_color="Custom",
            text_color=COLORS["text_primary"],
            size_hint_y=None, height=dp(26),
        ))
        prog_inner.add_widget(progress_row(done / total * 100 if total else 0, COLORS["secondary"]))
        prog_card.add_widget(prog_inner)
        ca.add_widget(prog_card)

        # Toggle: Active / All
        toggle_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48), spacing=dp(8))
        active_btn = MDRaisedButton(
            text="Active",
            md_bg_color=COLORS["accent"] if not self._show_all else COLORS["surface_alt"],
            on_release=lambda x: self._set_tab(False),
        )
        all_btn = MDRaisedButton(
            text="All Habits",
            md_bg_color=COLORS["accent"] if self._show_all else COLORS["surface_alt"],
            on_release=lambda x: self._set_tab(True),
        )
        toggle_row.add_widget(active_btn)
        toggle_row.add_widget(all_btn)
        ca.add_widget(toggle_row)

        # Habit list
        habits = (
            self.controller.get_all_habits_with_stats()
            if self._show_all
            else self.controller.get_habits_with_stats()
        )

        if not habits:
            empty = make_card(padding=20, size_hint_y=None, height=dp(100))
            empty.add_widget(MDLabel(
                text="No habits yet.\nTap + to add your first habit.",
                halign="center",
                theme_text_color="Custom",
                text_color=COLORS["text_secondary"],
            ))
            ca.add_widget(empty)
            return

        for h in habits:
            ca.add_widget(self._habit_row(h))

        ca.add_widget(MDBoxLayout(size_hint_y=None, height=dp(16)))

    # ------------------------------------------------------------------
    def _habit_row(self, h: dict):
        is_active = bool(h.get("is_active", 1))
        is_done = bool(h["is_completed"])
        streak = h.get("streak", 0)

        card = make_card(padding=12, size_hint_y=None, height=dp(64))
        row = MDBoxLayout(orientation="horizontal", spacing=dp(8))

        # Checkbox
        chk = MDCheckbox(
            active=is_done,
            disabled=not is_active,
            color_active=COLORS["secondary"],
            size_hint=(None, None), size=(dp(40), dp(40)),
        )
        hid, state = h["id"], is_done
        chk.bind(
            active=lambda w, val, _id=hid, _s=state: self._toggle_habit(_id, _s)
        )
        row.add_widget(chk)

        # Name
        name_lbl = MDLabel(
            text=h["name"],
            theme_text_color="Custom",
            text_color=COLORS["text_secondary"] if is_done else (
                COLORS["text_primary"] if is_active else COLORS["text_secondary"]
            ),
            size_hint_x=1,
        )
        row.add_widget(name_lbl)

        # Streak badge
        if streak > 0:
            row.add_widget(MDLabel(
                text=f"🔥{streak}",
                size_hint=(None, None), size=(dp(48), dp(40)),
                theme_text_color="Custom",
                text_color=COLORS["warning"],
                halign="center",
            ))

        # Deactivate / Reactivate button
        if is_active:
            action_btn = MDIconButton(
                icon="pause-circle-outline",
                theme_icon_color="Custom",
                icon_color=COLORS["text_secondary"],
                size_hint=(None, None), size=(dp(40), dp(40)),
                on_release=lambda x, _id=hid: self._deactivate(_id),
            )
        else:
            action_btn = MDIconButton(
                icon="play-circle-outline",
                theme_icon_color="Custom",
                icon_color=COLORS["secondary"],
                size_hint=(None, None), size=(dp(40), dp(40)),
                on_release=lambda x, _id=hid: self._reactivate(_id),
            )
        row.add_widget(action_btn)

        card.add_widget(row)
        return card

    # ------------------------------------------------------------------
    def _toggle_habit(self, habit_id: int, old_state: bool) -> None:
        self.controller.toggle_habit(habit_id, old_state)
        self._refresh()

    def _set_tab(self, show_all: bool) -> None:
        self._show_all = show_all
        self._refresh()

    def _deactivate(self, habit_id: int) -> None:
        self.controller.deactivate_habit(habit_id)
        self._refresh()

    def _reactivate(self, habit_id: int) -> None:
        self.controller.reactivate_habit(habit_id)
        self._refresh()

    # ------------------------------------------------------------------
    def _open_add_dialog(self) -> None:
        self._name_field = MDTextField(
            hint_text="Habit name",
            mode="rectangle",
        )
        self._add_dialog = MDDialog(
            title="Add Habit",
            type="custom",
            content_cls=self._name_field,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self._add_dialog.dismiss(),
                ),
                MDRaisedButton(
                    text="ADD",
                    on_release=lambda x: self._save_habit(),
                ),
            ],
        )
        self._add_dialog.open()

    def _save_habit(self) -> None:
        name = self._name_field.text.strip() if self._name_field else ""
        if not name:
            show_dialog("Invalid", "Please enter a habit name.")
            return
        ok = self.controller.add_habit(name)
        if ok:
            self._add_dialog.dismiss()
            self._refresh()
        else:
            show_dialog("Already exists", f'A habit named "{name}" already exists.')

    def on_enter(self) -> None:
        self._refresh()
