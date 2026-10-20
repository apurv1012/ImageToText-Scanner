"""
Registers (or removes) this app in the current user's Windows Startup folder,
so it launches automatically at sign-in.

Uses a .lnk shortcut in:
  %APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\
rather than a registry Run key, so it's visible/removable by the user via
Task Manager's Startup tab or by just deleting the shortcut — no hidden
registry edits.
"""
import os
import sys

import win32com.client

SHORTCUT_NAME = "ImageToTextScanner.lnk"


def _startup_folder():
    return os.path.join(
        os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup"
    )


def _shortcut_path():
    return os.path.join(_startup_folder(), SHORTCUT_NAME)


def _target_and_args():
    """
    If running as a frozen PyInstaller .exe, point straight at it.
    If running from source, point at pythonw.exe (no console window) with
    this folder's main.py as the argument.
    """
    if getattr(sys, "frozen", False):
        return sys.executable, ""
    python_dir = os.path.dirname(sys.executable)
    pythonw = os.path.join(python_dir, "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = sys.executable  # fall back to whatever's running this
    main_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
    return pythonw, f'"{main_py}"'


def is_enabled() -> bool:
    return os.path.exists(_shortcut_path())


def enable():
    os.makedirs(_startup_folder(), exist_ok=True)
    target, args = _target_and_args()
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(_shortcut_path())
    shortcut.TargetPath = target
    shortcut.Arguments = args
    shortcut.WorkingDirectory = os.path.dirname(os.path.abspath(__file__))
    shortcut.Description = "Image to Text Scanner"
    shortcut.Save()


def disable():
    path = _shortcut_path()
    if os.path.exists(path):
        os.remove(path)


def set_enabled(enabled: bool):
    if enabled:
        enable()
    else:
        disable()
