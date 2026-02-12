# ============================================================
#  main.py — NEXIS AI Voice Assistant  (entry point)
#
#  COMPLETELY FREE — No paid APIs, no cloud LLMs, no API keys.
#  Uses: pyttsx3 · SpeechRecognition · wikipedia · duckduckgo_search
#        sqlite3 · subprocess · threading
#
#  Run: python main.py
# ============================================================

import sys
import os
import datetime
import threading

# ── Make sure all sub-packages are importable from project root ──
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

import config
from voice.speech_input    import Listener
from voice.speech_output   import Speaker
from brain.processor       import Brain
from memory.storage        import MemoryStore, ReminderThread
from windows_control.apps  import AppController
from utils.helpers         import print_banner, print_help, sanitize_for_speech


# ── Bootstrap ─────────────────────────────────────────────────
def initialize():
    """Create and wire up all components."""
    print("[BOOT] Initialising NEXIS…")

    speaker    = Speaker()
    listener   = Listener()
    memory     = MemoryStore(config.DB_PATH)
    app_ctrl   = AppController()
    brain      = Brain(memory, app_ctrl)

    # Reminder thread: fires callbacks when due reminders are found
    reminder_thread = ReminderThread(
        memory   = memory,
        callback = lambda msg: speaker.say(sanitize_for_speech(msg)),
    )
    reminder_thread.start()

    return speaker, listener, brain, reminder_thread


# ── Startup greeting ──────────────────────────────────────────
def greet(speaker: Speaker):
    """
    Say the required personalised greeting exactly as specified.
    """
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        greeting = f"What's up {config.USER_NAME}? Good morning! How can I help you today?"
    elif 12 <= hour < 17:
        greeting = f"What's up {config.USER_NAME}? Good afternoon! What can I do for you?"
    elif 17 <= hour < 21:
        greeting = f"What's up {config.USER_NAME}? Good evening! Ready to assist."
    else:
        greeting = f"What's up {config.USER_NAME}? Working late? I'm here to help!"

    speaker.say(greeting)


# ── Main loop ─────────────────────────────────────────────────
def run():
    """Primary event loop: listen → process → speak → repeat."""
    print_banner(config.ASSISTANT_NAME)

    speaker, listener, brain, reminder_thread = initialize()

    greet(speaker)

    while True:
        try:
            # 1. Get input (voice or keyboard)
            user_input = listener.listen()

            if not user_input:
                continue

            # 2. Handle "help" locally so we don't waste a search call
            if user_input.strip() in ("help", "help me", "what can you do", "commands"):
                print_help()
                speaker.say("I can search Wikipedia and the web, open apps, set reminders, "
                             "remember things, do maths, and control your Windows PC. "
                             "Check the terminal for the full list.")
                continue

            # 3. Respect wake word (if configured)
            if config.WAKE_WORD:
                if config.WAKE_WORD.lower() not in user_input:
                    continue   # silently ignore — waiting for wake word
                # Strip the wake word from the query before processing
                user_input = user_input.replace(config.WAKE_WORD.lower(), "").strip()

            # 4. Let the brain process the command
            response, should_exit = brain.process(user_input)

            # 5. Speak the response
            clean_response = sanitize_for_speech(response)
            speaker.say(clean_response)

            # 6. Exit if the brain says so (bye / exit commands)
            if should_exit:
                break

        except KeyboardInterrupt:
            speaker.say(f"Interrupted! Goodbye, {config.USER_NAME}.")
            break
        except Exception as e:
            print(f"[ERROR] Unexpected error in main loop: {e}")
            speaker.say("Something went wrong. Please try again.")
            continue

    # ── Cleanup ───────────────────────────────────────────────
    reminder_thread.stop()
    print("\n[BOOT] NEXIS shut down. Goodbye!\n")


# ── Entry ─────────────────────────────────────────────────────
if __name__ == "__main__":
    run()