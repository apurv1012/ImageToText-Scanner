"""
Configuration management for Image-to-Text Scanner.

Settings are stored as plain JSON next to the app so they're easy to inspect
or edit by hand if needed. Defaults are sane for a first run.
"""
import json
import os

APP_DIR = os.path.join(os.path.expanduser("~"), ".image_to_text_scanner")
CONFIG_PATH = os.path.join(APP_DIR, "config.json")
HISTORY_PATH = os.path.join(APP_DIR, "history.json")
HISTORY_IMAGES_DIR = os.path.join(APP_DIR, "history_images")

DEFAULTS = {
    "hotkey": "<ctrl>+<shift>+x",   # manual "re-run OCR on clipboard" hotkey
    "auto_watch_clipboard": True,    # auto-OCR whenever a new image appears on clipboard
    "keep_image_on_clipboard": False,  # False = replace clipboard image with text
    "show_preview_popup": False,     # quick-edit popup before copying
    "auto_format_code_blocks": True,  # wrap code-looking text in ``` fences
    "max_history_items": 50,
    "ocr_language": "eng",
    "start_with_windows": False,
    "paused": False,
}


def ensure_app_dir():
    os.makedirs(APP_DIR, exist_ok=True)
    os.makedirs(HISTORY_IMAGES_DIR, exist_ok=True)


def load_config():
    ensure_app_dir()
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULTS)
        return dict(DEFAULTS)
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = dict(DEFAULTS)
        merged.update(data)
        return merged
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULTS)


def save_config(cfg):
    ensure_app_dir()
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
