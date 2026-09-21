[app]

# ---- Identity --------------------------------------------------------
title = Momentum
package.name = momentum
package.domain = com.upredictedbunny

version = 1.0.0

# ---- Source ----------------------------------------------------------
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,sql,md

# Entry point
source.main = main.py

# ---- Requirements ----------------------------------------------------
# Only Android-compatible packages.
# sqlite3 is part of CPython stdlib (compiled into the interpreter by p4a)
# and must NOT appear here — p4a has no separate recipe for it.
# customtkinter, pyinstaller, matplotlib are intentionally excluded.
# plyer provides Android notifications.
requirements = python3==3.11.9,kivy==2.3.1,kivymd==1.2.0,plyer

# ---- Android ---------------------------------------------------------
android.permissions = INTERNET,RECEIVE_BOOT_COMPLETED,VIBRATE,POST_NOTIFICATIONS,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Minimum SDK 21 = Android 5.0 Lollipop (wide device coverage)
android.minapi = 21

# Target SDK 33 = Android 13
android.api = 33

# NDK r25b — stable with the pinned Python 3.11 / Kivy 2.3.1 Android toolchain
android.ndk = 25b

# Single-arch debug build — arm64-v8a covers all modern Android phones
android.archs = arm64-v8a

# Automatically accept Android SDK licenses in CI.
# Required for non-interactive GitHub Actions builds.
android.accept_sdk_license = True

# Orientation: portrait-first
orientation = portrait

# ---- Display ---------------------------------------------------------
# Show the status bar (safer default for first debug build)
fullscreen = 0

# ---- Icons & Splash --------------------------------------------------
# Place icon.png (512×512) and presplash.png (1080×1920) in the project root,
# then uncomment these lines:
# icon.filename = %(source.dir)s/icon.png
# presplash.filename = %(source.dir)s/presplash.png

# ---- Build log level -------------------------------------------------
log_level = 2
warn_on_root = 1

# ---- P4A recipe overrides -------------------------------------------
# p4a.branch = master   # uncomment to build from p4a HEAD

[buildozer]
log_level = 2
warn_on_root = 1
