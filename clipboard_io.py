"""
Windows clipboard access: detecting new images, reading the current clipboard
image, and writing extracted text (optionally alongside the original image).

Uses pywin32 directly rather than a generic cross-platform library, since we
need to distinguish "a new image was copied" from "nothing changed" and from
"text was copied" — a generic clipboard poller can't easily tell those apart.
"""
import io
import time

import win32clipboard
from PIL import Image


def get_clipboard_image():
    """Return a PIL Image if the clipboard currently holds a bitmap, else None."""
    try:
        win32clipboard.OpenClipboard()
        try:
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_DIB):
                data = win32clipboard.GetClipboardData(win32clipboard.CF_DIB)
                # CF_DIB data is a BMP file missing its 14-byte file header;
                # reconstruct a valid BMP so PIL can open it.
                bmp_header = b"BM" + (len(data) + 14).to_bytes(4, "little") + b"\x00\x00\x00\x00\x36\x00\x00\x00"
                return Image.open(io.BytesIO(bmp_header + data))
            return None
        finally:
            win32clipboard.CloseClipboard()
    except Exception:
        return None


def set_clipboard_text(text: str):
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, text)
    finally:
        win32clipboard.CloseClipboard()


class ClipboardImageWatcher:
    """
    Polls the clipboard's sequence number (a Windows-maintained counter that
    increments every time clipboard contents change) and fires a callback
    only when the new content is an image. Cheap, reliable, no hooks needed.
    """

    def __init__(self, on_new_image, poll_interval=0.5):
        self.on_new_image = on_new_image
        self.poll_interval = poll_interval
        self._last_sequence = None
        self._running = False

    def _get_sequence_number(self):
        return win32clipboard.GetClipboardSequenceNumber()

    def start(self, should_continue):
        """
        Blocking loop; call from a background thread.
        `should_continue` is a callable returning False to stop the loop.
        """
        self._running = True
        self._last_sequence = self._get_sequence_number()
        while should_continue():
            time.sleep(self.poll_interval)
            try:
                seq = self._get_sequence_number()
            except Exception:
                continue
            if seq != self._last_sequence:
                self._last_sequence = seq
                image = get_clipboard_image()
                if image is not None:
                    self.on_new_image(image)
