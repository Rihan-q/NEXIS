# ============================================================
#  config.py — All global settings for your Jarvis assistant
# ============================================================

# ─── Personal ──────────────────────────────────────────────
USER_NAME       = "Rihan"       # The assistant greets this name
ASSISTANT_NAME  = "NEXIS"      # Assistant identity 
#Holds N.E.X.I.S – Neural Executive Intelligence System

# ─── Voice / TTS ───────────────────────────────────────────
TTS_RATE         = 175      # Words-per-minute (150-190 feels natural)
TTS_VOLUME       = 1.0      # 0.0 → 1.0
TTS_VOICE_INDEX  = 0        # 0 = first system voice  (see README for how to list voices)

# ─── Speech Recognition ────────────────────────────────────
SR_ENGINE             = "google"  # "google" (free online) or "sphinx" (offline, needs pocketsphinx)
SR_TIMEOUT            = 5         # seconds to wait for speech start
SR_PHRASE_TIME_LIMIT  = 10        # max seconds per utterance
SR_ENERGY_THRESHOLD   = 300       # mic sensitivity

# ─── Knowledge search ──────────────────────────────────────
WIKIPEDIA_SENTENCES  = 3   # sentences pulled from Wikipedia
DDG_MAX_RESULTS      = 5   # DuckDuckGo results to consider
ANSWER_MAX_SENTENCES = 2   # trim final answer to N sentences

# ─── Memory / Reminders ────────────────────────────────────
DB_PATH = "data/jarvis.db"   # SQLite path (relative to project root)

# ─── Windows app shortcuts ─────────────────────────────────
APP_COMMANDS = {
    "chrome"              : r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "google chrome"       : r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "firefox"             : r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "notepad"             : "notepad.exe",
    "calculator"          : "calc.exe",
    "vs code"             : r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "vscode"              : r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "visual studio code"  : r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "file explorer"       : "explorer.exe",
    "task manager"        : "taskmgr.exe",
    "settings"            : "ms-settings:",
    "paint"               : "mspaint.exe",
    "cmd"                 : "cmd.exe",
    "command prompt"      : "cmd.exe",
    "powershell"          : "powershell.exe",
    "spotify"             : r"C:\Users\%USERNAME%\AppData\Roaming\Spotify\Spotify.exe",
    "word"                : r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel"               : r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "vlc"                 : r"C:\Program Files\VideoLAN\VLC\vlc.exe",
}

FOLDER_COMMANDS = {
    "downloads"   : r"%USERPROFILE%\Downloads",
    "documents"   : r"%USERPROFILE%\Documents",
    "desktop"     : r"%USERPROFILE%\Desktop",
    "pictures"    : r"%USERPROFILE%\Pictures",
    "music"       : r"%USERPROFILE%\Music",
    "videos"      : r"%USERPROFILE%\Videos",
}

PROCESS_NAMES = {
    "chrome"           : "chrome.exe",
    "google chrome"    : "chrome.exe",
    "firefox"          : "firefox.exe",
    "notepad"          : "notepad.exe",
    "calculator"       : "Calculator.exe",
    "vs code"          : "Code.exe",
    "vscode"           : "Code.exe",
    "spotify"          : "Spotify.exe",
    "vlc"              : "vlc.exe",
    "word"             : "WINWORD.EXE",
    "excel"            : "EXCEL.EXE",
}

WAKE_WORD = None   # e.g. "NEXIS" — set None to respond to all input