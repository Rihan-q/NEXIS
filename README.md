# 🤖 NEXIS — Free AI Voice Assistant for Windows

> *"What's up Rihan?"* — NEXIS greets you every time you start it.

A **100% free, offline-first** AI voice assistant built in Python.
No paid APIs. No cloud LLMs. No API keys. Everything runs locally.

------------------

## 📁 Project Structure

nexis_assistant/
├── main.py                   ← Entry point — run this
├── config.py                 ← All settings (your name, voice, app paths)
├── requirements.txt          ← pip dependencies
│
├── voice/
│   ├── speech_input.py       ← Mic → text  (SpeechRecognition)
│   └── speech_output.py      ← Text → speech  (pyttsx3)
│
├── brain/
│   ├── processor.py          ← Intent detection + command routing
│   └── knowledge.py          ← Wikipedia + DuckDuckGo search
│
├── memory/
│   └── storage.py            ← SQLite: memories & reminders
│
├── windows_control/
│   └── apps.py               ← Open/close apps, folders, system cmds
│
├── utils/
│   └── helpers.py            ← Banner, help text, text sanitizer
│
└── data/
    └── nexis.db             ← Auto-created SQLite database


--------------------

## ⚡ Quick Setup (Step-by-Step)

### Step 1 — Install Python
Make sure you have **Python 3.10(recomended) or newer** installed.
Download from: https://python.org/downloads/

Verify:

python --version
# Should print: Python 3.10.x or higher


### Step 2 — Clone / Download the project
Place the `nexis_assistant/` folder anywhere on your PC, e.g.:

C:\Users\Rihan\Desktop\nexis_assistant\

**To create a virtual environment**

python -m venv venv

# Active it by 

venv\Scripts\activate

### Step 3 — Install dependencies
Open a terminal **inside the project folder** and run:

pip install -r requirements.txt


   **PyAudio trouble on Windows?**
> If `python -m pip install PyAudio` fails, use the pre-built wheel:

> pip install pipwin
> pipwin install pyaudio

> Or download the correct `.whl` from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
> and install with: `pip install PyAudio‑0.2.14‑cp312‑cp312‑win_amd64.whl`

### Step 4 — (Optional) Set your voice
List available TTS voices on your machine:

python -c "import pyttsx3; e=pyttsx3.init(); [print(i, v.name) for i,v in enumerate(e.getProperty('voices'))]"

Then open `config.py` and set:

TTS_VOICE_INDEX = 1   # change to the index you prefer

Windows usually ships with "Microsoft David" (0) and "Microsoft Zira" (1).

### Step 5 — Run NEXIS!

python main.py


You should see the banner and hear:
> *"What's up Rihan? Good morning! How can I help you today?"*

---

## 🎙️ Voice Input Modes

| Mode | How | Notes |
|------|-----|-------|
| **Google** (default) | Mic → Google's free web API | Needs internet, very accurate |
| **Sphinx** (offline) | Mic → CMU Sphinx locally | 100% offline, less accurate |
| **Keyboard** | No mic? Type instead | Automatic fallback |

Switch modes in `config.py`:

SR_ENGINE = "google"   # or "sphinx"


For Sphinx offline mode:

pip install pocketsphinx



## 💬 What You Can Say

| Voice Command | What Happens |
|---|---|
| `"What's up"` / `"Hello"` | Friendly greeting |
| `"What time is it?"` | Current time |
| `"What's today's date?"` | Today's date |
| `"What is quantum computing?"` | Wikipedia search |
| `"Who was Albert Einstein?"` | Wikipedia search |
| `"Search for best Python tutorials"` | DuckDuckGo search |
| `"Open Chrome"` | Launches Chrome |
| `"Open VS Code"` | Launches VS Code |
| `"Open Downloads folder"` | Opens in Explorer |
| `"Close Chrome"` | Kills the process |
| `"Remind me to call mom at 8 pm"` | Saves timed reminder |
| `"List reminders"` | Shows pending reminders |
| `"Remember that my WiFi password is abc"` | Saves to memory |
| `"What do you remember?"` | Recalls saved memories |
| `"Clear memory"` | Deletes all memories |
| `"Calculate 25 * 4 + 10"` | Math result |
| `"Tell me a joke"` | Random programmer joke |
| `"Lock screen"` | Locks the PC |
| `"Volume up"` / `"Volume down"` | Audio control |
| `"Mute"` | Toggle mute |
| `"Screenshot"` | Saves to Desktop |
| `"Shutdown"` / `"Restart"` | System control |
| `"Help"` | Shows this list |
| `"Exit"` / `"Bye"` | Shuts down NEXIS |



## ⚙️ Customisation

### Add a new app
In `config.py`, add to `APP_COMMANDS`:

"discord": r"C:\Users\%USERNAME%\AppData\Local\Discord\app-1.0.9035\Discord.exe",

And to `PROCESS_NAMES`:

"discord": "Discord.exe",


### Change your name

USER_NAME = "YourName"   # in config.py


### Adjust voice speed

TTS_RATE = 165   # slower    (default: 175)
TTS_RATE = 200   # faster


---

## 🧰 Tech Stack (100% Free)

| Purpose            | Library                    | Cost          |
|--------------------|----------------------------|---------------|
| Text-to-Speech     | `pyttsx3`                  | Free, offline |
| Speech Recognition | `SpeechRecognition`        | Free          |
| Microphone         | `PyAudio`                  | Free, offline |
| Wikipedia          | `wikipedia`                | Free          |
| DuckDuckGo         | `duckduckgo-search`        | Free, no key  |
| Web scraping       | `requests + beautifulsoup4`| Free          |
| Database           | `sqlite3`                  | Free, built-in|
| Windows control    | `os + subprocess`          | Free, built-in|
| Threading          | `threading`                | Free, built-in|
-------------------------------------------------------------------

---

Troubleshooting

**"No microphone found"**
→ NEXIS automatically switches to keyboard input. Type your commands.

**DuckDuckGo returns no results**
→ Sometimes DDG rate-limits. Wait a moment and try again.
→ The `duckduckgo-search` library automatically retries with backoff.

**App not opening ("couldn't find")**
→ Check the path in `config.py → APP_COMMANDS`. The default paths are standard but your install may differ.

---

## ✅ Verification Checklist

- [x] 100% free — no paid services
- [x] No API keys required anywhere
- [x] Runs fully on Python
- [x] Offline-first (TTS + optional Sphinx STT are fully offline)
- [x] Greets with "What's up Rihan?"
- [x] Answers in 2–3 sentences max
- [x] Wikipedia + DuckDuckGo search
- [x] Opens/closes Windows apps
- [x] Persistent reminders (SQLite)
- [x] Persistent memory (SQLite)
- [x] Background reminder thread
- [x] Keyboard fallback if no mic

---

*Built with ❤️ using only open-source Python libraries.*
