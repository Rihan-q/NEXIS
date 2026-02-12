# ============================================================
#  voice/speech_input.py — Microphone → text
#  Uses SpeechRecognition library.
#  Primary engine : Google (free, needs internet)
#  Fallback       : text input from keyboard
# ============================================================

import speech_recognition as sr
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config


class Listener:
    """
    Captures microphone audio and converts it to text.
    Falls back to keyboard input if the mic is unavailable.
    """

    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Adjust energy threshold for background noise sensitivity
        self.recognizer.energy_threshold        = config.SR_ENERGY_THRESHOLD
        self.recognizer.dynamic_energy_threshold = True   # auto-adjusts to ambient noise
        self.recognizer.pause_threshold          = 0.8    # seconds of silence = end of phrase

        # Test mic availability once at startup
        self.mic_available = self._check_mic()

    def _check_mic(self) -> bool:
        try:
            with sr.Microphone() as _:
                pass
            print("[MIC] Microphone detected ✓")
            return True
        except (OSError, AttributeError):
            print("[MIC] No microphone found — keyboard mode activated.")
            return False

    def _transcribe(self, audio) -> str | None:
        """Send audio to the configured recognition engine."""
        engine = config.SR_ENGINE.lower()
        try:
            if engine == "google":
                # Free — uses Google's public Speech API, no key needed
                return self.recognizer.recognize_google(audio)
            elif engine == "sphinx":
                # 100 % offline (requires:  pip install pocketsphinx)
                return self.recognizer.recognize_sphinx(audio)
            else:
                print(f"[SR] Unknown engine '{engine}', falling back to Google.")
                return self.recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return None          # Speech detected but not understood
        except sr.RequestError as e:
            print(f"[SR] Recognition service error: {e}")
            return None

    
    def listen(self) -> str:
        """
        Capture one utterance from the mic (or keyboard if no mic).
        Returns the recognised text in lowercase, stripped.
        """
        if not self.mic_available:
            return self._keyboard_input()

        print("🎤 Listening…")
        try:
            with sr.Microphone() as source:
                # Brief ambient-noise calibration on each call keeps accuracy high
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(
                    source,
                    timeout           = config.SR_TIMEOUT,
                    phrase_time_limit = config.SR_PHRASE_TIME_LIMIT,
                )
            text = self._transcribe(audio)
            if text:
                text = text.strip().lower()
                print(f"👤 You said: \"{text}\"")
                return text
            else:
                print("[SR] Could not understand audio.")
                return ""
        except sr.WaitTimeoutError:
            print("[SR] No speech detected (timeout).")
            return ""
        except Exception as e:
            print(f"[SR] Unexpected error: {e}")
            return self._keyboard_input()

    @staticmethod
    def _keyboard_input() -> str:
        """Fallback: read text from the console."""
        try:
            text = input("⌨️  Type your command: ").strip().lower()
            return text
        except (EOFError, KeyboardInterrupt):
            return "exit"