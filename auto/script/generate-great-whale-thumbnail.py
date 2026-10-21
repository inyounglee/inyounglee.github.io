#!/usr/bin/env python3
"""1280x720 thumbnail for the great whale content guide."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = Path(__file__).resolve().parent / "sources" / "great-whale.png"
OUT_PATH = ROOT / "assets" / "images" / "posts" / "great-whale-loot-guide.webp"
WIDTH, HEIGHT = 1280, 720
TITLE = "대왕 고래"
SUB = "콘텐츠 가이드"
WHITE = (248, 246, 242)
GOLD = (214, 188, 118)


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


def knockout(src: Image.Image) -> Image.Image:
    image = src.convert("RGBA")
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, _ = pixels[x, y]
            peak = max(r, g, b)
            if peak < 18:
                pixels[x, y] = (0, 0, 0, 0)
            elif peak < 48 and g < 40 and b < 40:
                pixels[x, y] = (r, g, b, int(255 * (peak - 18) / 30))
    bbox = image.getbbox()
    if bbox is None:
        return image
    return image.crop(bbox)


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_width: int, start: int, bold: bool) -> ImageFont.ImageFont:
    size = start
    while size > 28:
        font = load_font(size, bold=bold)
        box = draw.textbbox((0, 0), text, font=font)
        if box[2] - box[0] <= max_width:
            return font
        size -= 2
    return load_font(size, bold=bold)


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (WIDTH, HEIGHT), (16, 22, 40))
    sky = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        sky.line(
            [(0, y), (WIDTH, y)],
            fill=(
                int(16 + 10 * ratio),
                int(22 + 14 * ratio),
                int(40 + 18 * ratio),
            ),
        )

    canvas = img.convert("RGBA")
    whale = knockout(Image.open(SRC_PATH))
    whale_w = 760
    whale_h = round(whale_w * whale.height / whale.width)
    whale = whale.resize((whale_w, whale_h), Image.Resampling.LANCZOS)
    whale_x = WIDTH - 36 - whale_w
    whale_y = (HEIGHT - whale_h) // 2
    canvas.alpha_composite(whale, (whale_x, whale_y))

    text_left = 72
    max_width = whale_x - text_left - 28
    measure = ImageDraw.Draw(canvas)
    title_font = fit_font(measure, TITLE, max_width, 104, bold=True)
    sub_font = fit_font(measure, SUB, max_width, 58, bold=True)
    title_box = measure.textbbox((0, 0), TITLE, font=title_font)
    sub_box = measure.textbbox((0, 0), SUB, font=sub_font)
    gap = 22
    block_h = (title_box[3] - title_box[1]) + gap + (sub_box[3] - sub_box[1])
    top = (HEIGHT - block_h) // 2 - 6
    measure.text((text_left, top), TITLE, font=title_font, fill=WHITE)
    measure.text(
        (text_left, top + (title_box[3] - title_box[1]) + gap),
        SUB,
        font=sub_font,
        fill=GOLD,
    )

    canvas.convert("RGB").save(OUT_PATH, format="WEBP", quality=92, method=6)
    print(OUT_PATH, title_font.size, sub_font.size, whale.size)


if __name__ == "__main__":
    main()
