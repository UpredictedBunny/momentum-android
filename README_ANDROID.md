# Momentum Android v1.0.0

A mobile-first Android port of the Momentum productivity desktop application.

---

## Overview

Momentum Android preserves all business logic, data models, services, and
controllers from the frozen Windows v1.0.0 release while replacing the
CustomTkinter desktop UI layer with a Kivy/KivyMD touch-first interface.

**The Windows application is not modified in any way.**

---

## Technology Stack

| Layer | Desktop (frozen) | Android (this project) |
|-------|-----------------|----------------------|
| UI | CustomTkinter | Kivy 2.3.0 + KivyMD 1.2.0 |
| Timer | `widget.after()` | `kivy.clock.Clock` |
| Notifications | plyer (Windows) | plyer (Android channels) |
| Packaging | PyInstaller | Buildozer |
| Database | SQLite (same) | SQLite (same) |
| Business logic | Python (same) | Python (same — reused) |

---

## Prerequisites

### Build machine (Ubuntu / WSL2 recommended)

```bash
# Python 3.11+
python3 --version

# Java JDK 17
sudo apt install openjdk-17-jdk

# Build tools
sudo apt install -y git zip unzip autoconf libtool pkg-config \
    zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake \
    libffi-dev libssl-dev

# Buildozer
pip install --upgrade buildozer
pip install --upgrade cython

# Android SDK / NDK: Buildozer downloads these automatically on first build.
```

---

## Build Instructions

### 1. Clone / place the project

```
momentum_android/
├── main.py
├── buildozer.spec
├── config/
├── database/
├── models/
├── services/
├── controllers/
├── utils/
├── themes/
└── screens/
```

### 2. Build a debug APK

```bash
cd momentum_android/
buildozer android debug
```

The first build downloads the Android SDK, NDK, and all Python recipes —
this takes 20–60 minutes depending on your connection.

Subsequent builds are incremental and take 2–5 minutes.

The APK is output to:

```
momentum_android/.buildozer/android/platform/build-*/dists/momentum/bin/
```

Copy and rename to `Momentum-v1.0.0-Android.apk`.

### 3. Build a release APK

```bash
# Generate a keystore once
keytool -genkey -v -keystore momentum-release-key.jks \
  -alias momentum -keyalg RSA -keysize 2048 -validity 10000

# Build and sign
buildozer android release
```

### 4. Install on a device

```bash
# Via ADB (USB debugging enabled)
adb install Momentum-v1.0.0-Android.apk

# Or copy to device and open via Files app
```

### 5. View logs during development

```bash
adb logcat | grep -i "momentum\|python\|kivy"
```

---

## Development (run on desktop without Android)

```bash
cd momentum_android/
pip install kivy kivymd plyer
python main.py
```

Data is stored in `~/.momentum_android/` during desktop development.

---

## Project Structure

```
momentum_android/
├── main.py                   # App entry point (MomentumApp)
├── buildozer.spec            # Android build configuration
│
├── config/
│   ├── settings.py           # ADAPTED: Android-safe path resolution
│   └── config.json           # REUSED: same as Windows
│
├── database/
│   ├── db_manager.py         # ADAPTED: writable path → Android storage
│   └── schema.sql            # REUSED: identical to Windows
│
├── models/
│   ├── base_model.py         # REUSED: unchanged
│   └── habit.py              # REUSED: unchanged
│
├── services/                 # REUSED: all services unchanged
│   ├── habit_service.py
│   ├── routine_service.py
│   ├── pomodoro_service.py
│   ├── study_service.py
│   └── dashboard_service.py
│
├── controllers/              # REUSED: all unchanged except settings_controller
│   ├── dashboard_controller.py
│   ├── habit_controller.py
│   ├── routine_controller.py
│   ├── pomodoro_controller.py
│   ├── study_controller.py
│   ├── calendar_controller.py
│   ├── statistics_controller.py
│   ├── goals_controller.py
│   ├── projects_controller.py
│   ├── focus_controller.py
│   └── settings_controller.py  # ADAPTED: returns Android path
│
├── utils/
│   └── logger.py             # ADAPTED: logs to Android private storage
│
├── themes/
│   └── theme.py              # NEW: KivyMD colour + typography constants
│
└── screens/                  # NEW: all Android screens (replaces views/)
    ├── base_screen.py        # Shared layout, bottom nav, card/dialog helpers
    ├── dashboard_screen.py
    ├── habits_screen.py
    ├── routine_screen.py
    ├── pomodoro_screen.py
    ├── focus_screen.py
    ├── calendar_screen.py
    ├── study_screen.py
    ├── statistics_screen.py
    ├── goals_screen.py
    ├── projects_screen.py
    ├── settings_screen.py
    └── menu_screen.py        # "More" hub for secondary screens
```

