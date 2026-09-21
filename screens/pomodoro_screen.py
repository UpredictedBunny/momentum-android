"""
pomodoro_screen.py
-------------------
Pomodoro timer for Android.

Key Android differences from the desktop version:
  - Kivy Clock replaces Tkinter's .after() for the countdown tick
  - Timer STATE is stored in module-level _pomo_state so the countdown
    continues even when the user navigates to another screen and returns
  - Clock.schedule_interval keeps firing as long as the Kivy app is in
    the foreground; backgrounded apps may be throttled by Android but the
    elapsed-time correction in _tick() compensates on resume
"""

from __future__ import annotations

from datetime import datetime

from kivy.clock import Clock
from kivy.metrics import dp

from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu

from config.settings import settings
from controllers.pomodoro_controller import PomodoroController
from screens.base_screen import (
    StandardLayout, make_card, section_label, stat_card,
    COLORS, PAD
)


# -----------------------------------------------------------------------
# Persistent timer state (survives screen navigation)
# -----------------------------------------------------------------------
class _PomoState:
    running: bool = False
    remaining: int = 0           # seconds left
    preset_name: str = ""
    focus_minutes: int = 25
    break_minutes: int = 5
    last_tick_time: datetime | None = None
    clock_event = None           # Kivy ClockEvent (schedule handle)


_pomo_state = _PomoState()


class PomodoroScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = PomodoroController()
        self._timer_label: MDLabel | None = None
        self._status_label: MDLabel | None = None
        self._stats_label: MDLabel | None = None
        self._start_btn: MDRaisedButton | None = None
        self._preset_label: MDLabel | None = None
        self._menu: MDDropdownMenu | None = None
        self._build()

    # ------------------------------------------------------------------
    def _build(self) -> None:
        self._layout = StandardLayout(
            title="Pomodoro",
            current_tab="pomodoro",
        )
        self.add_widget(self._layout)
        ca = self._layout.content_area

        # Preset selector card
        preset_card = make_card(padding=16, size_hint_y=None, height=dp(72))
        preset_row = MDBoxLayout(orientation="horizontal", spacing=dp(8))
        preset_row.add_widget(MDLabel(
            text="Preset:",
            theme_text_color="Custom",
            text_color=COLORS["text_secondary"],
            size_hint=(None, None), size=(dp(60), dp(40)),
        ))
        self._preset_label = MDLabel(
            text=_pomo_state.preset_name or self._default_preset_name(),
            theme_text_color="Custom",
            text_color=COLORS["text_primary"],
        )
        preset_row.add_widget(self._preset_label)
        preset_btn = MDFlatButton(
            text="Change",
            on_release=self._open_preset_menu,
        )
        preset_row.add_widget(preset_btn)
        preset_card.add_widget(preset_row)
        ca.add_widget(preset_card)

        # Timer display card
        timer_card = make_card(padding=24, size_hint_y=None, height=dp(240))
        timer_inner = MDBoxLayout(orientation="vertical", spacing=dp(12))

        self._timer_label = MDLabel(
            text=self._format(
                _pomo_state.remaining if _pomo_state.remaining > 0
                else _pomo_state.focus_minutes * 60
            ),
            font_style="H2",
            theme_text_color="Custom",
            text_color=COLORS["accent"],
            halign="center",
        )
        timer_inner.add_widget(self._timer_label)

        self._status_label = MDLabel(
            text="Focusing…" if _pomo_state.running else "Ready",
            font_style="Body1",
            theme_text_color="Custom",
            text_color=COLORS["text_secondary"],
            halign="center",
            size_hint_y=None, height=dp(32),
        )
        timer_inner.add_widget(self._status_label)

        # Buttons
        btn_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(52), spacing=dp(12))
        self._start_btn = MDRaisedButton(
            text="Pause" if _pomo_state.running else "Start",
            md_bg_color=COLORS["accent"],
            on_release=self._toggle_timer,
        )
        btn_row.add_widget(self._start_btn)
        btn_row.add_widget(MDFlatButton(
            text="Reset",
            on_release=lambda x: self._reset_timer(),
        ))
        timer_inner.add_widget(btn_row)

        timer_card.add_widget(timer_inner)
        ca.add_widget(timer_card)

        # Stats card
        stats_card = make_card(padding=16, size_hint_y=None, height=dp(72))
        self._stats_label = MDLabel(
            text="",
            font_style="Body1",
            theme_text_color="Custom",
            text_color=COLORS["text_secondary"],
            halign="center",
        )
        stats_card.add_widget(self._stats_label)
        ca.add_widget(stats_card)

        ca.add_widget(MDBoxLayout(size_hint_y=None, height=dp(16)))

        # Init preset if not yet set
        if not _pomo_state.preset_name:
            self._load_default_preset()

        self._refresh_stats()

        # If a timer was already running, hook back into the Clock
        if _pomo_state.running and _pomo_state.clock_event is None:
            _pomo_state.clock_event = Clock.schedule_interval(self._tick, 1)

    # ------------------------------------------------------------------
    def _default_preset_name(self) -> str:
        presets = settings.pomodoro.presets
        return presets[0]["name"] if presets else "Classic"

    def _load_default_preset(self) -> None:
        presets = settings.pomodoro.presets
        if not presets:
            return
        p = presets[0]
        _pomo_state.preset_name = p["name"]
        _pomo_state.focus_minutes = int(p["focus_minutes"])
        _pomo_state.break_minutes = int(p["break_minutes"])
        _pomo_state.remaining = _pomo_state.focus_minutes * 60
        self._update_display()

    def _open_preset_menu(self, button) -> None:
        if _pomo_state.running:
            return
        presets = settings.pomodoro.presets
        items = [
            {
                "text": f'{p["name"]} ({p["focus_minutes"]}m / {p["break_minutes"]}m break)',
                "on_release": (lambda x, p=p: self._select_preset(p)),
            }
            for p in presets
        ]
        self._menu = MDDropdownMenu(caller=button, items=items, width_mult=5)
        self._menu.open()

    def _select_preset(self, preset: dict) -> None:
        if self._menu:
            self._menu.dismiss()
        _pomo_state.preset_name = preset["name"]
        _pomo_state.focus_minutes = int(preset["focus_minutes"])
        _pomo_state.break_minutes = int(preset["break_minutes"])
        _pomo_state.remaining = _pomo_state.focus_minutes * 60
        _pomo_state.running = False
        if _pomo_state.clock_event:
            _pomo_state.clock_event.cancel()
            _pomo_state.clock_event = None
        self._update_display()
        if self._preset_label:
            self._preset_label.text = preset["name"]
        if self._status_label:
            self._status_label.text = "Ready"
        if self._start_btn:
            self._start_btn.text = "Start"

    # ------------------------------------------------------------------
    def _toggle_timer(self, *args) -> None:
        if _pomo_state.running:
            self._pause_timer()
        else:
            self._start_timer()

    def _start_timer(self) -> None:
        if _pomo_state.running:
            return
        if _pomo_state.remaining <= 0:
            _pomo_state.remaining = _pomo_state.focus_minutes * 60
        _pomo_state.running = True
        _pomo_state.last_tick_time = datetime.now()
        _pomo_state.clock_event = Clock.schedule_interval(self._tick, 1)
        if self._status_label:
            self._status_label.text = "Focusing…"
        if self._start_btn:
            self._start_btn.text = "Pause"

    def _pause_timer(self) -> None:
        _pomo_state.running = False
        if _pomo_state.clock_event:
            _pomo_state.clock_event.cancel()
            _pomo_state.clock_event = None
        if self._status_label:
            self._status_label.text = "Paused"
        if self._start_btn:
            self._start_btn.text = "Resume"

    def _reset_timer(self) -> None:
        _pomo_state.running = False
        if _pomo_state.clock_event:
            _pomo_state.clock_event.cancel()
            _pomo_state.clock_event = None
        _pomo_state.remaining = _pomo_state.focus_minutes * 60
        self._update_display()
        if self._status_label:
            self._status_label.text = "Ready"
        if self._start_btn:
            self._start_btn.text = "Start"

    def _tick(self, dt: float) -> None:
        """Called every second by the Kivy Clock."""
        if not _pomo_state.running:
            return

        # Use elapsed real time to compensate for CPU throttling / backgrounding
        now = datetime.now()
        if _pomo_state.last_tick_time is not None:
            elapsed = int((now - _pomo_state.last_tick_time).total_seconds())
        else:
            elapsed = 1
        _pomo_state.last_tick_time = now

        _pomo_state.remaining = max(0, _pomo_state.remaining - elapsed)
        self._update_display()

        if _pomo_state.remaining <= 0:
            self._complete_session()

    def _complete_session(self) -> None:
        _pomo_state.running = False
        if _pomo_state.clock_event:
            _pomo_state.clock_event.cancel()
            _pomo_state.clock_event = None

        # Record to DB
        try:
            self.controller.record(
                _pomo_state.preset_name,
                _pomo_state.focus_minutes,
                _pomo_state.break_minutes,
            )
        except Exception:
            pass

        _pomo_state.remaining = 0
        self._update_display()
        if self._status_label:
            self._status_label.text = "Session complete! 🎉"
        if self._start_btn:
            self._start_btn.text = "Start"
        self._refresh_stats()

        # Try to fire a notification
        self._notify_complete()

    def _notify_complete(self) -> None:
        try:
            from plyer import notification  # type: ignore
            notification.notify(
                title="Pomodoro Complete!",
                message=f"Great focus session — {_pomo_state.focus_minutes} minutes done.",
                app_name="Momentum",
                timeout=5,
            )
        except Exception:
            pass

    # ------------------------------------------------------------------
    def _update_display(self) -> None:
        if self._timer_label:
            self._timer_label.text = self._format(_pomo_state.remaining)

    @staticmethod
    def _format(seconds: int) -> str:
        m, s = divmod(max(0, int(seconds)), 60)
        return f"{m:02d}:{s:02d}"

    def _refresh_stats(self) -> None:
        if self._stats_label:
            try:
                stats = self.controller.stats()
                sessions = int(stats.get("sessions", 0))
                focus_m = int(stats.get("focus_minutes", 0))
                self._stats_label.text = (
                    f"Today: {sessions} session{'s' if sessions != 1 else ''} "
                    f"· {focus_m} min focused"
                )
            except Exception:
                self._stats_label.text = "Stats unavailable"

    # ------------------------------------------------------------------
    def on_enter(self) -> None:
        """Re-hook into the running Clock event when navigating back."""
        self._update_display()
        self._refresh_stats()
        if self._status_label:
            if _pomo_state.running:
                self._status_label.text = "Focusing…"
                if self._start_btn:
                    self._start_btn.text = "Pause"
                # Re-hook the clock if needed
                if _pomo_state.clock_event is None:
                    _pomo_state.last_tick_time = datetime.now()
                    _pomo_state.clock_event = Clock.schedule_interval(self._tick, 1)
