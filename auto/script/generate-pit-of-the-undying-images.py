#!/usr/bin/env python3
"""Thumbnail and emblem strip for the Pit of the Undying guide."""

from __future__ import annotations

import io
import re
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "assets" / "images" / "posts"
CODEX_BASE = "https://bdocodex.com"
WIDTH, HEIGHT, PADDING = 760, 430, 72

EMBLEMS = (
    (12813, "장", "+5%"),
    (12814, "광", "+10%"),
    (12815, "고", "+15%"),
    (12816, "유", "+20%"),
    (12817, "동", "+30%"),
)


def fetch_icon(item_id: int) -> Image.Image:
    html = urllib.request.urlopen(
        urllib.request.Request(
            f"{CODEX_BASE}/kr/item/{item_id}/",
            headers={"User-Agent": "Mozilla/5.0"},
        ),
        timeout=30,
    ).read().decode("utf-8", "ignore")
    match = re.search(r"(?:https://bdocodex\.com/)?(items/new_icon/[^\"']+\.(?:webp|png))", html)
    if not match:
        raise RuntimeError(f"Icon not found for {item_id}")
    path = match.group(1)
    url = path if path.startswith("http") else f"{CODEX_BASE}/{path}"
    data = urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}),
        timeout=30,
    ).read()
    return Image.open(io.BytesIO(data)).convert("RGBA")


def load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = (
        ["C:/Windows/Fonts/malgunbd.ttf", "C:/Windows/Fonts/malgun.ttf"]
        if bold
        else ["C:/Windows/Fonts/malgun.ttf"]
    )
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def vertical_bg(size: tuple[int, int]) -> Image.Image:
    width, height = size
    img = Image.new("RGB", size, (14, 16, 22))
    draw = ImageDraw.Draw(img)
    for y in range(height):
        ratio = y / height
        draw.line(
            [(0, y), (width, y)],
            fill=(int(14 + 18 * ratio), int(16 + 14 * ratio), int(22 + 36 * ratio)),
        )
    return img


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    icons = [(name, bonus, fetch_icon(item_id)) for item_id, name, bonus in EMBLEMS]

    thumb = vertical_bg((WIDTH, HEIGHT)).convert("RGBA")
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse((WIDTH - 380, -140, WIDTH + 80, 300), fill=(90, 70, 40, 50))
    od.ellipse((-180, HEIGHT - 280, 240, HEIGHT + 80), fill=(28, 42, 78, 46))
    canvas = Image.alpha_composite(thumb, overlay)

    icon_size = 188
    icon = icons[-1][2].resize((icon_size, icon_size), Image.Resampling.LANCZOS)
    icon_x = WIDTH - PADDING - icon_size
    icon_y = (HEIGHT - icon_size) // 2
    glow = Image.new("RGBA", (icon_size + 48, icon_size + 48), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((0, 0, icon_size + 48, icon_size + 48), fill=(200, 160, 70, 55))
    canvas.alpha_composite(glow, (icon_x - 24, icon_y - 24))
    canvas.alpha_composite(icon, (icon_x, icon_y))

    draw = ImageDraw.Draw(canvas)
    title_font = load_font(54, bold=True)
    sub_font = load_font(28)
    draw.text((PADDING, PADDING + 36), "불멸의 나락", font=title_font, fill=(248, 246, 240, 255))
    bbox = draw.textbbox((PADDING, PADDING + 36), "불멸의 나락", font=title_font)
    draw.text((PADDING, bbox[3] + 16), "승급 · 휘장 · 주간 수익", font=sub_font, fill=(220, 185, 110, 255))

    thumb_path = OUT_DIR / "pit-of-the-undying-guide.webp"
    canvas.convert("RGB").save(thumb_path, format="WEBP", quality=92, method=6)

    strip_w, strip_h = 760, 220
    strip = vertical_bg((strip_w, strip_h)).convert("RGBA")
    sd = ImageDraw.Draw(strip)
    name_font = load_font(22, bold=True)
    bonus_font = load_font(18)
    slot = strip_w // len(icons)
    glyph = 96
    for index, (name, bonus, source) in enumerate(icons):
        resized = source.resize((glyph, glyph), Image.Resampling.LANCZOS)
        x = index * slot + (slot - glyph) // 2
        strip.alpha_composite(resized, (x, 28))
        name_bbox = sd.textbbox((0, 0), name, font=name_font)
        bonus_bbox = sd.textbbox((0, 0), bonus, font=bonus_font)
        name_x = index * slot + (slot - (name_bbox[2] - name_bbox[0])) // 2
        bonus_x = index * slot + (slot - (bonus_bbox[2] - bonus_bbox[0])) // 2
        sd.text((name_x, 132), name, font=name_font, fill=(248, 246, 240, 255))
        sd.text((bonus_x, 164), bonus, font=bonus_font, fill=(220, 185, 110, 255))

    strip_path = OUT_DIR / "pit-of-the-undying-emblems.webp"
    strip.convert("RGB").save(strip_path, format="WEBP", quality=92, method=6)
    print(f"Wrote {thumb_path}")
    print(f"Wrote {strip_path}")


if __name__ == "__main__":
    main()
