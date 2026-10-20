# Image-to-Text Scanner

A Windows system-tray app: take a screenshot anywhere, and the extracted text
is automatically put on your clipboard — ready to paste into an AI chat.

## How it works day to day

1. Launch the app (double-click `ImageToTextScanner.exe`, or `python main.py`).
   A notification confirms it's running and added to the tray.
2. Take a screenshot the normal way (`Win+Shift+S`, Snipping Tool, PrintScreen, etc.).
3. The app notices the new image on the clipboard and runs OCR automatically.
4. A small notification confirms the text was copied.
5. Alt-Tab to your AI chat and paste (`Ctrl+V`).

A manual hotkey (default `Ctrl+Shift+X`) re-runs OCR on whatever image is
currently on the clipboard, for when auto-watch is paused or missed something.

Right-click (or left-click, depending on Windows settings) the tray icon for:
Pause/Resume, Re-run OCR now, View history, Settings, Quit.

## 1. Install prerequisites

**Python 3.9+** — if not already installed, get it from
https://www.python.org/downloads/ (check "Add Python to PATH" during install).

**Tesseract OCR** (the actual OCR engine, runs fully offline) — install from
https://github.com/UB-Mannheim/tesseract/wiki (the Windows installer). Default
install location (`C:\Program Files\Tesseract-OCR\tesseract.exe`) is detected
automatically; otherwise make sure `tesseract.exe` is on your PATH.

## 2. Install Python dependencies

Open a command prompt in this folder and run:

```
pip install -r requirements.txt
```

## 3. Run it

```
python main.py
```

The tray icon should appear near the clock. Take a screenshot to try it out.

To make it start automatically with Windows: enable "Start automatically with
Windows" in the Settings window (tray icon → Settings), or manually place a
shortcut to the app in:
`shell:startup` (type that into the Windows Start menu's Run box to open the
folder).

## 4. (Optional) Package as a standalone .exe

So you don't need Python installed to run it day-to-day:

```
build_exe.bat
```

This uses PyInstaller to produce `dist\ImageToTextScanner.exe` — a single
file you can pin to Start or drop into `shell:startup`, already carrying the
app's icon (taskbar, shortcut, and tray all use it). Tesseract itself still
needs to be installed separately (step 1) since it's a native engine, not a
Python package.

If you ever want to redesign the icon, edit `generate_icon.py` and run
`python generate_icon.py` — it regenerates `icon.ico` and `icon_paused.ico`
(the dimmed version shown while watching is paused), then rebuild the `.exe`.

## Settings reference

| Setting | What it does |
|---|---|
| Automatically OCR new screenshots | Core auto-watch behavior. Turn off to only use the manual hotkey. |
| Keep original image on clipboard too | By default the image is replaced with the extracted text; enable this to keep both (text pasted via the app's history window instead). |
| Show review/edit popup before copying | Adds a quick-edit step so you can fix OCR mistakes before the text is copied. Off by default to keep the flow to one step. |
| Auto-wrap code-looking text in a code block | Detects code-like text (braces, semicolons, indentation) and wraps it in triple backticks. |
| Start automatically with Windows | Adds/removes a Startup shortcut. |
| Hotkey | Manual "re-run OCR on clipboard image" shortcut. |
| Max history items | How many past scans to keep locally. |
| OCR language | Tesseract language code — `eng` (English) by default. Install additional Tesseract language packs for others (e.g. `fra`, `deu`, `hin`). |

## Privacy

All OCR runs locally via Tesseract — screenshots and extracted text never
leave your machine. History (text + small thumbnails) is stored locally at
`%USERPROFILE%\.image_to_text_scanner\`.

## Project files

| File | Purpose |
|---|---|
| `main.py` | App entry point; wires everything together. |
| `clipboard_io.py` | Reads/writes the Windows clipboard; watches for new images. |
| `ocr_engine.py` | Runs Tesseract OCR and cleans up/formats the text. |
| `tray_icon.py` | System tray icon and menu. |
| `preview_popup.py` | Optional review/edit popup before copying. |
| `settings_window.py` | Settings dialog. |
| `history_window.py` | Scan history viewer. |
| `history.py` | Local history storage (JSON + thumbnails). |
| `config.py` | Settings storage (JSON). |
| `requirements.txt` | Python dependencies. |
| `build_exe.bat` | Packages the app into a standalone `.exe` via PyInstaller. |

## Troubleshooting

- **"Tesseract OCR isn't installed or isn't on PATH"** — install it (step 1)
  and restart the app.
- **Nothing happens after a screenshot** — check the tray icon isn't paused
  (grey icon = paused), and that "Automatically OCR new screenshots" is on
  in Settings.
- **OCR text looks wrong/garbled** — Tesseract works best on clear,
  reasonably high-resolution text; very small or stylized text may need a
  closer screenshot crop.
