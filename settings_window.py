"""
Simple settings window (tkinter) for adjusting hotkey, behavior toggles, and
history length. Opened from the tray menu.
"""
import tkinter as tk
from tkinter import ttk


def show_settings(cfg: dict, on_save):
    """
    Blocking (run in its own thread, each call creates its own Tk root so it
    can be opened repeatedly from the tray). `on_save` is called with the
    updated config dict when the user clicks Save.
    """
    root = tk.Tk()
    root.title("Image to Text Scanner - Settings")
    root.attributes("-topmost", True)
    root.geometry("420x360")
    root.resizable(False, False)

    pad = {"padx": 10, "pady": 6}

    auto_watch_var = tk.BooleanVar(value=cfg.get("auto_watch_clipboard", True))
    keep_image_var = tk.BooleanVar(value=cfg.get("keep_image_on_clipboard", False))
    show_preview_var = tk.BooleanVar(value=cfg.get("show_preview_popup", False))
    auto_format_var = tk.BooleanVar(value=cfg.get("auto_format_code_blocks", True))
    start_with_windows_var = tk.BooleanVar(value=cfg.get("start_with_windows", False))
    hotkey_var = tk.StringVar(value=cfg.get("hotkey", "<ctrl>+<shift>+x"))
    history_var = tk.StringVar(value=str(cfg.get("max_history_items", 50)))
    lang_var = tk.StringVar(value=cfg.get("ocr_language", "eng"))

    ttk.Checkbutton(root, text="Automatically OCR new screenshots on the clipboard",
                    variable=auto_watch_var).pack(anchor="w", **pad)
    ttk.Checkbutton(root, text="Keep the original image on the clipboard too",
                    variable=keep_image_var).pack(anchor="w", **pad)
    ttk.Checkbutton(root, text="Show a review/edit popup before copying text",
                    variable=show_preview_var).pack(anchor="w", **pad)
    ttk.Checkbutton(root, text="Auto-wrap code-looking text in a code block",
                    variable=auto_format_var).pack(anchor="w", **pad)
    ttk.Checkbutton(root, text="Start automatically with Windows",
                    variable=start_with_windows_var).pack(anchor="w", **pad)

    hotkey_frame = tk.Frame(root)
    hotkey_frame.pack(fill="x", **pad)
    tk.Label(hotkey_frame, text="Manual hotkey (re-run OCR on clipboard image):").pack(anchor="w")
    tk.Entry(hotkey_frame, textvariable=hotkey_var).pack(fill="x")
    tk.Label(hotkey_frame, text="Format example: <ctrl>+<shift>+x", fg="gray").pack(anchor="w")

    history_frame = tk.Frame(root)
    history_frame.pack(fill="x", **pad)
    tk.Label(history_frame, text="Max history items to keep:").pack(anchor="w")
    tk.Entry(history_frame, textvariable=history_var).pack(fill="x")

    lang_frame = tk.Frame(root)
    lang_frame.pack(fill="x", **pad)
    tk.Label(lang_frame, text="OCR language code (e.g. eng, fra, deu):").pack(anchor="w")
    tk.Entry(lang_frame, textvariable=lang_var).pack(fill="x")

    def do_save():
        cfg["auto_watch_clipboard"] = auto_watch_var.get()
        cfg["keep_image_on_clipboard"] = keep_image_var.get()
        cfg["show_preview_popup"] = show_preview_var.get()
        cfg["auto_format_code_blocks"] = auto_format_var.get()
        cfg["start_with_windows"] = start_with_windows_var.get()
        cfg["hotkey"] = hotkey_var.get().strip() or "<ctrl>+<shift>+x"
        try:
            cfg["max_history_items"] = max(1, int(history_var.get()))
        except ValueError:
            pass
        cfg["ocr_language"] = lang_var.get().strip() or "eng"
        on_save(cfg)
        root.destroy()

    button_frame = tk.Frame(root)
    button_frame.pack(fill="x", padx=10, pady=10)
    tk.Button(button_frame, text="Save", command=do_save).pack(side="right")
    tk.Button(button_frame, text="Cancel", command=root.destroy).pack(side="right", padx=(0, 6))

    root.mainloop()
