# ============================================================
#  windows_control/apps.py — Open / close Windows apps & folders
#  Uses only os, subprocess, and ctypes — zero third-party deps
# ============================================================

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config


class AppController:
    """
    Handles opening/closing applications and folders on Windows.
    All commands use built-in Windows mechanisms — no extra libraries.
    """

    # ── Open an application ──────────────────────────────────
    def open_app(self, app_name: str) -> str:
        app_name_lower = app_name.lower()
        path = config.APP_COMMANDS.get(app_name_lower)

        if not path:
            return f"I don't have a shortcut for '{app_name}'. You can add it to config.py."

        # Expand environment variables like %USERNAME%
        path = os.path.expandvars(path)

        try:
            # "ms-settings:" style URIs need os.startfile
            if path.startswith("ms-"):
                os.startfile(path)
            else:
                subprocess.Popen(
                    path,
                    shell              = True,   # shell=True handles spaces in paths
                    creationflags      = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                    stdout             = subprocess.DEVNULL,
                    stderr             = subprocess.DEVNULL,
                )
            return f"Opening {app_name}."
        except FileNotFoundError:
            return (f"Couldn't find '{app_name}'. "
                    f"Check the path in config.py: {path}")
        except Exception as e:
            return f"Failed to open {app_name}: {e}"

    # ── Close an application ─────────────────────────────────
    def close_app(self, app_name: str) -> str:
        app_name_lower = app_name.lower()
        process = config.PROCESS_NAMES.get(app_name_lower)

        if not process:
            return f"I don't know the process name for '{app_name}'. Add it to config.py."

        try:
            # /F = force-kill, /IM = by image name, /T = include children
            result = subprocess.run(
                ["taskkill", "/F", "/IM", process, "/T"],
                capture_output = True,
                text           = True,
            )
            if result.returncode == 0:
                return f"Closed {app_name}."
            else:
                return f"{app_name} doesn't seem to be running."
        except Exception as e:
            return f"Couldn't close {app_name}: {e}"

    # ── Open a folder ─────────────────────────────────────────
    def open_folder(self, folder_name: str) -> str:
        folder_name_lower = folder_name.lower()
        path = config.FOLDER_COMMANDS.get(folder_name_lower)

        if not path:
            return f"I don't have a shortcut for the '{folder_name}' folder."

        path = os.path.expandvars(path)

        try:
            os.startfile(path)   # Opens in File Explorer
            return f"Opening your {folder_name} folder."
        except Exception as e:
            return f"Couldn't open {folder_name}: {e}"

    # ── System controls ───────────────────────────────────────
    def lock_screen(self) -> str:
        try:
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
            return "Screen locked."
        except Exception as e:
            return f"Couldn't lock screen: {e}"

    def shutdown_pc(self) -> str:
        try:
            subprocess.run(["shutdown", "/s", "/t", "10"])
            return "PC will shut down in 10 seconds. Say 'cancel shutdown' to abort."
        except Exception as e:
            return f"Couldn't initiate shutdown: {e}"

    def restart_pc(self) -> str:
        try:
            subprocess.run(["shutdown", "/r", "/t", "10"])
            return "PC will restart in 10 seconds."
        except Exception as e:
            return f"Couldn't initiate restart: {e}"

    def sleep_pc(self) -> str:
        try:
            subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
            return "Putting the PC to sleep."
        except Exception as e:
            return f"Couldn't sleep: {e}"

    def take_screenshot(self) -> str:
        """Save screenshot to Desktop using the built-in Win32 API via ctypes."""
        try:
            # Use PowerShell's built-in screenshot capability — no extra deps
            desktop = os.path.expandvars(r"%USERPROFILE%\Desktop")
            filename = f"screenshot_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(desktop, filename)
            ps_cmd = (
                f"Add-Type -AssemblyName System.Windows.Forms; "
                f"$s=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds; "
                f"$b=New-Object System.Drawing.Bitmap($s.Width,$s.Height); "
                f"$g=[System.Drawing.Graphics]::FromImage($b); "
                f"$g.CopyFromScreen($s.Location,[System.Drawing.Point]::Empty,$s.Size); "
                f"$b.Save('{filepath}'); $g.Dispose(); $b.Dispose()"
            )
            subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True
            )
            return f"Screenshot saved to Desktop as {filename}."
        except Exception as e:
            return f"Screenshot failed: {e}"

    def volume_change(self, direction: str) -> str:
        """
        Adjust system volume using NirCmd (if installed) or PowerShell.
        direction: "up" | "down" | "mute"
        """
        try:
            # Uses PowerShell + Windows Audio COM object — no NirCmd needed
            if direction == "up":
                script = "(New-Object -com WScript.Shell).SendKeys([char]175)"   # VK_VOLUME_UP  ×5
                script = "(1..5) | % { (New-Object -com WScript.Shell).SendKeys([char]175) }"
            elif direction == "down":
                script = "(1..5) | % { (New-Object -com WScript.Shell).SendKeys([char]174) }"
            else:  # mute
                script = "(New-Object -com WScript.Shell).SendKeys([char]173)"

            subprocess.run(["powershell", "-Command", script], capture_output=True)

            if direction == "up":
                return "Volume increased."
            elif direction == "down":
                return "Volume decreased."
            else:
                return "Audio muted / unmuted."
        except Exception as e:
            return f"Volume control failed: {e}"
