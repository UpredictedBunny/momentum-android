"""
focus_screen.py
----------------
Focus Mode: distraction-free 25-minute deep work timer.
Timer state persists across in-app navigation via module-level _focus_state.
"""

from __future__ import annotations

from datetime import datetime

from kivy.clock import Clock
from kivy.metrics import dp

from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout

from controllers.focus_controller import FocusController
from screens.base_screen import (
    StandardLayout, make_card, COLORS, PAD
)


class _FocusState:
    running: bool = False
    remaining: int = 25 * 60
    last_tick_time: datetime | None = None
    clock_event = None


_focus_state = _FocusState()


class FocusScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = FocusController()
        self._timer_label: MDLabel | None = None
        self._status_label: MDLabel | None = None
        self._start_btn: MDRaisedButton | None = None
        self._build()

    # ------------------------------------------------------------------
    def _build(self) -> None:
        self._layout = StandardLayout(
            title="Focus Mode",
            current_tab="menu",  # accessible via More menu
        )
        self.add_widget(self._layout)
        ca = self._layout.content_area

        focus_card = make_card(padding=32, size_hint_y=None, height=dp(300))
        inner = MDBoxLayout(orientation="vertical", spacing=dp(16))

        inner.add_widget(MDLabel(
            text="Deep Work",
            font_style="H5",
            theme_text_color="Custom",
            text_color=COLORS["text_secondary"],
            halign="center",
            size_hint_y=None, height=dp(36),
        ))

        self._timer_label = MDLabel(
            text=self._fmt(_focus_state.remaining),
            font_style="H1",
            theme_text_color="Custom",
            text_color=COLORS["accent"],
            halign="center",
            size_hint_y=None, height=dp(80),
        )
        inner.add_widget(self._timer_label)

        self._status_label = MDLabel(
            text="Focusing…" if _focus_state.running else "Ready",
            font_style="Body1",
            theme_text_color="Custom",
            text_color=COLORS["text_secondary"],
            halign="center",
            size_hint_y=None, height=dp(32),
        )
        inner.add_widget(self._status_label)

        btn_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(52), spacing=dp(16))
        self._start_btn = MDRaisedButton(
            text="Pause" if _focus_state.running else "Start Focus",
            md_bg_color=COLORS["accent"],
            on_release=self._toggle,
        )
        btn_row.add_widget(self._start_btn)
        btn_row.add_widget(MDFlatButton(
            text="Reset",
            on_release=lambda x: self._reset(),
        ))
        inner.add_widget(btn_row)

        focus_card.add_widget(inner)
        ca.add_widget(focus_card)

        tip_card = make_card(padding=20, size_hint_y=None, height=dp(80))
        tip_card.add_widget(MDLabel(
            text="💡 Put your phone face-down and eliminate distractions.\n"
                 "This session will be logged automatically when complete.",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=COLORS["text_secondary"],
            halign="center",
        ))
        ca.add_widget(tip_card)
        ca.add_widget(MDBoxLayout(size_hint_y=None, height=dp(16)))

        if _focus_state.running and _focus_state.clock_event is None:
            _focus_state.clock_event = Clock.schedule_interval(self._tick, 1)

    # ------------------------------------------------------------------
    def _toggle(self, *args) -> None:
        if _focus_state.running:
            self._pause()
        else:
            self._start()

    def _start(self) -> None:
        if _focus_state.remaining <= 0:
            _focus_state.remaining = 25 * 60
        _focus_state.running = True
        _focus_state.last_tick_time = datetime.now()
        _focus_state.clock_event = Clock.schedule_interval(self._tick, 1)
        if self._status_label:
            self._status_label.text = "Focus in progress…"
        if self._start_btn:
            self._start_btn.text = "Pause"

    def _pause(self) -> None:
        _focus_state.running = False
        if _focus_state.clock_event:
            _focus_state.clock_event.cancel()
            _focus_state.clock_event = None
        if self._status_label:
            self._status_label.text = "Paused"
        if self._start_btn:
            self._start_btn.text = "Resume"

    def _reset(self) -> None:
        _focus_state.running = False
        if _focus_state.clock_event:
            _focus_state.clock_event.cancel()
            _focus_state.clock_event = None
        _focus_state.remaining = 25 * 60
        if self._timer_label:
            self._timer_label.text = self._fmt(_focus_state.remaining)
        if self._status_label:
            self._status_label.text = "Ready"
        if self._start_btn:
            self._start_btn.text = "Start Focus"

    def _tick(self, dt: float) -> None:
        if not _focus_state.running:
            return
        now = datetime.now()
        if _focus_state.last_tick_time is not None:
            elapsed = int((now - _focus_state.last_tick_time).total_seconds())
        else:
            elapsed = 1
        _focus_state.last_tick_time = now
        _focus_state.remaining = max(0, _focus_state.remaining - elapsed)
        if self._timer_label:
            self._timer_label.text = self._fmt(_focus_state.remaining)
        if _focus_state.remaining <= 0:
            self._complete()

    def _complete(self) -> None:
        _focus_state.running = False
        if _focus_state.clock_event:
            _focus_state.clock_event.cancel()
            _focus_state.clock_event = None
        try:
            self.controller.record(25, 5)
        except Exception:
            pass
        if self._status_label:
            self._status_label.text = "Focus session complete! 🎉"
        if self._start_btn:
            self._start_btn.text = "Start Focus"
        try:
            from plyer import notification  # type: ignore
            notification.notify(
                title="Focus Complete!",
                message="25 minutes of deep work done. Well done!",
                app_name="Momentum",
                timeout=5,
            )
        except Exception:
            pass

    @staticmethod
    def _fmt(seconds: int) -> str:
        m, s = divmod(max(0, int(seconds)), 60)
        return f"{m:02d}:{s:02d}"

    def on_enter(self) -> None:
        if self._timer_label:
            self._timer_label.text = self._fmt(_focus_state.remaining)
        if self._status_label:
            self._status_label.text = "Focusing…" if _focus_state.running else (
                "Ready" if _focus_state.remaining == 25 * 60 else "Paused"
            )
        if _focus_state.running and _focus_state.clock_event is None:
            _focus_state.last_tick_time = datetime.now()
            _focus_state.clock_event = Clock.schedule_interval(self._tick, 1)
