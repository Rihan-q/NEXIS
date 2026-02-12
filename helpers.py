# ============================================================
#  utils/helpers.py — Small utility functions used across modules
# ============================================================

import re
import os
import sys
import datetime


def clear_screen():
    """Clear the terminal (cross-platform)."""
    os.system("cls" if sys.platform == "win32" else "clear")


def print_banner(name: str):
    """Print a startup banner."""
    width = 56
    line  = "─" * width
    print(f"\n{'─' * width}")
    print(f"  🤖  {name} — AI Voice Assistant")
    print(f"  ⚡  Powered by free & open-source libraries")
    print(f"  📅  {datetime.datetime.now().strftime('%A, %B %d %Y  %I:%M %p')}")
    print(f"{'─' * width}\n")
    print("  Say 'exit' or 'bye' to quit.")
    print("  Say 'help' to see what I can do.\n")
    print(f"{'─' * width}\n")


HELP_TEXT = """
📋  WHAT I CAN DO:
─────────────────────────────────────────────────────
  🕐  "What time is it?"              → Current time
  📅  "What's today's date?"          → Today's date
  📖  "What is black holes?"          → Wikipedia search
  🌐  "Search for Python tutorials"   → DuckDuckGo search
  📂  "Open Chrome"                   → Launch app
  📁  "Open Downloads folder"         → Open folder
  ❌  "Close Chrome"                  → Kill process
  ⏰  "Remind me to call mom at 8 pm" → Set reminder
  🧠  "Remember that my WiFi is X"    → Save memory
  📝  "What do you remember?"         → Recall memory
  🃏  "Tell me a joke"                → Random joke
  🔢  "Calculate 25 * 4"              → Math
  🔒  "Lock screen"                   → Lock PC
  💤  "Sleep the computer"            → Sleep PC
  🔁  "Restart"                       → Reboot
  🔉  "Volume up" / "Volume down"     → Audio
  📸  "Screenshot"                    → Save screenshot
─────────────────────────────────────────────────────
"""


def print_help():
    print(HELP_TEXT)


def sanitize_for_speech(text: str) -> str:
    """
    Clean text before passing to TTS — remove markdown, URLs, etc.
    so the speech sounds natural.
    """
    # Strip URLs
    text = re.sub(r"https?://\S+", "", text)
    # Strip markdown bold/italic
    text = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", text)
    # Strip markdown headers
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Remove bullet characters
    text = re.sub(r"^[•\-\*]\s+", "", text, flags=re.MULTILINE)
    return text


def timestamp_now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")