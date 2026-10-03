#!/usr/bin/env python3
"""760x430 thumbnail for the post-hyper-boost spec guide."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets" / "images" / "posts" / "post-hyper-boost-spec-guide.webp"
W, H, PAD = 760, 430, 72


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = ["malgunbd.ttf", "malgun.ttf"] if bold else ["malgun.ttf"]
    for name in names:
        path = Path("C:/Windows/Fonts") / name
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


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
    d = ImageDraw.Draw(canvas)
    title = font(46, bold=True)
    sub = font(26)
    d.text((PAD, PAD + 56), "하이퍼 부스트 이후", font=title, fill=(248, 246, 240, 255))
    bbox = d.textbbox((PAD, PAD + 56), "하이퍼 부스트 이후", font=title)
    d.text((PAD, bbox[3] + 16), "강화비 · 거래소 비교", font=sub, fill=(196, 214, 196, 255))
    canvas.convert("RGB").save(OUT, format="WEBP", quality=92, method=6)
    print(OUT)


if __name__ == "__main__":
    main()
