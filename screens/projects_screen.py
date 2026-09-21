"""
projects_screen.py
-------------------
Projects screen: list projects with progress sliders, add-project dialog
with name / deadline / GitHub link / notes. ProjectsController reused.
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

from controllers.projects_controller import ProjectsController
from screens.base_screen import (
    StandardLayout, make_card, section_label,
    show_dialog, COLORS, PAD
)


class ProjectsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = ProjectsController()
        self._add_dialog: MDDialog | None = None
        self._fields: list[MDTextField] = []
        self._build()

    # ------------------------------------------------------------------
    def _build(self) -> None:
        self._layout = StandardLayout(
            title="Projects",
            current_tab="menu",
            right_icons=[["plus", lambda x: self._open_add_dialog()]],
        )
        self.add_widget(self._layout)
        self._refresh()

    # ------------------------------------------------------------------
    def _refresh(self) -> None:
        ca = self._layout.content_area
        ca.clear_widgets()
        projects = self.controller.all()

        if not projects:
            empty = make_card(padding=24, size_hint_y=None, height=dp(110))
            empty.add_widget(MDLabel(
                text="No projects yet.\n\nTap + to start tracking one.",
                halign="center",
                theme_text_color="Custom",
                text_color=COLORS["text_secondary"],
            ))
            ca.add_widget(empty)
        else:
            for p in projects:
                ca.add_widget(self._project_card(p))

        ca.add_widget(MDBoxLayout(size_hint_y=None, height=dp(16)))

    # ------------------------------------------------------------------
    def _project_card(self, p: dict):
        pct = float(p["progress_pct"])
        card = make_card(padding=16, size_hint_y=None)
        inner = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8), padding=[0, 0, 0, 4])
        inner.bind(minimum_height=inner.setter("height"))

        # Name + deadline row
        name_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(36))
        name_row.add_widget(MDLabel(
            text=p["name"],
            font_style="Body1",
            theme_text_color="Custom",
            text_color=COLORS["text_primary"],
        ))
        name_row.add_widget(MDLabel(
            text=p["deadline"] or "No deadline",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=COLORS["text_secondary"],
            size_hint=(None, None), size=(dp(100), dp(36)),
            halign="right",
        ))
        inner.add_widget(name_row)

        # GitHub link (if present)
        if p.get("github_link"):
            inner.add_widget(MDLabel(
                text=f"⭐ {p['github_link']}",
                font_style="Caption",
                theme_text_color="Custom",
                text_color=COLORS["accent"],
                size_hint_y=None, height=dp(22),
            ))

        # Notes (truncated)
        if p.get("notes"):
            notes_preview = p["notes"][:80] + ("…" if len(p["notes"]) > 80 else "")
            inner.add_widget(MDLabel(
                text=notes_preview,
                font_style="Caption",
                theme_text_color="Custom",
                text_color=COLORS["text_secondary"],
                size_hint_y=None, height=dp(22),
            ))

        # Progress percentage
        pct_label = MDLabel(
            text=f"{pct:.0f}% complete",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=COLORS["accent"],
            size_hint_y=None, height=dp(22),
        )
        inner.add_widget(pct_label)

        # Progress slider
        slider = MDSlider(
            min=0, max=100,
            value=pct,
            color=COLORS["accent"],
            size_hint_y=None, height=dp(40),
        )

        def on_value(widget, value, _id=p["id"], _lbl=pct_label):
            _lbl.text = f"{value:.0f}% complete"

        def on_release(widget, _id=p["id"]):
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
    def _open_add_dialog(self) -> None:
        name_f = MDTextField(hint_text="Project name *", mode="rectangle")
        dl_f = MDTextField(hint_text="Deadline YYYY-MM-DD (optional)", mode="rectangle")
        gh_f = MDTextField(hint_text="GitHub link (optional)", mode="rectangle")
        notes_f = MDTextField(hint_text="Notes (optional)", mode="rectangle")
        self._fields = [name_f, dl_f, gh_f, notes_f]

        content = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(280), spacing=dp(8))
        for f in self._fields:
            content.add_widget(f)

        self._add_dialog = MDDialog(
            title="Add Project",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self._add_dialog.dismiss()),
                MDRaisedButton(text="ADD", on_release=lambda x: self._save_project()),
            ],
        )
        self._add_dialog.open()

    def _save_project(self) -> None:
        name, deadline, github, notes = [f.text.strip() for f in self._fields]
        if not name:
            show_dialog("Invalid", "Please enter a project name.")
            return
        ok = self.controller.add(name, deadline or None, github, notes)
        if ok:
            self._add_dialog.dismiss()
            self._refresh()
        else:
            show_dialog("Invalid", "Enter a valid project name.")

    def on_enter(self) -> None:
        self._refresh()
