[app]

# ---- Identity --------------------------------------------------------
title = Momentum
package.name = momentum
package.domain = com.upredictedbunny

version = 1.0.0

# ---- Source ----------------------------------------------------------
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,sql,md
source.main = main.py

# ---- Requirements ----------------------------------------------------
# Pin BOTH the target Python and host Python to the same version.
# python-for-android requires these versions to match.
# sqlite3 is part of CPython stdlib and must not appear here.
requirements = python3==3.11.9,hostpython3==3.11.9,kivy==2.3.1,kivymd==1.2.0,plyer

# ---- Android ---------------------------------------------------------
android.permissions = INTERNET,RECEIVE_BOOT_COMPLETED,VIBRATE,POST_NOTIFICATIONS,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.minapi = 21
android.api = 33
android.ndk = 25b
android.archs = arm64-v8a

# Automatically accept Android SDK licenses in CI.
android.accept_sdk_license = True

orientation = portrait
fullscreen = 0

# ---- Icons & Splash --------------------------------------------------
# icon.filename = %(source.dir)s/icon.png
# presplash.filename = %(source.dir)s/presplash.png

log_level = 2
warn_on_root = 1

# Use the stable p4a master branch explicitly.
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
