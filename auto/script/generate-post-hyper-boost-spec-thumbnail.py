#!/usr/bin/env python3
"""760x430 thumbnail for the post-hyper-boost spec guide."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets" / "images" / "posts" / "post-hyper-boost-spec-guide.webp"
W, H = 760, 430
SIDE = 64
TITLE = "하이퍼 부스트 이후"
SUB = "강화비 · 거래소 비교"
SUB_RATIO = 26 / 46


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = ["malgunbd.ttf", "malgun.ttf"] if bold else ["malgun.ttf"]
    for name in names:
        path = Path("C:/Windows/Fonts") / name
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def ink(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.ImageFont) -> tuple[int, int, int, int]:
    box = draw.textbbox((0, 0), text, font=face)
    return box[0], box[1], box[2] - box[0], box[3] - box[1]


def fit_title(draw: ImageDraw.ImageDraw) -> tuple[ImageFont.ImageFont, ImageFont.ImageFont, int]:
    max_w = W - 2 * SIDE
    chosen = 28
    for size in range(28, 160):
        title_font = font(size, bold=True)
        sub_font = font(max(18, round(size * SUB_RATIO)))
        _, _, tw, th = ink(draw, TITLE, title_font)
        _, _, sw, sh = ink(draw, SUB, sub_font)
        gap = round(16 * size / 46)
        if max(tw, sw) <= max_w and th + gap + sh <= H - 96:
            chosen = size
        else:
            break
    return font(chosen, bold=True), font(max(18, round(chosen * SUB_RATIO))), chosen


def draw_line(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.ImageFont, top: int, fill: tuple[int, int, int, int]) -> int:
    ox, oy, tw, th = ink(draw, text, face)
    x = (W - tw) // 2 - ox
    draw.text((x, top - oy), text, font=face, fill=fill)
    return th


def draw_pair(canvas: Image.Image) -> None:
    draw = ImageDraw.Draw(canvas)
    title_font, sub_font, size = fit_title(draw)
    gap = round(16 * size / 46)
    _, _, _, th = ink(draw, TITLE, title_font)
    _, _, _, sh = ink(draw, SUB, sub_font)
    top = (H - (th + gap + sh)) // 2
    draw_line(draw, TITLE, title_font, top, (248, 246, 240, 255))
    draw_line(draw, SUB, sub_font, top + th + gap, (196, 214, 196, 255))
    print("title", size, "sub", max(18, round(size * SUB_RATIO)))


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (W, H), (16, 18, 28))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        draw.line([(0, y), (W, y)], fill=(int(16 + 18 * t), int(20 + 14 * t), int(32 + 22 * t)))
    canvas = img.convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse((W - 380, -80, W + 40, 300), fill=(90, 140, 170, 42))
    od.ellipse((-140, H - 220, 280, H + 60), fill=(160, 120, 60, 36))
    canvas = Image.alpha_composite(canvas, overlay)
    draw_pair(canvas)
    canvas.convert("RGB").save(OUT, format="WEBP", quality=92, method=6)
    print(OUT)


if __name__ == "__main__":
    main()
