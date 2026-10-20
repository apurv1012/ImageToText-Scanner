"""
OCR engine wrapper.

Uses Tesseract OCR (via pytesseract) running fully locally/offline — nothing
in the screenshot ever leaves the machine. Includes light post-processing to
make the extracted text paste-ready for an AI chat prompt.
"""
import re
import shutil

import pytesseract
from PIL import Image


class OcrError(Exception):
    pass


def _find_tesseract():
    """Try to locate the tesseract binary; raise a clear error if missing."""
    exe = shutil.which("tesseract")
    if exe:
        pytesseract.pytesseract.tesseract_cmd = exe
        return
    # Common default install path on Windows
    import os
    default_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(default_path):
        pytesseract.pytesseract.tesseract_cmd = default_path
        return
    raise OcrError(
        "Tesseract OCR isn't installed or isn't on PATH. "
        "Install it from https://github.com/UB-Mannheim/tesseract/wiki "
        "and either add it to PATH or install to the default location."
    )


def _looks_like_code(text: str) -> bool:
    """Heuristic: does this text look like source code rather than prose?"""
    if not text.strip():
        return False
    lines = text.splitlines()
    indicator_hits = 0
    code_symbols = ("{", "}", ";", "=>", "def ", "function ", "const ", "import ",
                    "class ", "</", "->", "    ", "\t", "#include", "public ", "private ")
    for line in lines:
        if any(sym in line for sym in code_symbols):
            indicator_hits += 1
    # If a meaningful fraction of lines look code-y, treat the whole block as code.
    return len(lines) > 0 and (indicator_hits / len(lines)) >= 0.3


def _clean_text(raw: str) -> str:
    """Strip common OCR artifacts: stray whitespace, trailing spaces, blank-line runs."""
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    # collapse runs of 3+ blank lines down to 1
    text = re.sub(r"\n{3,}", "\n\n", text)
    # strip trailing whitespace on each line
    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines).strip("\n")
    return text


def extract_text(image: Image.Image, language: str = "eng", auto_format_code: bool = True) -> str:
    """
    Run OCR on a PIL Image and return cleaned, paste-ready text.
    Raises OcrError if Tesseract isn't available or OCR fails.
    """
    _find_tesseract()
    try:
        raw = pytesseract.image_to_string(image, lang=language)
    except pytesseract.TesseractError as e:
        raise OcrError(f"OCR failed: {e}") from e

    cleaned = _clean_text(raw)

    if not cleaned:
        return ""

    if auto_format_code and _looks_like_code(cleaned):
        return f"```\n{cleaned}\n```"

    return cleaned
