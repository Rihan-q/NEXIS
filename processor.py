# ============================================================
#  brain/processor.py — Intent detection and response routing
#
#  Parses what the user said and decides what Jarvis should do:
#  greet, answer, search, open apps, manage reminders, etc.
# ============================================================

import re
import math
import random
import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config
from brain import knowledge
from memory.storage import MemoryStore
from windows_control.apps import AppController


# ── Jarvis jokes (offline fallback for fun) ──────────────────
JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "I would tell you a UDP joke, but you might not get it.",
    "A SQL query walks into a bar, walks up to two tables and asks: Can I join you?",
    "Why did the computer go to the doctor? It had a virus!",
    "To understand recursion, you must first understand recursion.",
    "There are only 10 kinds of people: those who understand binary, and those who don't.",
]

# ── Greeting & small-talk patterns ───────────────────────────
GREETING_PATTERNS = [
    r"\b(hi|hello|hey|yo|what's up|sup|howdy|hiya)\b",
    r"\b(good morning|good afternoon|good evening|good night)\b",
]

FAREWELL_PATTERNS = [
    r"\b(bye|goodbye|exit|quit|see you|later|cya|peace out|shut down)\b",
]

HOW_ARE_YOU_PATTERNS = [
    r"\b(how are you|how're you|how do you feel|are you okay|you good)\b",
]

# ── Intent detectors (compiled for speed) ────────────────────
_RE = {k: re.compile(p, re.IGNORECASE) for k, p in {
    "greeting"     : "|".join(GREETING_PATTERNS),
    "farewell"     : "|".join(FAREWELL_PATTERNS),
    "how_are_you"  : "|".join(HOW_ARE_YOU_PATTERNS),
    "time"         : r"\b(what time|current time|what's the time|tell me the time)\b",
    "date"         : r"\b(what('s| is) (today|the date)|today's date|current date)\b",
    "day"          : r"\b(what day|which day)\b",
    "open_app"     : r"\b(open|launch|start|run)\b",
    "close_app"    : r"\b(close|kill|stop|quit|exit)\b",
    "open_folder"  : r"\b(open|show|go to)\b.*(folder|directory|downloads|documents|desktop|pictures|music|videos)\b",
    "remind"       : r"\bremind\s+me\b",
    "remember"     : r"\bremember\s+(that\s+)?(.*)",
    "recall"       : r"\b(what do you remember|recall|show memories|my notes)\b",
    "calc"         : r"\b(calculate|what is|compute|how much is)\s+[\d\s\+\-\*\/\^\(\)\.]+",
    "joke"         : r"\b(joke|make me laugh|something funny|tell me a joke)\b",
    "what_is"      : r"\b(what is|what are|who is|who was|tell me about|explain|define|describe)\b",
    "search"       : r"\b(search for|look up|find|google|search)\b",
    "weather"      : r"\b(weather|temperature|forecast|rain|sunny)\b",
    "news"         : r"\b(news|latest|today's news|headlines)\b",
    "volume_up"    : r"\b(volume up|louder|increase volume)\b",
    "volume_down"  : r"\b(volume down|quieter|lower volume|decrease volume)\b",
    "mute"         : r"\b(mute|silence)\b",
    "screenshot"   : r"\b(screenshot|screen capture|capture screen)\b",
    "lock"         : r"\b(lock (the )?screen|lock pc|lock computer)\b",
    "shutdown"     : r"\b(shutdown|shut down|power off|turn off (the )?pc)\b",
    "restart"      : r"\b(restart|reboot)\b",
    "sleep_pc"     : r"\b(sleep|hibernate|put to sleep)\b.*(pc|computer|system)?\b",
    "list_reminders": r"\b(list reminders|show reminders|my reminders|pending reminders)\b",
    "clear_memory" : r"\b(clear memory|forget everything|delete memories)\b",
}.items()}


