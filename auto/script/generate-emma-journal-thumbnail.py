#!/usr/bin/env python3
"""Generate 760x430 webp thumbnail for Emma Bartali journal guide."""

from __future__ import annotations

import io
import re
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = ROOT / "assets" / "images" / "posts" / "emma-bartali-journal-guide.webp"
CODEX_BASE = "https://bdocodex.com"
WIDTH, HEIGHT, PADDING = 760, 430, 80
ITEM_ID = 12814  # 광 : 불멸의 까마귀 휘장


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


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (WIDTH, HEIGHT), (14, 16, 22))
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        draw.line(
            [(0, y), (WIDTH, y)],
            fill=(int(14 + 22 * ratio), int(16 + 18 * ratio), int(22 + 40 * ratio)),
        )

    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse((WIDTH - 360, -120, WIDTH + 120, 280), fill=(120, 70, 40, 45))
    od.ellipse((-160, HEIGHT - 260, 220, HEIGHT + 120), fill=(30, 50, 90, 40))
    canvas = Image.alpha_composite(img.convert("RGBA"), overlay)

    icon_size = 200
    icon = fetch_icon(ITEM_ID).resize((icon_size, icon_size), Image.Resampling.LANCZOS)
    icon_x = WIDTH - PADDING - icon_size
    icon_y = (HEIGHT - icon_size) // 2

    glow = Image.new("RGBA", (icon_size + 48, icon_size + 48), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((0, 0, icon_size + 48, icon_size + 48), fill=(200, 150, 70, 50))
    canvas.alpha_composite(glow, (icon_x - 24, icon_y - 24))
    canvas.alpha_composite(icon, (icon_x, icon_y))

    d = ImageDraw.Draw(canvas)
    title_font = load_font(56, bold=True)
    sub_font = load_font(30, bold=False)
    d.text((PADDING, PADDING + 20), "엠마 바탈리", font=title_font, fill=(248, 246, 240, 255))
    bbox = d.textbbox((PADDING, PADDING + 20), "엠마 바탈리", font=title_font)
    d.text((PADDING, bbox[3] + 8), "기록일지", font=title_font, fill=(248, 246, 240, 255))
    bbox2 = d.textbbox((PADDING, bbox[3] + 8), "기록일지", font=title_font)
    d.text((PADDING, bbox2[3] + 18), "1~13장 보상 · 진행 순서", font=sub_font, fill=(220, 185, 110, 255))

    out = canvas.convert("RGB")
    out.save(OUT_PATH, format="WEBP", quality=92, method=6)
    assert out.size == (WIDTH, HEIGHT)
    print(f"Wrote {OUT_PATH} {out.size}")


if __name__ == "__main__":
    main()
