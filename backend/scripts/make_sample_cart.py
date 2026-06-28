"""Generates a sample shopping-cart screenshot for demoing the cart analyser."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def _font(size: int):
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


ITEMS = [
    ("Maggi 2-Minute Masala Noodles", "Pack of 12", "Rs 144"),
    ("Kurkure Masala Munch", "90 g", "Rs 20"),
    ("Lay's Classic Salted Chips", "52 g", "Rs 20"),
    ("Thums Up Cola", "750 ml", "Rs 40"),
    ("Amul Taaza Toned Milk", "1 L", "Rs 76"),
]


def main(out: str) -> None:
    W, H = 760, 720
    img = Image.new("RGB", (W, H), "#f4f5f7")
    d = ImageDraw.Draw(img)

    d.rectangle([0, 0, W, 90], fill="#1faa59")
    d.text((28, 30), "QuickCart  -  My Basket", font=_font(30), fill="white")

    y = 120
    for name, qty, price in ITEMS:
        d.rounded_rectangle([24, y, W - 24, y + 96], radius=14, fill="white", outline="#e2e5ea")
        d.rectangle([44, y + 20, 100, y + 76], fill="#eef1f5")
        d.text((120, y + 22), name, font=_font(24), fill="#1b2330")
        d.text((120, y + 56), qty, font=_font(18), fill="#7a8699")
        d.text((W - 150, y + 36), price, font=_font(24), fill="#1b2330")
        y += 116

    d.text((28, y + 10), "Total: Rs 300", font=_font(26), fill="#1b2330")
    img.save(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "sample_cart.png")