---

## Architecture

```
Screen  →  Controller  →  Service  →  Model  →  DatabaseManager  →  SQLite
 (new)       (reused)     (reused)   (reused)      (adapted)         (same)
```

The Android project replaces only the View layer (screens/) and adapts three
infrastructure files (settings.py, db_manager.py, logger.py) for Android paths.
Every business rule, calculation, streak logic, and data model is preserved.

---

## Navigation

### Bottom navigation bar (always visible)
| Tab | Screen |
|-----|--------|
| 🏠 Home | Dashboard |
| ✓ Habits | Habit Tracker |
| ☀ Routine | Daily Routine |
| ⏱ Pomodoro | Pomodoro Timer |
| ⋯ More | Menu hub |

### More menu (secondary screens)
Calendar · Study Tracker · Statistics · Goals · Projects · Focus Mode · Settings

---

## Reused vs Replaced

### Reused unchanged (copied verbatim)
- `database/schema.sql`
- `config/config.json`
- `models/base_model.py`, `models/habit.py`
- All 5 service files
- 10 of 11 controller files

### Android-adapted (same interface, new internals)
- `config/settings.py` — path resolution → Android app storage
- `database/db_manager.py` — db path uses adapted settings.resolve_path()
- `utils/logger.py` — log file → Android private storage
- `controllers/settings_controller.py` — returns Android path in info()

### Desktop-only (not ported — intentionally excluded)
- `views/` (all CustomTkinter views)
- `themes/dark_theme.py` (imports customtkinter)
- `views/components/` (CTk sidebar, placeholder)
- PyInstaller build configuration

### Android-specific replacements
| Desktop | Android |
|---------|---------|
| `customtkinter` widgets | `kivy` + `kivymd` widgets |
| `CTkScrollableFrame` | `ScrollView` |
| `CTkToplevel` dialog | `MDDialog` |
| `CTkComboBox` | `MDDropdownMenu` |
| `CTkCheckBox` | `MDCheckbox` |
| `CTkSlider` | `MDSlider` |
| `CTkProgressBar` | `MDProgressBar` |
| `widget.after(1000, fn)` | `Clock.schedule_interval(fn, 1)` |
| Left sidebar nav | Bottom navigation bar |
| `plyer` (Win notifications) | `plyer` (Android channels) |
| `matplotlib` charts | Native canvas progress bars |
| `pyinstaller` | `buildozer` |

---

## Timer Behaviour (Pomodoro & Focus)

The Kivy `Clock.schedule_interval()` is a global scheduler that continues
ticking as long as the Kivy app is in the foreground.

When the user navigates between screens within the app, the timer keeps
running — this is verified by storing state in module-level objects
(`_pomo_state`, `_focus_state`).

When the user **minimises** the app to the Android home screen, Android may
throttle or pause the process after ~60 seconds. On return, the elapsed-time
correction in `_tick()` compensates for any missed seconds using wall-clock
`datetime.now()` comparison.

