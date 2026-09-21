"""
routine_screen.py
------------------
Daily Routine screen: checklist of today's items with period/priority,
completion toggle, add-item dialog. Uses RoutineController unchanged.
"""

from __future__ import annotations

from kivy.metrics import dp

from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu

from controllers.routine_controller import RoutineController
from screens.base_screen import (
    StandardLayout, make_card, section_label, progress_row,
    show_dialog, COLORS, PAD
)


PERIODS = ["morning", "afternoon", "evening", "night"]
PRIORITIES = ["low", "medium", "high"]

PERIOD_ICON = {
    "morning":   "weather-sunny",
    "afternoon": "weather-partly-cloudy",
    "evening":   "weather-sunset",
    "night":     "weather-night",
}


class RoutineScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = RoutineController()
        self._add_dialog: MDDialog | None = None
        self._name_field: MDTextField | None = None
        self._mins_field: MDTextField | None = None
        self._selected_period = "morning"
        self._selected_priority = "medium"
        self._build()

    # ------------------------------------------------------------------
    def _build(self) -> None:
        self._layout = StandardLayout(
            title="Daily Routine",
            current_tab="routine",
            right_icons=[["plus", lambda x: self._open_add_dialog()]],
        )
        self.add_widget(self._layout)
        self._refresh()

    # ------------------------------------------------------------------
    def _refresh(self) -> None:
        ca = self._layout.content_area
        ca.clear_widgets()

        items = self.controller.items()
        done = sum(1 for i in items if i["is_completed"])
        total = len(items)

        # Progress card
        prog_card = make_card(padding=16, size_hint_y=None, height=dp(80))
        prog_inner = MDBoxLayout(orientation="vertical", spacing=dp(6))
        prog_inner.add_widget(MDLabel(
            text=f"{done} of {total} completed today",
            font_style="Body1",
            theme_text_color="Custom",
            text_color=COLORS["text_primary"],
            size_hint_y=None, height=dp(26),
        ))
        prog_inner.add_widget(progress_row(done / total * 100 if total else 0, COLORS["accent"]))
        prog_card.add_widget(prog_inner)
        ca.add_widget(prog_card)

        if not items:
            empty = make_card(padding=20, size_hint_y=None, height=dp(100))
            empty.add_widget(MDLabel(
                text="No routine items.\nTap + to add your first item.",
                halign="center",
                theme_text_color="Custom",
                text_color=COLORS["text_secondary"],
            ))
            ca.add_widget(empty)
            return

        # Group by period for readability
        periods_seen = []
        items_by_period: dict[str, list] = {}
        for item in items:
            p = item["period"]
            if p not in items_by_period:
                items_by_period[p] = []
                periods_seen.append(p)
            items_by_period[p].append(item)

        for period in periods_seen:
            ca.add_widget(section_label(period))
            for item in items_by_period[period]:
                ca.add_widget(self._item_row(item))

        ca.add_widget(MDBoxLayout(size_hint_y=None, height=dp(16)))

    # ------------------------------------------------------------------
    def _item_row(self, item: dict):
        is_done = bool(item["is_completed"])
        card = make_card(padding=12, size_hint_y=None, height=dp(72))
        row = MDBoxLayout(orientation="horizontal", spacing=dp(8))

        chk = MDCheckbox(
            active=is_done,
            color_active=COLORS["accent"],
            size_hint=(None, None), size=(dp(40), dp(44)),
        )
        iid, state = item["id"], is_done
        chk.bind(active=lambda w, val, _id=iid, _s=state: self._toggle(_id, _s))
        row.add_widget(chk)

        info_col = MDBoxLayout(orientation="vertical", size_hint_x=1)
        info_col.add_widget(MDLabel(
            text=item["name"],
            font_style="Body1",
            theme_text_color="Custom",
            text_color=COLORS["text_secondary"] if is_done else COLORS["text_primary"],
            size_hint_y=None, height=dp(28),
        ))
        meta = f'{item["est_minutes"]} min  ·  {item["priority"]}'
        info_col.add_widget(MDLabel(
            text=meta,
            font_style="Caption",
            theme_text_color="Custom",
            text_color=COLORS["text_secondary"],
            size_hint_y=None, height=dp(20),
        ))
        row.add_widget(info_col)

        # Completion checkmark
        if is_done:
            row.add_widget(MDLabel(
                text="✓",
                size_hint=(None, None), size=(dp(32), dp(44)),
                theme_text_color="Custom",
                text_color=COLORS["secondary"],
                halign="center",
            ))

        card.add_widget(row)
        return card

    # ------------------------------------------------------------------
    def _toggle(self, item_id: int, old_state: bool) -> None:
        self.controller.toggle(item_id, old_state)
        self._refresh()

    # ------------------------------------------------------------------
    def _open_add_dialog(self) -> None:
        self._name_field = MDTextField(hint_text="Item name", mode="rectangle")
        self._mins_field = MDTextField(
            hint_text="Estimated minutes",
            mode="rectangle",
            input_filter="int",
        )
        # Period button (acts as dropdown trigger)
        self._period_label = MDLabel(
            text=f"Period: {self._selected_period}",
            theme_text_color="Custom",
            text_color=COLORS["text_secondary"],
            size_hint_y=None, height=dp(36),
        )
        self._priority_label = MDLabel(
            text=f"Priority: {self._selected_priority}",
            theme_text_color="Custom",
            text_color=COLORS["text_secondary"],
            size_hint_y=None, height=dp(36),
        )

        content = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(220), spacing=dp(8))
        content.add_widget(self._name_field)
        content.add_widget(self._mins_field)

        # Period selector
        period_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(44))
        period_row.add_widget(self._period_label)
        period_btn = MDFlatButton(
            text="Change",
            on_release=self._open_period_menu,
        )
        period_row.add_widget(period_btn)
        content.add_widget(period_row)

        # Priority selector
        priority_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(44))
        priority_row.add_widget(self._priority_label)
        priority_btn = MDFlatButton(
            text="Change",
            on_release=self._open_priority_menu,
        )
        priority_row.add_widget(priority_btn)
        content.add_widget(priority_row)

        self._add_dialog = MDDialog(
            title="Add Routine Item",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self._add_dialog.dismiss()),
                MDRaisedButton(text="ADD", on_release=lambda x: self._save_item()),
            ],
        )
        self._add_dialog.open()

    def _open_period_menu(self, button) -> None:
        items = [
            {
                "text": p.capitalize(),
                "on_release": (lambda x, p=p: self._pick_period(p)),
            }
            for p in PERIODS
        ]
        MDDropdownMenu(caller=button, items=items, width_mult=3).open()

    def _pick_period(self, period: str) -> None:
        self._selected_period = period
        if self._period_label:
            self._period_label.text = f"Period: {period}"

    def _open_priority_menu(self, button) -> None:
        items = [
            {
                "text": p.capitalize(),
                "on_release": (lambda x, p=p: self._pick_priority(p)),
            }
            for p in PRIORITIES
        ]
        MDDropdownMenu(caller=button, items=items, width_mult=3).open()

    def _pick_priority(self, priority: str) -> None:
        self._selected_priority = priority
        if self._priority_label:
            self._priority_label.text = f"Priority: {priority}"

    def _save_item(self) -> None:
        name = self._name_field.text.strip() if self._name_field else ""
        mins = self._mins_field.text.strip() if self._mins_field else "0"
        if not name:
            show_dialog("Invalid", "Please enter an item name.")
            return
        ok = self.controller.service.add_item(
            name, self._selected_period, mins or 0, self._selected_priority
        )
        if ok:
            self._add_dialog.dismiss()
            self._refresh()
        else:
            show_dialog("Invalid", "Check name and minutes are valid.")

    def on_enter(self) -> None:
        self._refresh()
