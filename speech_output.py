# ============================================================
#  voice/speech_output.py — Text-to-Speech using pyttsx3
#  100 % offline, no internet needed
# ============================================================

import pyttsx3
import threading
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config


class Speaker:
    """
    Wraps pyttsx3 for natural-sounding offline TTS.
    A threading lock ensures only one utterance plays at a time.
    """

    def __init__(self):
        self._engine = pyttsx3.init()
        self._lock   = threading.Lock()
        self._apply_settings()

    def _apply_settings(self):
        """Apply rate, volume, and voice index from config."""
        self._engine.setProperty("rate",   config.TTS_RATE)
        self._engine.setProperty("volume", config.TTS_VOLUME)

        voices = self._engine.getProperty("voices")
        if voices and config.TTS_VOICE_INDEX < len(voices):
            self._engine.setProperty("voice", voices[config.TTS_VOICE_INDEX].id)
            print(f"[TTS] Voice: {voices[config.TTS_VOICE_INDEX].name}")
        else:
            print("[TTS] Using default system voice.")

    def say(self, text: str, print_text: bool = True):
        """
        Speak `text` aloud.
        - print_text=True  → also echoes to the console.
        - Thread-safe via internal lock.
        """
        if not text or not text.strip():
            return
        if print_text:
            print(f"\n🤖 {config.ASSISTANT_NAME}: {text}\n")
        with self._lock:
            self._engine.say(text)
            self._engine.runAndWait()

    def list_voices(self):
        """Utility: print every TTS voice installed on this machine."""
        voices = self._engine.getProperty("voices")
        print("\n=== Available TTS Voices ===")
        for i, v in enumerate(voices):
            print(f"  [{i}] {v.name}  —  {v.id}")
        print(f"\nChange TTS_VOICE_INDEX in config.py to switch voices.\n")