#!/usr/bin/env python3
"""Redraw the Kharazad reform guide title so the line fills the card evenly."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
SRC = Path(__file__).resolve().parent / "sources" / "kharazad-reform-guide-src.webp"
OUT = ROOT / "assets" / "images" / "posts" / "kharazad-reform-guide.webp"
SIDE = 64
TITLE = "카라자드 개량"
SUB = "가이드"
# Previous overlay was about 51px title / 34px subtitle.
SUB_RATIO = 34 / 51


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    name = "malgunbd.ttf" if bold else "malgun.ttf"
    path = Path("C:/Windows/Fonts") / name
    if path.exists():
        return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def text_mask(src: Image.Image) -> Image.Image:
    px = src.load()
    w, h = src.size
    mask = Image.new("L", src.size, 0)
    mp = mask.load()
    for y in range(155, 230):
        for x in range(180, 640):
            r, g, b = px[x, y]
            if r > 200 and g > 185 and b > 165:
                mp[x, y] = 255
    for y in range(228, 280):
        for x in range(330, 470):
            r, g, b = px[x, y]
            if r > 165 and g > 115 and b < 150 and r > b + 35:
                mp[x, y] = 255
    grown = Image.new("L", src.size, 0)
    gp = grown.load()
    for y in range(150, 290):
        for x in range(170, 650):
            if mp[x, y] == 0:
                continue
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < w and 0 <= yy < h:
                        gp[xx, yy] = 255
    return grown


def inpaint(src: Image.Image, mask: Image.Image) -> Image.Image:
    im = src.copy()
    px = im.load()
    mp = mask.load()
    w, h = im.size
    neighbors = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1))
    for _ in range(64):
        border: list[tuple[int, int, list[tuple[int, int, int]]]] = []
        for y in range(145, 295):
            for x in range(165, 655):
                if mp[x, y] == 0:
                    continue
                found = []
                for dx, dy in neighbors:
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < w and 0 <= yy < h and mp[xx, yy] == 0:
                        found.append(px[xx, yy])
                if found:
                    border.append((x, y, found))
        if not border:
            break
        for x, y, found in border:
            n = len(found)
            px[x, y] = (
                sum(c[0] for c in found) // n,
                sum(c[1] for c in found) // n,
                sum(c[2] for c in found) // n,
            )
            mp[x, y] = 0
    return im


def ink(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.ImageFont) -> tuple[int, int, int, int]:
    box = draw.textbbox((0, 0), text, font=face)
    return box[0], box[1], box[2] - box[0], box[3] - box[1]


def fit(draw: ImageDraw.ImageDraw, width: int) -> tuple[ImageFont.ImageFont, ImageFont.ImageFont, int]:
    max_w = width - 2 * SIDE
    chosen = 36
    for size in range(36, 160):
        title_font = font(size, bold=True)
        sub_font = font(max(18, round(size * SUB_RATIO)))
        _, _, tw, th = ink(draw, TITLE, title_font)
        _, _, sw, sh = ink(draw, SUB, sub_font)
        gap = round(14 * size / 51)
        if max(tw, sw) <= max_w and th + gap + sh <= 280:
            chosen = size
        else:
            break
    sub_size = max(18, round(chosen * SUB_RATIO))
    return font(chosen, bold=True), font(sub_size), chosen


def draw_line(
    draw: ImageDraw.ImageDraw,
    text: str,
    face: ImageFont.ImageFont,
    top: int,
    fill: tuple[int, int, int, int],
    width: int,
) -> int:
    ox, oy, tw, th = ink(draw, text, face)
    x = (width - tw) // 2 - ox
    y = top - oy
    draw.text((x + 2, y + 3), text, font=face, fill=(0, 0, 0, 150))
    draw.text((x, y), text, font=face, fill=fill)
    return th


def main() -> None:
    src = Image.open(SRC).convert("RGB")
    clean = inpaint(src, text_mask(src)).convert("RGBA")
    draw = ImageDraw.Draw(clean)
    width, height = clean.size
    title_font, sub_font, size = fit(draw, width)
    gap = round(14 * size / 51)
    _, _, _, th = ink(draw, TITLE, title_font)
    _, _, _, sh = ink(draw, SUB, sub_font)
    # Keep the pair over the altar, where the old title sat.
    top = 168
    if top + th + gap + sh > height - 40:
        top = height - 40 - (th + gap + sh)
    draw_line(draw, TITLE, title_font, top, (248, 246, 240, 255), width)
    draw_line(draw, SUB, sub_font, top + th + gap, (212, 176, 96, 255), width)
    clean.convert("RGB").save(OUT, format="WEBP", quality=92, method=6)
    print("Wrote", OUT, "title", size, "sub", max(18, round(size * SUB_RATIO)))


if __name__ == "__main__":
    main()
