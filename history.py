"""
Local, searchable scan history. Stores the extracted text plus a thumbnail of
the source screenshot so you can find and re-copy something from earlier,
even if you alt-tabbed away before pasting it.
"""
import json
import os
import time
import uuid

from PIL import Image

from config import HISTORY_PATH, HISTORY_IMAGES_DIR, ensure_app_dir


def _load_raw():
    ensure_app_dir()
    if not os.path.exists(HISTORY_PATH):
        return []
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save_raw(items):
    ensure_app_dir()
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)


def add_entry(text: str, image: Image.Image, max_items: int = 50):
    """Save a new history entry (text + a small thumbnail), trimming old ones."""
    ensure_app_dir()
    items = _load_raw()

    entry_id = uuid.uuid4().hex[:12]
    thumb_path = os.path.join(HISTORY_IMAGES_DIR, f"{entry_id}.png")

    try:
        thumb = image.copy()
        thumb.thumbnail((320, 320))
        thumb.save(thumb_path, format="PNG")
    except Exception:
        thumb_path = None

    items.insert(0, {
        "id": entry_id,
        "timestamp": time.time(),
        "text": text,
        "thumbnail": thumb_path,
    })

    # Trim and clean up old thumbnails beyond the cap
    while len(items) > max_items:
        old = items.pop()
        if old.get("thumbnail") and os.path.exists(old["thumbnail"]):
            try:
                os.remove(old["thumbnail"])
            except OSError:
                pass

    _save_raw(items)
    return entry_id


def list_entries():
    return _load_raw()


def search(query: str):
    query = query.lower().strip()
    if not query:
        return list_entries()
    return [e for e in list_entries() if query in e["text"].lower()]


def get_text(entry_id: str):
    for e in list_entries():
        if e["id"] == entry_id:
            return e["text"]
    return None


def clear():
    items = _load_raw()
    for e in items:
        if e.get("thumbnail") and os.path.exists(e["thumbnail"]):
            try:
                os.remove(e["thumbnail"])
            except OSError:
                pass
    _save_raw([])
