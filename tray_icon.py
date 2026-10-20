"""
System tray icon, menu and notifications (pystray + Pillow).
"""
import os
import sys

from PIL import Image, ImageDraw
import pystray


def _resource_path(filename):
    """Find a bundled file whether running from source or a PyInstaller .exe."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS  # PyInstaller's temp extraction dir
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, filename)


def _make_icon_image(paused=False):
    """Load the designed icon.ico/icon_paused.ico; fall back to a drawn glyph
    if the icon files are missing for some reason."""
    filename = "icon_paused.ico" if paused else "icon.ico"
    path = _resource_path(filename)
    if os.path.exists(path):
        try:
            return Image.open(path).convert("RGBA")
        except Exception:
            pass

    # Fallback: simple drawn glyph so the app still runs without icon.ico
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    bg = (120, 120, 120, 255) if paused else (40, 120, 220, 255)
    draw.rounded_rectangle([2, 2, size - 2, size - 2], radius=14, fill=bg)
    draw.rectangle([16, 16, 48, 24], fill=(255, 255, 255, 255))
    draw.rectangle([28, 16, 36, 48], fill=(255, 255, 255, 255))
    return img


class TrayApp:
    def __init__(self, cfg, on_toggle_pause, on_open_settings, on_open_history,
                 on_rerun_ocr, on_quit):
        self.cfg = cfg
        self.on_toggle_pause = on_toggle_pause
        self.on_open_settings = on_open_settings
        self.on_open_history = on_open_history
        self.on_rerun_ocr = on_rerun_ocr
        self.on_quit = on_quit
        self.icon = pystray.Icon(
            "image_to_text_scanner",
            icon=_make_icon_image(paused=cfg.get("paused", False)),
            title=self._title(),
            menu=self._build_menu(),
        )

    def _title(self):
        state = "Paused" if self.cfg.get("paused") else "Watching clipboard"
        return f"Image to Text Scanner — {state}"

    def _build_menu(self):
        return pystray.Menu(
            pystray.MenuItem(
                lambda item: "Resume watching" if self.cfg.get("paused") else "Pause watching",
                self._handle_toggle_pause,
            ),
            pystray.MenuItem("Re-run OCR on clipboard image now", lambda item: self.on_rerun_ocr()),
            pystray.MenuItem("View history...", lambda item: self.on_open_history()),
            pystray.MenuItem("Settings...", lambda item: self.on_open_settings()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", lambda item: self._handle_quit()),
        )

    def _handle_toggle_pause(self, item):
        self.on_toggle_pause()
        self.refresh()

    def _handle_quit(self):
        self.on_quit()
        self.icon.stop()

    def refresh(self):
        self.icon.icon = _make_icon_image(paused=self.cfg.get("paused", False))
        self.icon.title = self._title()

    def notify(self, message, title="Image to Text Scanner"):
        try:
            self.icon.notify(message, title)
        except Exception:
            pass  # notifications are a nicety, never fatal

    def run(self, on_ready=None):
        """
        `on_ready`, if given, is called once the tray icon is actually visible
        (pystray's `setup` hook) — the right place to fire a "started
        successfully" notification, since notifying before the icon exists
        would silently do nothing.
        """
        def _setup(icon):
            icon.visible = True
            if on_ready:
                try:
                    on_ready()
                except Exception:
                    pass

        self.icon.run(setup=_setup)

    def stop(self):
        self.icon.stop()
