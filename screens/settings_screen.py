"""
settings_screen.py
-------------------
Settings screen: app version, Android storage path, create backup button.
Uses SettingsController (Android-adapted version).
"""

from __future__ import annotations

from kivy.metrics import dp

from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout

from controllers.settings_controller import SettingsController
from screens.base_screen import (
    StandardLayout, make_card, section_label,
    show_dialog, COLORS, PAD
)


class SettingsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = SettingsController()
        self._build()

    # ------------------------------------------------------------------
    def _build(self) -> None:
        self._layout = StandardLayout(
            title="Settings",
            current_tab="menu",
        )
        self.add_widget(self._layout)
        ca = self._layout.content_area
        info = self.controller.info()

        # App info card
        ca.add_widget(section_label("Application"))
        app_card = make_card(padding=20, size_hint_y=None)
        app_inner = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        app_inner.bind(minimum_height=app_inner.setter("height"))

        for label, value in [
            ("Name", info["name"]),
            ("Version", info["version"]),
            ("Platform", "Android"),
        ]:
            row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(32))
            row.add_widget(MDLabel(
                text=label,
                font_style="Caption",
                theme_text_color="Custom",
                text_color=COLORS["text_secondary"],
                size_hint=(None, None), size=(dp(80), dp(32)),
            ))
            row.add_widget(MDLabel(
                text=value,
                font_style="Body1",
                theme_text_color="Custom",
                text_color=COLORS["text_primary"],
            ))
            app_inner.add_widget(row)

        app_card.add_widget(app_inner)
        ca.add_widget(app_card)

        # Storage card
        ca.add_widget(section_label("Storage"))
        storage_card = make_card(padding=20, size_hint_y=None)
        storage_inner = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8))
        storage_inner.bind(minimum_height=storage_inner.setter("height"))

        storage_inner.add_widget(MDLabel(
            text="Data directory",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=COLORS["text_secondary"],
            size_hint_y=None, height=dp(22),
        ))
        storage_inner.add_widget(MDLabel(
            text=info.get("data_dir", "—"),
            font_style="Caption",
            theme_text_color="Custom",
            text_color=COLORS["text_primary"],
            size_hint_y=None, height=dp(28),
        ))
        storage_inner.add_widget(MDLabel(
            text="Database file",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=COLORS["text_secondary"],
            size_hint_y=None, height=dp(22),
        ))
        storage_inner.add_widget(MDLabel(
            text=info.get("database", "—"),
            font_style="Caption",
            theme_text_color="Custom",
            text_color=COLORS["text_primary"],
            size_hint_y=None, height=dp(28),
        ))

        storage_card.add_widget(storage_inner)
        ca.add_widget(storage_card)

        # Database tools card
        ca.add_widget(section_label("Database & Maintenance"))
        tools_card = make_card(padding=20, size_hint_y=None, height=dp(120))
        tools_inner = MDBoxLayout(orientation="vertical", spacing=dp(8))
        tools_inner.add_widget(MDLabel(
            text="Create a timestamped backup of your Momentum database.\n"
                 "Backups are stored in your app's private storage.",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=COLORS["text_secondary"],
            size_hint_y=None, height=dp(44),
        ))
        tools_inner.add_widget(MDRaisedButton(
            text="Create Backup Now",
            md_bg_color=COLORS["accent"],
            size_hint_y=None, height=dp(44),
            on_release=lambda x: self._backup(),
        ))
        tools_card.add_widget(tools_inner)
        ca.add_widget(tools_card)

        # About card
        ca.add_widget(section_label("About"))
        about_card = make_card(padding=20, size_hint_y=None, height=dp(100))
        about_card.add_widget(MDLabel(
            text="Momentum Android v1.0.0\n"
                 "A consistency-first productivity companion.\n"
                 "Your data stays on your device — no cloud, no ads.",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=COLORS["text_secondary"],
            halign="center",
        ))
        ca.add_widget(about_card)
        ca.add_widget(MDBoxLayout(size_hint_y=None, height=dp(16)))

    # ------------------------------------------------------------------
    def _backup(self) -> None:
        try:
            path = self.controller.backup()
            show_dialog("Backup Created", f"Saved to:\n{path}")
        except Exception as e:
            show_dialog("Backup Failed", str(e))
