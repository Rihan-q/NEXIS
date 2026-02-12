# ============================================================
#  memory/storage.py — Persistent memory & reminders
#  Uses SQLite — 100 % local, no cloud needed
# ============================================================

import sqlite3
import datetime
import threading
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config


class MemoryStore:
    """
    Two-table SQLite store:
    ├── memories  : free-form facts the user asks Jarvis to remember
    └── reminders : time-based alerts (checked by ReminderThread)
    """

    def __init__(self, db_path: str = config.DB_PATH):
        # Make sure the data/ folder exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._lock   = threading.Lock()
        self._init_db()

    # ── DB setup ──────────────────────────────────────────────
    def _init_db(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    content    TEXT    NOT NULL,
                    saved_at   TEXT    NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    task        TEXT    NOT NULL,
                    remind_at   TEXT    NOT NULL,  -- ISO-8601 datetime
                    notified    INTEGER DEFAULT 0  -- 0=pending, 1=done
                )
            """)
            conn.commit()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row   # enables dict-style row access
        return conn

    # ── Memories API ─────────────────────────────────────────
    def save_memory(self, content: str):
        """Store a new fact."""
        now = datetime.datetime.now().isoformat(timespec="seconds")
        with self._lock, self._connect() as conn:
            conn.execute(
                "INSERT INTO memories (content, saved_at) VALUES (?, ?)",
                (content.strip(), now)
            )
            conn.commit()
        print(f"[Memory] Saved: {content!r}")

    def get_all_memories(self) -> list[dict]:
        """Return every stored fact, newest first."""
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT content, saved_at FROM memories ORDER BY id DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    def clear_memories(self):
        """Delete all stored memories (does NOT affect reminders)."""
        with self._lock, self._connect() as conn:
            conn.execute("DELETE FROM memories")
            conn.commit()

    # ── Reminders API ─────────────────────────────────────────
    def add_reminder(self, task: str, remind_at: datetime.datetime):
        """Schedule a new reminder."""
        remind_str = remind_at.isoformat(timespec="seconds")
        with self._lock, self._connect() as conn:
            conn.execute(
                "INSERT INTO reminders (task, remind_at) VALUES (?, ?)",
                (task.strip(), remind_str)
            )
            conn.commit()
        print(f"[Reminder] Set: '{task}' at {remind_str}")

    def get_pending_reminders(self) -> list[dict]:
        """Return all un-notified reminders."""
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT id, task, remind_at FROM reminders WHERE notified=0 ORDER BY remind_at"
            ).fetchall()
        return [dict(r) for r in rows]

    def get_due_reminders(self) -> list[dict]:
        """Return reminders whose time has arrived (and haven't fired yet)."""
        now = datetime.datetime.now().isoformat(timespec="seconds")
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT id, task, remind_at FROM reminders WHERE notified=0 AND remind_at <= ?",
                (now,)
            ).fetchall()
        return [dict(r) for r in rows]

    def mark_notified(self, reminder_id: int):
        """Flag a reminder as fired so it doesn't trigger again."""
        with self._lock, self._connect() as conn:
            conn.execute(
                "UPDATE reminders SET notified=1 WHERE id=?", (reminder_id,)
            )
            conn.commit()


# ── Background reminder thread ────────────────────────────────
class ReminderThread(threading.Thread):
    """
    Runs in the background every 30 seconds, checks for due reminders,
    and calls `callback(task_text)` when one fires.
    """

    def __init__(self, memory: MemoryStore, callback):
        super().__init__(daemon=True)   # dies automatically when main exits
        self.memory   = memory
        self.callback = callback        # e.g. lambda text: speaker.say(text)
        self._stop_event = threading.Event()

    def run(self):
        print("[Reminders] Background thread started ✓")
        while not self._stop_event.is_set():
            due = self.memory.get_due_reminders()
            for r in due:
                msg = f"⏰ Reminder: {r['task']}"
                print(f"\n{msg}\n")
                self.callback(msg)
                self.memory.mark_notified(r["id"])
            # Sleep in small chunks so stop_event is responsive
            for _ in range(30):
                if self._stop_event.is_set():
                    break
                self._stop_event.wait(timeout=1)

    def stop(self):
        self._stop_event.set()
