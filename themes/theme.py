"""
themes/theme.py
----------------
Single source of truth for colors and typography in Momentum Android.
Mirrors the desktop dark_theme.py values exactly — same palette, same
accent, same danger/secondary colors — translated to KivyMD format.

Colors in Kivy are (r, g, b, a) tuples with 0-1 floats.
"""

from __future__ import annotations


def _hex(h: str) -> list:
    """Convert #RRGGBB hex to [r, g, b, 1.0] Kivy color."""
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return [r / 255, g / 255, b / 255, 1.0]


# ---- Palette (matches desktop COLORS dict) ----------------------------
COLORS = {
    "background":    _hex("#0F1115"),
    "surface":       _hex("#171A21"),
    "surface_alt":   _hex("#1E222B"),
    "border":        _hex("#272B35"),
    "text_primary":  _hex("#F5F6F8"),
    "text_secondary": _hex("#9CA3AF"),
    "accent":        _hex("#4F8EF7"),   # blue
    "secondary":     _hex("#22C55E"),   # green
    "danger":        _hex("#EF4444"),   # red
    "warning":       _hex("#F59E0B"),   # amber
    "accent_alt":    _hex("#A78BFA"),   # purple
    "on_accent":     _hex("#000000"),
}

# ---- Typography sizes (dp) -------------------------------------------
FONT_SIZE = {
    "caption":  12,
    "body":     14,
    "title":    16,
    "heading":  22,
    "display":  36,
    "hero":     52,
}

# ---- Spacing (dp) ----------------------------------------------------
PAD = {
    "xs": 6,
    "sm": 12,
    "md": 16,
    "lg": 24,
    "xl": 32,
}

# ---- Shape ----------------------------------------------------------
RADIUS = 14   # corner radius in dp


def apply_theme(app) -> None:
    """
    Configure KivyMD's MDApp with Momentum's dark palette.
    Call once in MomentumApp.build() before widgets are created.
    """
    app.theme_cls.theme_style = "Dark"
    app.theme_cls.primary_palette = "Blue"
    app.theme_cls.accent_palette = "Green"
    # KivyMD Dark sets a dark surface; we override per-widget for our
    # specific palette using COLORS constants above.
