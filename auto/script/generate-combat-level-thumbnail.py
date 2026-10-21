#!/usr/bin/env python3
"""760x430 thumbnail for the combat level system guide."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = ROOT / "assets" / "images" / "posts" / "combat-level-system-guide.webp"
WIDTH, HEIGHT, PADDING = 760, 430, 72
TITLE = "전투 레벨"
SUB = "75레벨 · 경험치 · 비급서"


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

    img = Image.new("RGB", (WIDTH, HEIGHT), (12, 14, 24))
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        draw.line(
            [(0, y), (WIDTH, y)],
            fill=(int(12 + 10 * ratio), int(16 + 22 * ratio), int(28 + 36 * ratio)),
        )

    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse((WIDTH - 360, -120, WIDTH + 40, 280), fill=(48, 92, 140, 70))
    od.ellipse((-160, HEIGHT - 260, 260, HEIGHT + 60), fill=(180, 140, 60, 36))
    canvas = Image.alpha_composite(img.convert("RGBA"), overlay)

    badge = Image.new("RGBA", (220, 220), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge)
    bd.ellipse((8, 8, 212, 212), fill=(18, 28, 48, 230), outline=(220, 185, 110, 255), width=6)
    badge_font = load_font(92, bold=True)
    label = "75"
    box = bd.textbbox((0, 0), label, font=badge_font)
    tw, th = box[2] - box[0], box[3] - box[1]
    bd.text(((220 - tw) / 2 - box[0], (220 - th) / 2 - box[1] - 6), label, font=badge_font, fill=(248, 246, 240, 255))
    badge_x = WIDTH - PADDING - 220
    badge_y = (HEIGHT - 220) // 2
    canvas.alpha_composite(badge, (badge_x, badge_y))

    text_right = badge_x - 36
    d = ImageDraw.Draw(canvas)
    title_size = 64
    while title_size > 28:
        title_font = load_font(title_size, bold=True)
        box = d.textbbox((0, 0), TITLE, font=title_font)
        if box[2] - box[0] <= text_right - PADDING:
            break
        title_size -= 2
    title_font = load_font(title_size, bold=True)
    sub_font = load_font(26)
    title_box = d.textbbox((PADDING, 0), TITLE, font=title_font)
    sub_box = d.textbbox((PADDING, 0), SUB, font=sub_font)
    block_h = (title_box[3] - title_box[1]) + 18 + (sub_box[3] - sub_box[1])
    top = (HEIGHT - block_h) // 2
    d.text((PADDING, top), TITLE, font=title_font, fill=(248, 246, 240, 255))
    d.text((PADDING, top + (title_box[3] - title_box[1]) + 18), SUB, font=sub_font, fill=(220, 185, 110, 255))

    canvas.convert("RGB").save(OUT_PATH, format="WEBP", quality=92, method=6)
    print(OUT_PATH)


if __name__ == "__main__":
    main()
