#!/usr/bin/env python3
"""760x430 thumbnail for the Magaia Temple prep guide."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = ROOT / "assets" / "images" / "posts" / "magaia-temple-prep-guide.webp"
WIDTH, HEIGHT = 760, 430
# Title grows until its ink sits this far from both edges.
SIDE = 64
TITLE = "마가이아 신전"
SUB = "공방 410 / 490 · 준비"
SUB_RATIO = 26 / 48


def load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = ["malgunbd.ttf", "malgun.ttf"] if bold else ["malgun.ttf"]
    for name in names:
        path = Path("C:/Windows/Fonts") / name
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def ink(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int, int, int]:
    box = draw.textbbox((0, 0), text, font=font)
    return box[0], box[1], box[2] - box[0], box[3] - box[1]


def fit_title(draw: ImageDraw.ImageDraw) -> tuple[ImageFont.ImageFont, ImageFont.ImageFont, int]:
    max_w = WIDTH - 2 * SIDE
    chosen = 28
    for size in range(28, 160):
        title_font = load_font(size, bold=True)
        sub_font = load_font(max(18, round(size * SUB_RATIO)))
        _, _, tw, th = ink(draw, TITLE, title_font)
        _, _, sw, sh = ink(draw, SUB, sub_font)
        gap = round(18 * size / 48)
        if max(tw, sw) <= max_w and th + gap + sh <= HEIGHT - 96:
            chosen = size
        else:
            break
    return load_font(chosen, bold=True), load_font(max(18, round(chosen * SUB_RATIO))), chosen


def draw_line(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, top: int, fill: tuple[int, int, int, int]) -> int:
    ox, oy, tw, th = ink(draw, text, font)
    x = (WIDTH - tw) // 2 - ox
    draw.text((x, top - oy), text, font=font, fill=fill)
    return th


def draw_pair(canvas: Image.Image) -> None:
    draw = ImageDraw.Draw(canvas)
    title_font, sub_font, size = fit_title(draw)
    gap = round(18 * size / 48)
    _, _, _, th = ink(draw, TITLE, title_font)
    _, _, _, sh = ink(draw, SUB, sub_font)
    top = (HEIGHT - (th + gap + sh)) // 2
    draw_line(draw, TITLE, title_font, top, (248, 246, 240, 255))
    draw_line(draw, SUB, sub_font, top + th + gap, (220, 196, 120, 255))
    print("title", size, "sub", max(18, round(size * SUB_RATIO)))


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
    draw_pair(canvas)
    canvas.convert("RGB").save(OUT_PATH, format="WEBP", quality=92, method=6)
    print("Wrote", OUT_PATH)


if __name__ == "__main__":
    main()
