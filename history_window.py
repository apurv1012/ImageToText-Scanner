"""
Scan history viewer: a searchable list of past OCR results. Double-click (or
select + "Copy selected") puts that entry's text back on the clipboard.
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime

import history
from clipboard_io import set_clipboard_text


def show_history():
    root = tk.Tk()
    root.title("Image to Text Scanner - History")
    root.attributes("-topmost", True)
    root.geometry("520x420")

    search_var = tk.StringVar()
    search_entry = tk.Entry(root, textvariable=search_var)
    search_entry.pack(fill="x", padx=8, pady=(8, 4))
    search_entry.focus_set()

    listbox = tk.Listbox(root, font=("Segoe UI", 10))
    listbox.pack(fill="both", expand=True, padx=8, pady=4)

    entries_ref = {"items": []}

    def refresh(*_):
        query = search_var.get()
        items = history.search(query)
        entries_ref["items"] = items
        listbox.delete(0, "end")
        for e in items:
            ts = datetime.fromtimestamp(e["timestamp"]).strftime("%Y-%m-%d %H:%M")
            preview = e["text"].replace("\n", " ")[:70]
            listbox.insert("end", f"[{ts}]  {preview}")

    search_var.trace_add("write", refresh)
    refresh()

    def copy_selected():
        sel = listbox.curselection()
        if not sel:
            return
        entry = entries_ref["items"][sel[0]]
        set_clipboard_text(entry["text"])
        status_label.config(text="Copied to clipboard.")

    def clear_all():
        history.clear()
        refresh()
        status_label.config(text="History cleared.")

    listbox.bind("<Double-Button-1>", lambda e: copy_selected())

    button_frame = tk.Frame(root)
    button_frame.pack(fill="x", padx=8, pady=8)
    tk.Button(button_frame, text="Copy selected", command=copy_selected).pack(side="left")
    tk.Button(button_frame, text="Clear history", command=clear_all).pack(side="left", padx=6)
    tk.Button(button_frame, text="Close", command=root.destroy).pack(side="right")

    status_label = tk.Label(root, text="", fg="gray")
    status_label.pack(anchor="w", padx=8, pady=(0, 6))

    root.mainloop()
