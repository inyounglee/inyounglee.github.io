#!/usr/bin/env python3
"""760x430 thumbnail for the Magaia Temple prep guide."""

from __future__ import annotations

import io
import re
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = ROOT / "assets" / "images" / "posts" / "magaia-temple-prep-guide.webp"
CODEX = "https://bdocodex.com"
WIDTH, HEIGHT, PADDING = 760, 430, 72


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read()


def find_icon() -> Image.Image | None:
    html = fetch(f"{CODEX}/kr/search/?q=%EC%97%98%EB%A6%AC%EC%96%B8+%EC%B6%94%EC%A2%85%EC%9E%90%EC%9D%98+%ED%88%AC%EA%B5%AC").decode(
        "utf-8", "ignore"
    )
    item = re.search(r"/kr/item/(\d+)/", html)
    if not item:
        return None
    page = fetch(f"{CODEX}/kr/item/{item.group(1)}/").decode("utf-8", "ignore")
    match = re.search(r"(?:https://bdocodex\.com/)?(items/new_icon/[^\"']+\.(?:webp|png))", page)
    if not match:
        return None
    path = match.group(1)
    url = path if path.startswith("http") else f"{CODEX}/{path}"
    return Image.open(io.BytesIO(fetch(url))).convert("RGBA")


def load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = ["malgunbd.ttf", "malgun.ttf"] if bold else ["malgun.ttf"]
    for name in names:
        path = Path("C:/Windows/Fonts") / name
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (WIDTH, HEIGHT), (12, 16, 28))
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        draw.line(
            [(0, y), (WIDTH, y)],
            fill=(int(12 + 20 * ratio), int(18 + 16 * ratio), int(32 + 28 * ratio)),
        )
    canvas = img.convert("RGBA")
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse((WIDTH - 400, -120, WIDTH + 60, 320), fill=(180, 150, 70, 40))
    od.ellipse((-160, HEIGHT - 240, 260, HEIGHT + 80), fill=(40, 70, 120, 46))
    canvas = Image.alpha_composite(canvas, overlay)

    try:
        icon = find_icon()
    except Exception as exc:
        print("icon skipped", exc)
        icon = None
    if icon is not None:
        size = 188
        icon = icon.resize((size, size), Image.Resampling.LANCZOS)
        x = WIDTH - PADDING - size
        y = (HEIGHT - size) // 2
        glow = Image.new("RGBA", (size + 48, size + 48), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse((0, 0, size + 48, size + 48), fill=(220, 190, 90, 50))
        canvas.alpha_composite(glow, (x - 24, y - 24))
        canvas.alpha_composite(icon, (x, y))

    d = ImageDraw.Draw(canvas)
    title = load_font(48, bold=True)
    sub = load_font(26)
    d.text((PADDING, PADDING + 48), "마가이아 신전", font=title, fill=(248, 246, 240, 255))
    bbox = d.textbbox((PADDING, PADDING + 48), "마가이아 신전", font=title)
    d.text((PADDING, bbox[3] + 18), "공방 410 / 490 · 준비", font=sub, fill=(220, 196, 120, 255))
    canvas.convert("RGB").save(OUT_PATH, format="WEBP", quality=92, method=6)
    print("Wrote", OUT_PATH, "icon", icon is not None)


if __name__ == "__main__":
    main()