class Brain:
    """
    Central processor: maps user input → appropriate action → response string.
    """

    def __init__(self, memory: MemoryStore, app_ctrl: AppController):
        self.memory   = memory
        self.app_ctrl = app_ctrl

    # ── Entry point ───────────────────────────────────────────
    def process(self, text: str) -> tuple[str, bool]:
        """
        Process `text` and return (response_string, should_exit).
        should_exit=True signals the main loop to stop.
        """
        t = text.strip().lower()
        if not t:
            return "I didn't catch that. Could you repeat?", False

        # ─ Farewell ──────────────────────────────────────────
        if _RE["farewell"].search(t):
            return f"Take care, {config.USER_NAME}! Shutting down now.", True

        # ─ Greeting ──────────────────────────────────────────
        if _RE["greeting"].search(t):
            return self._greet(), False

        # ─ How are you ───────────────────────────────────────
        if _RE["how_are_you"].search(t):
            return "I'm running perfectly — ready to help you, " + config.USER_NAME + "!", False

        # ─ Time / Date ───────────────────────────────────────
        if _RE["time"].search(t):
            return "It's currently " + datetime.datetime.now().strftime("%I:%M %p") + ".", False
        if _RE["date"].search(t):
            return "Today is " + datetime.datetime.now().strftime("%A, %B %d, %Y") + ".", False
        if _RE["day"].search(t):
            return "Today is " + datetime.datetime.now().strftime("%A") + ".", False

        # ─ Jokes ─────────────────────────────────────────────
        if _RE["joke"].search(t):
            return random.choice(JOKES), False

        # ─ System control ────────────────────────────────────
        if _RE["lock"].search(t):
            return self.app_ctrl.lock_screen(), False
        if _RE["shutdown"].search(t):
            return self.app_ctrl.shutdown_pc(), False
        if _RE["restart"].search(t):
            return self.app_ctrl.restart_pc(), False
        if _RE["sleep_pc"].search(t):
            return self.app_ctrl.sleep_pc(), False
        if _RE["screenshot"].search(t):
            return self.app_ctrl.take_screenshot(), False
        if _RE["volume_up"].search(t):
            return self.app_ctrl.volume_change("up"), False
        if _RE["volume_down"].search(t):
            return self.app_ctrl.volume_change("down"), False
        if _RE["mute"].search(t):
            return self.app_ctrl.volume_change("mute"), False

        # ─ Open folder ───────────────────────────────────────
        if _RE["open_folder"].search(t):
            result = self._handle_folder(t)
            if result:
                return result, False

        # ─ Open app ──────────────────────────────────────────
        if _RE["open_app"].search(t):
            result = self._handle_open(t)
            if result:
                return result, False

        # ─ Close app ─────────────────────────────────────────
        if _RE["close_app"].search(t):
            result = self._handle_close(t)
            if result:
                return result, False

        # ─ Reminders ─────────────────────────────────────────
        if _RE["remind"].search(t):
            return self._handle_remind(t), False

        if _RE["list_reminders"].search(t):
            return self._list_reminders(), False

        # ─ Memory ────────────────────────────────────────────
        m = _RE["remember"].search(t)
        if m:
            return self._handle_remember(t, m), False

        if _RE["recall"].search(t):
            return self._handle_recall(), False

        if _RE["clear_memory"].search(t):
            self.memory.clear_memories()
            return "I've cleared all stored memories.", False

        # ─ Calculator ────────────────────────────────────────
        calc_result = self._try_calculate(t)
        if calc_result is not None:
            return calc_result, False

        # ─ Weather notice (no weather API — honest response) ──
        if _RE["weather"].search(t):
            return ("I don't have a weather API, but you can check weather.com or ask me to open Chrome "
                    "and search for the weather."), False

        # ─ Wikipedia "what is / who is" queries ──────────────
        if _RE["what_is"].search(t):
            cleaned = re.sub(r"\b(what is|what are|who is|who was|tell me about|explain|define|describe)\b", "", t, flags=re.IGNORECASE).strip()
            return knowledge.find_answer(cleaned, prefer_wikipedia=True), False

        # ─ Explicit search ────────────────────────────────────
        if _RE["search"].search(t):
            cleaned = re.sub(r"\b(search for|look up|find|google|search)\b", "", t, flags=re.IGNORECASE).strip()
            return knowledge.find_answer(cleaned, prefer_wikipedia=False), False

        # ─ News ───────────────────────────────────────────────
        if _RE["news"].search(t):
            return knowledge.find_answer("latest news today", prefer_wikipedia=False), False

        # ─ Catch-all: treat anything else as a search query ───
        return knowledge.find_answer(t, prefer_wikipedia=True), False

    # ── Intent handlers ──────────────────────────────────────
    def _greet(self) -> str:
        hour = datetime.datetime.now().hour
        if 5 <= hour < 12:
            tod = "Good morning"
        elif 12 <= hour < 17:
            tod = "Good afternoon"
        elif 17 <= hour < 21:
            tod = "Good evening"
        else:
            tod = "Hey"
        return f"{tod}, {config.USER_NAME}! How can I help you today?"

    def _handle_open(self, text: str) -> str | None:
        for app_name in sorted(config.APP_COMMANDS, key=len, reverse=True):
            if app_name in text:
                return self.app_ctrl.open_app(app_name)
        return None

    def _handle_close(self, text: str) -> str | None:
        for app_name in sorted(config.PROCESS_NAMES, key=len, reverse=True):
            if app_name in text:
                return self.app_ctrl.close_app(app_name)
        return None

    def _handle_folder(self, text: str) -> str | None:
        for folder_name in sorted(config.FOLDER_COMMANDS, key=len, reverse=True):
            if folder_name in text:
                return self.app_ctrl.open_folder(folder_name)
        return None

    def _handle_remind(self, text: str) -> str:
        """
        Parse phrases like:
          "remind me to call mom at 8 pm"
          "remind me to take medicine at 14:30"
        """
        # Try to extract time patterns
        time_pattern = re.search(
            r"at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?",
            text, re.IGNORECASE
        )
        task_match = re.search(
            r"remind\s+me\s+to\s+(.+?)(?:\s+at\s+[\d:]+|\s*$)",
            text, re.IGNORECASE
        )

        if not task_match:
            return "What should I remind you about, and at what time?"

        task = task_match.group(1).strip()

        if time_pattern:
            hour   = int(time_pattern.group(1))
            minute = int(time_pattern.group(2)) if time_pattern.group(2) else 0
            meridiem = time_pattern.group(3)
            if meridiem and meridiem.lower() == "pm" and hour < 12:
                hour += 12
            elif meridiem and meridiem.lower() == "am" and hour == 12:
                hour = 0
            now = datetime.datetime.now()
            remind_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if remind_dt <= now:
                remind_dt += datetime.timedelta(days=1)  # schedule for tomorrow

            self.memory.add_reminder(task, remind_dt)
            time_str = remind_dt.strftime("%I:%M %p")
            return f"Got it! I'll remind you to '{task}' at {time_str}."
        else:
            return f"When should I remind you to '{task}'? Please say a time like 'at 8 pm'."

    def _list_reminders(self) -> str:
        reminders = self.memory.get_pending_reminders()
        if not reminders:
            return "You have no pending reminders."
        lines = []
        for r in reminders:
            dt = datetime.datetime.fromisoformat(r["remind_at"])
            lines.append(f"• {r['task']} — {dt.strftime('%A %I:%M %p')}")
        return "Your reminders:\n" + "\n".join(lines)

    def _handle_remember(self, text: str, match) -> str:
        # Extract everything after "remember that" or "remember"
        fact_match = re.search(
            r"remember\s+(?:that\s+)?(.+)", text, re.IGNORECASE
        )
        if fact_match:
            fact = fact_match.group(1).strip()
            self.memory.save_memory(fact)
            return f"I'll remember that: '{fact}'"
        return "What would you like me to remember?"

    def _handle_recall(self) -> str:
        memories = self.memory.get_all_memories()
        if not memories:
            return "I don't have anything saved in memory yet."
        lines = [f"• {m['content']}  (saved {m['saved_at'][:10]})" for m in memories]
        return "Here's what I remember:\n" + "\n".join(lines)

    def _try_calculate(self, text: str) -> str | None:
        """Safely evaluate simple arithmetic expressions."""
        # Strip known prefixes
        cleaned = re.sub(
            r"\b(calculate|what is|compute|how much is)\b", "", text, flags=re.IGNORECASE
        ).strip()

        # Must look like a math expression
        if not re.match(r"^[\d\s\+\-\*\/\^\(\)\.]+$", cleaned):
            return None

        try:
            # Replace ^ with ** for Python exponentiation
            expr   = cleaned.replace("^", "**")
            result = eval(expr, {"__builtins__": {}, "math": math})  # sandboxed eval
            return f"The answer is {result}."
        except Exception:
            return None
