"""Image OCR helper used for ingredient labels and shopping-cart screenshots.

Uses Tesseract via pytesseract. Degrades gracefully if Tesseract is not
installed: callers can still pass text directly.
"""

from __future__ import annotations

import io
from functools import lru_cache


@lru_cache(maxsize=1)
def ocr_available() -> bool:
    try:
        import pytesseract  # type: ignore
        from PIL import Image  # noqa: F401

        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def image_to_text(image_bytes: bytes) -> str:
    """Extract text from image bytes. Returns '' if OCR is unavailable."""
    if not ocr_available():
        return ""
    import pytesseract  # type: ignore
    from PIL import Image

    image = Image.open(io.BytesIO(image_bytes))
    if image.mode != "RGB":
        image = image.convert("RGB")
    return pytesseract.image_to_string(image)


def split_cart_lines(text: str) -> list[str]:
    """Heuristically split OCR'd cart text into candidate product line items."""
    lines = []
    for raw in text.splitlines():
        line = raw.strip()
        # Drop obvious price/quantity-only or very short noise lines.
        if len(line) < 3:
            continue
        if line.replace(".", "").replace(",", "").replace("₹", "").isdigit():
            continue
        lines.append(line)
    return lines