True background notification timers require an Android `Service` + `Pyjnius`
bridge, which is a known post-v1.0.0 enhancement.

---

## Known Limitations

1. **Background timers**: Pomodoro/Focus timers may lose accuracy if the
   app is minimised for an extended period. Elapsed-time correction is
   implemented but not a substitute for a true Android Service.

2. **Notification channels**: plyer's Android notification implementation
   requires Android 8.0+ channel registration. The app attempts this but
   silently continues if the permission is not granted by the user.

3. **Statistics charts**: Desktop matplotlib charts are replaced by inline
   progress bars. Full charting can be added post-v1.0.0 via Kivy Garden
   charts or a custom Canvas widget.

4. **Font**: The Windows "Segoe UI" font is not available on Android. Kivy
   will fall back to the system default (Roboto on most Android devices).

5. **Landscape mode**: The app is designed portrait-first. Landscape is
   functional but not optimised.

---

## QA Checklist

### Launch
- [ ] Fresh install — app starts, dashboard loads
- [ ] Subsequent launch — persisted data displayed correctly
- [ ] DB created at correct Android path on first run

### Navigation
- [ ] Bottom nav: Dashboard / Habits / Routine / Pomodoro / More
- [ ] More menu: all 7 secondary screens open
- [ ] Android back button exits to previous screen, not home
- [ ] App does not crash when back button is pressed from dashboard

### Habits
- [ ] Today's habits list loads
- [ ] Checking a habit marks it complete, shows streak
- [ ] Unchecking removes completion
- [ ] Add habit dialog saves and appears in list
- [ ] Deactivate / reactivate works
- [ ] Active / All toggle switches correctly

### Routine
- [ ] Today's items load with period grouping
- [ ] Tap checkbox marks item complete (checkmark appears)
- [ ] Add item dialog: name, period, minutes, priority
- [ ] Progress bar updates

### Pomodoro
- [ ] Preset selector shows Classic / Extended
- [ ] Start begins countdown
- [ ] Pause stops countdown, Resume continues
- [ ] Reset returns to preset time
- [ ] Session complete: recorded in DB, stats update, notification fires
- [ ] Timer state preserved when navigating to another screen and returning

### Focus Mode
- [ ] 25:00 countdown starts/pauses/resets
- [ ] Completion records session and shows notification
- [ ] Timer survives navigation away and back

### Calendar
- [ ] ‹ › navigates between days
- [ ] Mood, notes, hours saved and reloaded
- [ ] Today's data is pre-populated

### Study Tracker
- [ ] Category dropdown works
- [ ] Log session: valid hours saved, invalid rejected
- [ ] Recent sessions list shows with correct data
- [ ] Today's total updates after each log

### Statistics
- [ ] Today's 4 cards show correct values
- [ ] 7-day bars reflect habit/study data

### Goals
- [ ] Add goal dialog: name + deadline
- [ ] Slider updates progress in real time
- [ ] Progress persists after navigating away and returning
- [ ] Deactivate removes from active list

### Projects
- [ ] Add project: name, deadline, GitHub, notes
- [ ] Slider saves progress
- [ ] GitHub link and notes shown in card

### Settings
- [ ] Version and storage path shown correctly
- [ ] Backup creates a timestamped .db file
- [ ] Backup success dialog shows path

### Stability
- [ ] Minimise app → reopen → state preserved
- [ ] Navigate through all 12 screens → no crash
- [ ] No Python traceback visible to user
- [ ] Run for 30 minutes → no memory leak symptoms

---

## APK Build Command (exact)

```bash
cd momentum_android/
buildozer android debug 2>&1 | tee build.log
```

Output APK location:
```
.buildozer/android/platform/build-*/dists/momentum/bin/momentum-1.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

Rename before distributing:
```bash
cp .buildozer/android/platform/build-*/dists/momentum/bin/momentum-*-debug.apk \
   Momentum-v1.0.0-Android.apk
```
