#!/usr/bin/env python3
"""Generate 760x430 webp thumbnail for accessory upgrade guide."""

from __future__ import annotations

import io
import re
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "assets" / "images" / "posts"
OUT_PATH = OUT_DIR / "accessory-upgrade-guide.webp"
CODEX_BASE = "https://bdocodex.com"

WIDTH, HEIGHT = 760, 430
PADDING = 80
ITEM_ID = 11697  # 카라자드 목걸이


def fetch_icon(item_id: int) -> Image.Image:
    html = urllib.request.urlopen(f"{CODEX_BASE}/kr/item/{item_id}/", timeout=30).read().decode(
        "utf-8", "ignore"
    )
    match = re.search(r"(?:https://bdocodex\.com/)?(items/new_icon/[^\"']+\.(?:webp|png))", html)
    if not match:
        raise RuntimeError(f"Icon not found for {item_id}")
    path = match.group(1)
    url = path if path.startswith("http") else f"{CODEX_BASE}/{path}"
    data = urllib.request.urlopen(url, timeout=30).read()
    return Image.open(io.BytesIO(data)).convert("RGBA")


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        ["C:/Windows/Fonts/malgunbd.ttf", "C:/Windows/Fonts/NotoSansKR-Bold.otf"]
        if bold
        else ["C:/Windows/Fonts/malgun.ttf", "C:/Windows/Fonts/NotoSansKR-Regular.otf"]
    )
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def fit_font(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    max_width: int,
    max_height: int,
    bold: bool,
    start: int,
    min_size: int = 28,
) -> ImageFont.ImageFont:
    size = start
    while size >= min_size:
        font = load_font(size, bold=bold)
        heights = []
        widths = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            widths.append(bbox[2] - bbox[0])
            heights.append(bbox[3] - bbox[1])
        total_h = sum(heights) + 8 * (len(lines) - 1)
        if max(widths) <= max_width and total_h <= max_height:
            return font
        size -= 2
    return load_font(min_size, bold=bold)


def make_background() -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), (16, 18, 26))
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        color = (
            int(16 + 28 * ratio),
            int(18 + 20 * ratio),
            int(26 + 36 * ratio),
        )
        draw.line([(0, y), (WIDTH, y)], fill=color)

    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse((WIDTH - 340, -100, WIDTH + 100, 260), fill=(150, 100, 40, 40))
    od.ellipse((-140, HEIGHT - 240, 240, HEIGHT + 100), fill=(40, 70, 120, 35))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    canvas = make_background()
    draw = ImageDraw.Draw(canvas)

    icon_size = 200
    icon = fetch_icon(ITEM_ID).resize((icon_size, icon_size), Image.Resampling.LANCZOS)
    icon_x = WIDTH - PADDING - icon_size
    icon_y = (HEIGHT - icon_size) // 2

    glow = Image.new("RGBA", (icon_size + 48, icon_size + 48), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((0, 0, icon_size + 48, icon_size + 48), fill=(255, 200, 100, 55))
    canvas.alpha_composite(glow, (icon_x - 24, icon_y - 24))
    canvas.alpha_composite(icon, (icon_x, icon_y))

    text_right = icon_x - 36
    text_box_w = text_right - PADDING
    text_box_h = HEIGHT - PADDING * 2

    title_lines = ["액세서리", "업그레이드"]
    subtitle = "초보 → 환(X) 카라자드"

    # Title fills most of the padded left area
    title_font = fit_font(draw, title_lines, text_box_w, int(text_box_h * 0.72), True, 78, 40)
    subtitle_font = fit_font(draw, [subtitle], text_box_w, int(text_box_h * 0.22), False, 42, 28)

    y = PADDING
    for i, line in enumerate(title_lines):
        draw.text((PADDING, y), line, font=title_font, fill=(248, 246, 240, 255))
        bbox = draw.textbbox((PADDING, y), line, font=title_font)
        y = bbox[3] + (6 if i == 0 else 14)

    draw.text((PADDING, y), subtitle, font=subtitle_font, fill=(220, 185, 110, 255))

    out = canvas.convert("RGB")
    out.save(OUT_PATH, format="WEBP", quality=92, method=6)
    assert out.size == (WIDTH, HEIGHT)
    print(f"Wrote {OUT_PATH} {out.size}")


if __name__ == "__main__":
    main()
