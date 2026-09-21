"""
study_screen.py
----------------
Study Tracker: log hours by category (University / Freelancing / AI /
Reading), see today's total, browse recent logs.
"""

from __future__ import annotations

from kivy.metrics import dp

from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu

from controllers.study_controller import StudyController
from screens.base_screen import (
    StandardLayout, make_card, section_label,
    show_dialog, stat_card, COLORS, PAD
)

CATEGORIES = ["University", "Freelancing", "AI", "Reading"]
CAT_ICON = {
    "University": "📚",
    "Freelancing": "💼",
    "AI": "🤖",
    "Reading": "📖",
}


class StudyScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = StudyController()
        self._selected_category = "University"
        self._cat_label: MDLabel | None = None
        self._hours_field: MDTextField | None = None
        self._cat_menu: MDDropdownMenu | None = None
        self._build()

    # ------------------------------------------------------------------
    def _build(self) -> None:
        self._layout = StandardLayout(
            title="Study Tracker",
            current_tab="menu",
        )
        self.add_widget(self._layout)
        ca = self._layout.content_area

        # Summary stat
        stats = self.controller.stats()
        total_today = stats.get("total_hours", 0)
        today_card = stat_card(f"{total_today:.2f}h", "Studied Today", COLORS["accent_alt"])
        ca.add_widget(today_card)

        # Log entry card
        log_card = make_card(padding=16, size_hint_y=None, height=dp(180))
        log_inner = MDBoxLayout(orientation="vertical", spacing=dp(10))

        # Category selector
        cat_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48), spacing=dp(8))
        cat_row.add_widget(MDLabel(
            text="Category:",
            theme_text_color="Custom",
            text_color=COLORS["text_secondary"],
            size_hint=(None, None), size=(dp(80), dp(40)),
        ))
        self._cat_label = MDLabel(
            text=f"{CAT_ICON['University']} University",
            theme_text_color="Custom",
            text_color=COLORS["text_primary"],
        )
        cat_row.add_widget(self._cat_label)
        cat_row.add_widget(MDFlatButton(
            text="Change",
            on_release=self._open_cat_menu,
        ))
        log_inner.add_widget(cat_row)

        # Hours field
        self._hours_field = MDTextField(
            hint_text="Hours (e.g. 1.5)",
            mode="rectangle",
            input_filter="float",
            size_hint_y=None, height=dp(56),
        )
        log_inner.add_widget(self._hours_field)

        log_inner.add_widget(MDRaisedButton(
            text="Log Study Session",
            md_bg_color=COLORS["accent_alt"],
            size_hint_y=None, height=dp(44),
            on_release=lambda x: self._add_log(),
        ))

        log_card.add_widget(log_inner)
        ca.add_widget(log_card)

        # Recent logs
        ca.add_widget(section_label("Recent Sessions"))
        self._recent_area = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        self._recent_area.bind(minimum_height=self._recent_area.setter("height"))
        ca.add_widget(self._recent_area)

        self._populate_recent()
        ca.add_widget(MDBoxLayout(size_hint_y=None, height=dp(16)))

    # ------------------------------------------------------------------
    def _open_cat_menu(self, button) -> None:
        items = [
            {
                "text": f"{CAT_ICON[c]} {c}",
                "on_release": (lambda x, c=c: self._pick_cat(c)),
            }
            for c in CATEGORIES
        ]
        self._cat_menu = MDDropdownMenu(caller=button, items=items, width_mult=4)
        self._cat_menu.open()

    def _pick_cat(self, category: str) -> None:
        if self._cat_menu:
            self._cat_menu.dismiss()
        self._selected_category = category
        if self._cat_label:
            self._cat_label.text = f"{CAT_ICON[category]} {category}"

    def _add_log(self) -> None:
        hours_txt = self._hours_field.text.strip() if self._hours_field else ""
        if not hours_txt:
            show_dialog("Missing Hours", "Enter the number of hours studied.")
            return
        ok = self.controller.add(self._selected_category, hours_txt)
        if ok:
            if self._hours_field:
                self._hours_field.text = ""
            self._refresh_summary()
            self._populate_recent()
        else:
            show_dialog("Invalid", "Enter a positive number of hours.")

    def _refresh_summary(self) -> None:
        # Rebuild stats card (first child of content_area) in-place — simpler: rebuild screen
        self.on_enter()

    def _populate_recent(self) -> None:
        self._recent_area.clear_widgets()
        recent = self.controller.recent()
        if not recent:
            self._recent_area.add_widget(MDLabel(
                text="No study sessions logged yet.",
                theme_text_color="Custom",
                text_color=COLORS["text_secondary"],
                size_hint_y=None, height=dp(40),
                halign="center",
            ))
            return
        for r in recent:
            card = make_card(padding=12, size_hint_y=None, height=dp(52))
            row = MDBoxLayout(orientation="horizontal", spacing=dp(8))
            icon = CAT_ICON.get(r["category"], "📖")
            row.add_widget(MDLabel(
                text=f"{icon} {r['category']}",
                theme_text_color="Custom",
                text_color=COLORS["text_primary"],
                size_hint_x=1,
            ))
            row.add_widget(MDLabel(
                text=f"{float(r['hours']):.2f}h",
                theme_text_color="Custom",
                text_color=COLORS["accent_alt"],
                size_hint=(None, None), size=(dp(56), dp(40)),
                halign="right",
            ))
            row.add_widget(MDLabel(
                text=r["log_date"],
                font_style="Caption",
                theme_text_color="Custom",
                text_color=COLORS["text_secondary"],
                size_hint=(None, None), size=(dp(88), dp(40)),
                halign="right",
            ))
            card.add_widget(row)
            self._recent_area.add_widget(card)

    def on_enter(self) -> None:
        # Rebuild the whole screen to update the stat card
        self._layout.content_area.clear_widgets()
        ca = self._layout.content_area

        stats = self.controller.stats()
        total_today = stats.get("total_hours", 0)
        ca.add_widget(stat_card(f"{total_today:.2f}h", "Studied Today", COLORS["accent_alt"]))

        log_card = make_card(padding=16, size_hint_y=None, height=dp(180))
        log_inner = MDBoxLayout(orientation="vertical", spacing=dp(10))

        cat_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48), spacing=dp(8))
        cat_row.add_widget(MDLabel(text="Category:", theme_text_color="Custom",
                                   text_color=COLORS["text_secondary"],
                                   size_hint=(None, None), size=(dp(80), dp(40))))
        self._cat_label = MDLabel(
            text=f"{CAT_ICON[self._selected_category]} {self._selected_category}",
            theme_text_color="Custom", text_color=COLORS["text_primary"])
        cat_row.add_widget(self._cat_label)
        cat_row.add_widget(MDFlatButton(text="Change", on_release=self._open_cat_menu))
        log_inner.add_widget(cat_row)

        self._hours_field = MDTextField(
            hint_text="Hours (e.g. 1.5)", mode="rectangle",
            input_filter="float", size_hint_y=None, height=dp(56))
        log_inner.add_widget(self._hours_field)
        log_inner.add_widget(MDRaisedButton(
            text="Log Study Session", md_bg_color=COLORS["accent_alt"],
            size_hint_y=None, height=dp(44), on_release=lambda x: self._add_log()))
        log_card.add_widget(log_inner)
        ca.add_widget(log_card)

        ca.add_widget(section_label("Recent Sessions"))
        self._recent_area = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        self._recent_area.bind(minimum_height=self._recent_area.setter("height"))
        ca.add_widget(self._recent_area)
        self._populate_recent()
        ca.add_widget(MDBoxLayout(size_hint_y=None, height=dp(16)))
