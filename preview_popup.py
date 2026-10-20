"""
Optional tiny always-on-top popup for reviewing/editing OCR text before it's
copied to the clipboard. Only shown when the user enables
"show_preview_popup" in settings — off by default so the common flow stays
one step (screenshot -> clipboard).
"""
import tkinter as tk


def show_preview_and_get_text(initial_text: str):
    """
    Blocking (must be called from the main/UI thread or its own thread with
    its own Tk mainloop). Returns the (possibly edited) text, or None if the
    user cancelled.
    """
    result = {"text": None}

    root = tk.Tk()
    root.title("Image to Text - Review")
    root.attributes("-topmost", True)
    root.geometry("480x320")

    text_box = tk.Text(root, wrap="word", font=("Consolas", 10))
    text_box.insert("1.0", initial_text)
    text_box.pack(fill="both", expand=True, padx=8, pady=8)
    text_box.focus_set()

    button_frame = tk.Frame(root)
    button_frame.pack(fill="x", padx=8, pady=(0, 8))

    def on_copy():
        result["text"] = text_box.get("1.0", "end-1c")
        root.destroy()

    def on_cancel():
        result["text"] = None
        root.destroy()

    tk.Button(button_frame, text="Copy to clipboard", command=on_copy).pack(side="right", padx=(4, 0))
    tk.Button(button_frame, text="Cancel", command=on_cancel).pack(side="right")

    root.mainloop()
    return result["text"]
