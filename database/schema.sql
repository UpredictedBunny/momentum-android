-- schema.sql
-- Momentum database schema.
-- Applied once at first launch by DatabaseManager.initialize().
-- Every feature module in the spec maps to one or more tables below.

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------
-- 2. Daily Routine
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS routine_items (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    period        TEXT NOT NULL DEFAULT 'morning',   -- morning/afternoon/evening/night
    est_minutes   INTEGER DEFAULT 0,
    priority      TEXT DEFAULT 'medium',              -- low/medium/high
    sort_order    INTEGER DEFAULT 0,
    is_active     INTEGER DEFAULT 1                   -- soft delete
);

CREATE TABLE IF NOT EXISTS routine_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    routine_item_id INTEGER NOT NULL REFERENCES routine_items(id) ON DELETE CASCADE,
    log_date        TEXT NOT NULL,                     -- 'YYYY-MM-DD'
    is_completed    INTEGER DEFAULT 0,
    notes           TEXT DEFAULT '',
    completed_at    TEXT,
    UNIQUE(routine_item_id, log_date)
);

-- ---------------------------------------------------------------
-- 3. Habit Tracker
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS habits (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL UNIQUE,
    icon          TEXT DEFAULT '',
    is_active     INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS habit_logs (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id      INTEGER NOT NULL REFERENCES habits(id) ON DELETE CASCADE,
    log_date      TEXT NOT NULL,
    is_completed  INTEGER DEFAULT 0,
    UNIQUE(habit_id, log_date)
);

-- ---------------------------------------------------------------
-- 4. Calendar (per-day snapshot: mood, notes, hours)
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS calendar_days (
    log_date        TEXT PRIMARY KEY,
    mood            TEXT DEFAULT '',                  -- e.g. great/good/okay/bad
    notes           TEXT DEFAULT '',
    hours_studied   REAL DEFAULT 0,
    hours_worked    REAL DEFAULT 0
);

-- ---------------------------------------------------------------
-- 5. Pomodoro Timer
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS pomodoro_sessions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    session_date  TEXT NOT NULL,
    preset_name   TEXT NOT NULL,
    focus_minutes INTEGER NOT NULL,
    break_minutes INTEGER NOT NULL,
    completed_at  TEXT NOT NULL
);

-- ---------------------------------------------------------------
-- 6. Study Tracker
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS study_logs (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    log_date      TEXT NOT NULL,
    category      TEXT NOT NULL,   -- University / Freelancing / AI / Reading
    hours         REAL NOT NULL DEFAULT 0
);

-- ---------------------------------------------------------------
-- 8. Daily Review
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS daily_reviews (
    log_date          TEXT PRIMARY KEY,
    studied           INTEGER DEFAULT 0,
    coded             INTEGER DEFAULT 0,
    exercised         INTEGER DEFAULT 0,
    grateful_for      TEXT DEFAULT '',
    learned_today     TEXT DEFAULT '',
    improve_tomorrow  TEXT DEFAULT ''
);

-- ---------------------------------------------------------------
-- 15. Smart Goal System
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS goals (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    progress_pct  REAL DEFAULT 0,
    deadline      TEXT,
    is_active     INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS goal_milestones (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_id       INTEGER NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    title         TEXT NOT NULL,
    is_completed  INTEGER DEFAULT 0
);

-- ---------------------------------------------------------------
-- 16. Project Tracker
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS projects (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    progress_pct  REAL DEFAULT 0,
    deadline      TEXT,
    github_link   TEXT DEFAULT '',
    notes         TEXT DEFAULT ''
);

-- ---------------------------------------------------------------
-- 20. Gamification
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS gamification_state (
    id            INTEGER PRIMARY KEY CHECK (id = 1),  -- single row
    xp            INTEGER DEFAULT 0,
    level         INTEGER DEFAULT 1,
    coins         INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS achievements (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    code          TEXT NOT NULL UNIQUE,   -- e.g. '7_day_streak'
    name          TEXT NOT NULL,
    description   TEXT DEFAULT '',
    unlocked_at   TEXT                     -- NULL until earned
);

-- ---------------------------------------------------------------
-- 21. AI Coach notes (daily generated advice, cached)
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS coach_notes (
    log_date      TEXT PRIMARY KEY,
    advice        TEXT DEFAULT ''
);

-- Seed the single gamification row if missing
INSERT OR IGNORE INTO gamification_state (id, xp, level, coins) VALUES (1, 0, 1, 0);
