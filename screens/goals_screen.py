"""
goals_screen.py
----------------
Goals screen: list active goals with progress sliders, add-goal dialog,
deactivate button. GoalsController is reused unchanged from desktop.
"""

from __future__ import annotations

from kivy.metrics import dp

from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.slider import MDSlider
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField

from controllers.goals_controller import GoalsController
from screens.base_screen import (
    StandardLayout, make_card, section_label,
    show_dialog, COLORS, PAD
)


class GoalsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = GoalsController()
        self._add_dialog: MDDialog | None = None
        self._name_field: MDTextField | None = None
        self._deadline_field: MDTextField | None = None
        self._build()

    # ------------------------------------------------------------------
    def _build(self) -> None:
        self._layout = StandardLayout(
            title="Goals",
            current_tab="menu",
            right_icons=[["plus", lambda x: self._open_add_dialog()]],
        )
        self.add_widget(self._layout)
        self._refresh()

    # ------------------------------------------------------------------
    def _refresh(self) -> None:
        ca = self._layout.content_area
        ca.clear_widgets()
        goals = self.controller.all()

        if not goals:
            empty = make_card(padding=24, size_hint_y=None, height=dp(110))
            empty.add_widget(MDLabel(
                text="No goals yet.\n\nTap + to set your first goal.",
                halign="center",
                theme_text_color="Custom",
                text_color=COLORS["text_secondary"],
            ))
            ca.add_widget(empty)
        else:
            for g in goals:
                ca.add_widget(self._goal_card(g))

        ca.add_widget(MDBoxLayout(size_hint_y=None, height=dp(16)))

    # ------------------------------------------------------------------
    def _goal_card(self, g: dict):
        pct = float(g["progress_pct"])
        card = make_card(padding=16, size_hint_y=None)
        inner = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8), padding=[0, 0, 0, 4])
        inner.bind(minimum_height=inner.setter("height"))

        # Name row
        name_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(36))
        name_row.add_widget(MDLabel(
            text=g["name"],
            font_style="Body1",
            theme_text_color="Custom",
            text_color=COLORS["text_primary"],
        ))
        name_row.add_widget(MDIconButton(
            icon="trash-can-outline",
            theme_icon_color="Custom",
            icon_color=COLORS["danger"],
            size_hint=(None, None), size=(dp(40), dp(36)),
            on_release=lambda x, gid=g["id"]: self._deactivate(gid),
        ))
        inner.add_widget(name_row)

        # Meta: progress% + deadline
        deadline_str = g["deadline"] or "No deadline"
        pct_label = MDLabel(
            text=f"{pct:.0f}%  ·  {deadline_str}",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=COLORS["text_secondary"],
            size_hint_y=None, height=dp(22),
        )
        inner.add_widget(pct_label)

        # Slider
        slider = MDSlider(
            min=0,
            max=100,
            value=pct,
            color=COLORS["accent"],
            size_hint_y=None, height=dp(40),
        )

        # Use a debounce-style commit: update label immediately, commit on release
        def on_value(widget, value, _id=g["id"], _lbl=pct_label, _dl=deadline_str):
            _lbl.text = f"{value:.0f}%  ·  {_dl}"

        def on_release(widget, _id=g["id"]):
            try:
                self.controller.update_progress(_id, widget.value)
            except Exception:
                pass

        slider.bind(value=on_value)
        slider.bind(on_touch_up=lambda w, touch: on_release(w) if w.collide_point(*touch.pos) else None)
        inner.add_widget(slider)

        card.add_widget(inner)
        return card

    # ------------------------------------------------------------------
    def _deactivate(self, goal_id: int) -> None:
        self.controller.deactivate(goal_id)
        self._refresh()

    # ------------------------------------------------------------------
    def _open_add_dialog(self) -> None:
        self._name_field = MDTextField(hint_text="Goal name", mode="rectangle")
        self._deadline_field = MDTextField(
            hint_text="Deadline YYYY-MM-DD (optional)",
            mode="rectangle",
        )
        content = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(140), spacing=dp(10))
        content.add_widget(self._name_field)
        content.add_widget(self._deadline_field)

        self._add_dialog = MDDialog(
            title="Add Goal",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self._add_dialog.dismiss()),
                MDRaisedButton(text="ADD", on_release=lambda x: self._save_goal()),
            ],
        )
        self._add_dialog.open()

    def _save_goal(self) -> None:
        name = self._name_field.text.strip() if self._name_field else ""
        deadline = self._deadline_field.text.strip() if self._deadline_field else ""
        if not name:
            show_dialog("Invalid", "Please enter a goal name.")
            return
        ok = self.controller.add(name, deadline or None)
        if ok:
            self._add_dialog.dismiss()
            self._refresh()
        else:
            show_dialog("Invalid", "Enter a valid goal name.")

    def on_enter(self) -> None:
        self._refresh()
