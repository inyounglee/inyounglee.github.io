#!/usr/bin/env python3
"""Generate 760x430 webp post thumbnails for BDO treasure guides."""

from __future__ import annotations

import io
import re
import textwrap
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "assets" / "images" / "posts"
CODEX_BASE = "https://bdocodex.com"
CDN_BASE = "https://cdn.questlog.gg/black-desert/assets/ui_texture/icon/new_icon"

WIDTH, HEIGHT = 760, 430
PADDING = 80
ICON_SIZE = 210
TEXT_MAX_WIDTH = WIDTH - (PADDING * 2) - ICON_SIZE - 48

POSTS = [
    {
        "slug": "black-desert-treasure-list",
        "item_id": 12034,
        "title_lines": ["보물 아이템", "목록"],
        "subtitle": "특징 · 난이도 · 제작 가이드",
    },
    {
        "slug": "treasure-onet-elixir-guide",
        "item_id": 40712,
        "title_lines": ["오네트의", "정령수"],
        "subtitle": "제작 가이드",
    },
    {
        "slug": "treasure-odore-elixir-guide",
        "item_id": 40713,
        "title_lines": ["오도어의", "정령수"],
        "subtitle": "제작 가이드",
    },
    {
        "slug": "treasure-lafi-compass-guide",
        "item_id": 16016,
        "title_lines": ["개량형", "나침반"],
        "subtitle": "라피 베드마운틴 · 제작 가이드",
    },
    {
        "slug": "treasure-archaeologist-map-guide",
        "item_id": 16019,
        "title_lines": ["고고학자의", "지도"],
        "subtitle": "제작 가이드",
    },
    {
        "slug": "treasure-ebenus-wheel-guide",
        "item_id": 59321,
        "title_lines": ["에벤루스의", "놀"],
        "subtitle": "제작 가이드",
    },
    {
        "slug": "treasure-merchant-ring-guide",
        "item_id": 12034,
        "title_lines": ["거상의", "반지"],
        "subtitle": "제작 가이드",
    },
    {
        "slug": "treasure-krogdalo-nest-guide",
        "item_id": 59418,
        "title_lines": ["크로그달로의", "둥지"],
        "subtitle": "제작 가이드",
    },
    {
        "slug": "treasure-lafi-telescope-guide",
        "item_id": 65299,
        "title_lines": ["개량형", "망원경"],
        "subtitle": "라피 베드마운틴 · 제작 가이드",
    },
    {
        "slug": "treasure-remitarong-lamp-guide",
        "item_id": 53803,
        "title_lines": ["동동 램프"],
        "subtitle": "레미타롱솜 · 제작 가이드",
    },
    {
        "slug": "treasure-nostos-star-guide",
        "item_id": 767290,
        "title_lines": ["노스토스의", "별"],
        "subtitle": "제작 가이드",
    },
]

ICON_CACHE: dict[int, Image.Image] = {}


def fetch_icon_url(item_id: int) -> str:
    url = f"{CODEX_BASE}/kr/item/{item_id}/"
    html = urllib.request.urlopen(url, timeout=30).read().decode("utf-8", "ignore")
    match = re.search(
        r"(?:https://bdocodex\.com/)?(items/new_icon/[^\"']+\.(?:webp|png))",
        html,
    )
    if match:
        path = match.group(1)
        return path if path.startswith("http") else f"{CODEX_BASE}/{path}"

    padded = f"{item_id:08d}"
    short = f"{item_id:05d}" if item_id < 100000 else str(item_id)
    candidates = [
        f"{CDN_BASE}/03_etc/{short}.webp",
        f"{CDN_BASE}/03_etc/{padded}.webp",
        f"{CDN_BASE}/03_etc/000{short}.webp",
    ]
    for candidate in candidates:
        request = urllib.request.Request(candidate, method="HEAD")
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                if response.status == 200:
                    return candidate
        except Exception:
            continue

    raise RuntimeError(f"Icon not found for item {item_id}")


def load_icon(item_id: int) -> Image.Image:
    if item_id in ICON_CACHE:
        return ICON_CACHE[item_id].copy()

    icon_url = fetch_icon_url(item_id)
    data = urllib.request.urlopen(icon_url, timeout=30).read()
    icon = Image.open(io.BytesIO(data)).convert("RGBA")
    ICON_CACHE[item_id] = icon
    return icon.copy()


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


def make_background() -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), (18, 20, 28))
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        color = (
            int(18 + 24 * ratio),
            int(20 + 18 * ratio),
            int(28 + 32 * ratio),
        )
        draw.line([(0, y), (WIDTH, y)], fill=color)

    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.ellipse((WIDTH - 320, -80, WIDTH + 80, 240), fill=(120, 90, 40, 35))
    overlay_draw.ellipse((-120, HEIGHT - 220, 220, HEIGHT + 80), fill=(50, 80, 130, 30))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def wrap_lines(text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    words = text.split()
    if not words:
        return [text]

    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def draw_text_block(
    canvas: Image.Image,
    title_lines: list[str],
    subtitle: str,
) -> None:
    draw = ImageDraw.Draw(canvas)
    title_font = load_font(58, bold=True)
    subtitle_font = load_font(36, bold=False)

    x = PADDING
    y = PADDING
    line_gap = 10

    for line in title_lines:
        wrapped = wrap_lines(line, title_font, TEXT_MAX_WIDTH)
        if len(wrapped) > 1:
            wrapped = textwrap.wrap(line, width=7)
        for part in wrapped:
            draw.text((x, y), part, font=title_font, fill=(245, 245, 245, 255))
            bbox = draw.textbbox((x, y), part, font=title_font)
            y = bbox[3] + line_gap

    y += 8
    subtitle_lines = wrap_lines(subtitle, subtitle_font, TEXT_MAX_WIDTH)
    for part in subtitle_lines:
        draw.text((x, y), part, font=subtitle_font, fill=(210, 188, 120, 255))
        bbox = draw.textbbox((x, y), part, font=subtitle_font)
        y = bbox[3] + 6


def compose_thumbnail(title_lines: list[str], subtitle: str, item_id: int) -> Image.Image:
    canvas = make_background()
    icon = load_icon(item_id)
    icon = icon.resize((ICON_SIZE, ICON_SIZE), Image.Resampling.LANCZOS)

    icon_x = WIDTH - PADDING - ICON_SIZE
    icon_y = (HEIGHT - ICON_SIZE) // 2

    glow = Image.new("RGBA", (ICON_SIZE + 48, ICON_SIZE + 48), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((0, 0, ICON_SIZE + 48, ICON_SIZE + 48), fill=(255, 210, 120, 50))
    canvas.alpha_composite(glow, (icon_x - 24, icon_y - 24))
    canvas.alpha_composite(icon, (icon_x, icon_y))

    draw_text_block(canvas, title_lines, subtitle)
    return canvas.convert("RGB")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for post in POSTS:
        image = compose_thumbnail(post["title_lines"], post["subtitle"], post["item_id"])
        out_path = OUT_DIR / f"{post['slug']}.webp"
        image.save(out_path, format="WEBP", quality=92, method=6)
        assert image.size == (WIDTH, HEIGHT), out_path
        print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
