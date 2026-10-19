#!/usr/bin/env python3
"""760x430 thumbnail for the Donghae solo Black Shrine guide."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = ROOT / "assets" / "images" / "posts" / "donghae-solo-shrine-guide.webp"
ICON_PATH = Path(__file__).resolve().parent / "sources" / "black-shrine-icon.png"
WIDTH, HEIGHT, PADDING = 760, 430, 72
TITLE = "동해도(개인)"
SUB = "입장 · 횟수 · 보상"


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
            fill=(int(12 + 16 * ratio), int(14 + 18 * ratio), int(24 + 42 * ratio)),
        )

    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse((WIDTH - 380, -140, WIDTH + 80, 300), fill=(150, 110, 40, 48))
    od.ellipse((-180, HEIGHT - 280, 240, HEIGHT + 80), fill=(24, 36, 78, 50))
    canvas = Image.alpha_composite(img.convert("RGBA"), overlay)

    icon = Image.open(ICON_PATH).convert("RGBA")
    icon_w = 248
    icon_h = round(icon_w * icon.height / icon.width)
    icon = icon.resize((icon_w, icon_h), Image.Resampling.LANCZOS)
    icon_x = WIDTH - PADDING - icon_w
    icon_y = (HEIGHT - icon_h) // 2
    glow = Image.new("RGBA", (icon_w + 56, icon_h + 56), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((0, 0, icon_w + 56, icon_h + 56), fill=(210, 160, 60, 55))
    canvas.alpha_composite(glow, (icon_x - 28, icon_y - 28))
    canvas.alpha_composite(icon, (icon_x, icon_y))

    text_right = icon_x - 36
    d = ImageDraw.Draw(canvas)
    title_size = 64
    while title_size > 28:
        title_font = load_font(title_size, bold=True)
        box = d.textbbox((0, 0), TITLE, font=title_font)
        if box[2] - box[0] <= text_right - PADDING:
            break
        title_size -= 2
    title_font = load_font(title_size, bold=True)
    sub_font = load_font(28)
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
