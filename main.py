"""
Image-to-Text Scanner — entry point.

Runs as a system tray app. Watches the Windows clipboard for new screenshots,
OCRs them automatically, and puts clean, paste-ready text back on the
clipboard so it's one Alt+Tab + Ctrl+V away from your AI chat.

Run with:  python main.py
Package with PyInstaller for a double-clickable .exe (see README.md).
"""
import threading
import traceback

from pynput import keyboard

import config as config_module
import history
import startup
from clipboard_io import ClipboardImageWatcher, get_clipboard_image, set_clipboard_text
from ocr_engine import extract_text, OcrError
from tray_icon import TrayApp
from preview_popup import show_preview_and_get_text
from settings_window import show_settings
from history_window import show_history


class ScannerApp:
    def __init__(self):
        self.cfg = config_module.load_config()
        self._running = True
        self._watcher_thread = None
        self._hotkey_listener = None

        self.tray = TrayApp(
            cfg=self.cfg,
            on_toggle_pause=self.toggle_pause,
            on_open_settings=self.open_settings,
            on_open_history=self.open_history,
            on_rerun_ocr=self.rerun_ocr_on_current_clipboard,
            on_quit=self.quit,
        )

    # ---- core OCR flow -------------------------------------------------

    def _process_image(self, image):
        try:
            text = extract_text(
                image,
                language=self.cfg.get("ocr_language", "eng"),
                auto_format_code=self.cfg.get("auto_format_code_blocks", True),
            )
        except OcrError as e:
            self.tray.notify(str(e), title="OCR error")
            return
        except Exception:
            traceback.print_exc()
            self.tray.notify("Something went wrong reading that image.", title="OCR error")
            return

        if not text.strip():
            self.tray.notify("No text found in that image.")
            return

        if self.cfg.get("show_preview_popup", False):
            edited = show_preview_and_get_text(text)
            if edited is None:
                return  # user cancelled
            text = edited

        if not self.cfg.get("keep_image_on_clipboard", False):
            set_clipboard_text(text)

        history.add_entry(text, image, max_items=self.cfg.get("max_history_items", 50))

        preview = text.replace("\n", " ")[:80]
        self.tray.notify(f"Text copied: {preview}", title="Image to Text Scanner")

    def _on_new_clipboard_image(self, image):
        if self.cfg.get("paused", False) or not self.cfg.get("auto_watch_clipboard", True):
            return
        self._process_image(image)

    def rerun_ocr_on_current_clipboard(self):
        image = get_clipboard_image()
        if image is None:
            self.tray.notify("No image currently on the clipboard.")
            return
        self._process_image(image)

    # ---- tray actions ----------------------------------------------------

    def toggle_pause(self):
        self.cfg["paused"] = not self.cfg.get("paused", False)
        config_module.save_config(self.cfg)

    def open_settings(self):
        def _run():
            show_settings(dict(self.cfg), self._on_settings_saved)
        threading.Thread(target=_run, daemon=True).start()

    def _on_settings_saved(self, new_cfg):
        self.cfg.update(new_cfg)
        config_module.save_config(self.cfg)
        self._restart_hotkey_listener()
        self._sync_startup_shortcut()
        self.tray.refresh()

    def _sync_startup_shortcut(self):
        """Make the actual Windows Startup shortcut match the saved setting."""
        try:
            startup.set_enabled(self.cfg.get("start_with_windows", False))
        except Exception:
            traceback.print_exc()
            self.tray.notify(
                "Couldn't update the Windows Startup shortcut. "
                "You can add/remove it manually in shell:startup."
            )

    def open_history(self):
        threading.Thread(target=show_history, daemon=True).start()

    def quit(self):
        self._running = False
        if self._hotkey_listener:
            self._hotkey_listener.stop()

    # ---- background threads ----------------------------------------------

    def _start_clipboard_watcher(self):
        watcher = ClipboardImageWatcher(on_new_image=self._on_new_clipboard_image)
        self._watcher_thread = threading.Thread(
            target=watcher.start, args=(lambda: self._running,), daemon=True
        )
        self._watcher_thread.start()

    def _restart_hotkey_listener(self):
        if self._hotkey_listener:
            self._hotkey_listener.stop()
        hotkey = self.cfg.get("hotkey", "<ctrl>+<shift>+x")
        try:
            self._hotkey_listener = keyboard.GlobalHotKeys({
                hotkey: self.rerun_ocr_on_current_clipboard
            })
            self._hotkey_listener.start()
        except Exception:
            traceback.print_exc()
            self.tray.notify(f"Couldn't register hotkey '{hotkey}'. Check the format in Settings.")

    def _announce_ready(self):
        self.tray.notify(
            "Added to the system tray. Take a screenshot and the text "
            "will be copied automatically.",
            title="Image to Text Scanner is running",
        )

    def run(self):
        self._sync_startup_shortcut()
        self._start_clipboard_watcher()
        self._restart_hotkey_listener()
        self.tray.run(on_ready=self._announce_ready)  # blocks until quit


if __name__ == "__main__":
    ScannerApp().run()
