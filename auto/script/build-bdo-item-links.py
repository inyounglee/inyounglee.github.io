# -*- coding: utf-8 -*-
"""Build _data/bdo_craft_items.json from paz_items names that appear in posts."""
from __future__ import annotations

import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POSTS = ROOT / "_posts"
OUT = ROOT / "_data" / "bdo_craft_items.json"

SUPABASE_URL = "https://yjswbueufqddkbgwxlul.supabase.co"
API_KEY = os.environ.get(
    "BDO_CRAFT_SUPABASE_ANON_KEY",
    "sb_publishable_F2DLc6yyi5pUhPfDo1aLOQ_E3sWY3Qi",
)

FRONT_MATTER = re.compile(r"^---\r?\n.*?\r?\n---\r?\n", re.S)
MD_LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")
MD_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]+\)")
MD_CODE = re.compile(r"```[\s\S]*?```|`[^`]+`")
HTML_TAG = re.compile(r"<[^>]+>")
PREFIX = re.compile(r"^\[[^\]]+\]\s*")
STAT_NAME = re.compile(
    r"^(최대 |공격력 \+|방어력 \+|경험치 \+|공헌도 경험치|재료 \d)"
)
HANGUL = re.compile(r"[가-힣]")

# 2글자 실재료. 일반 한국어와 겹치는 짧은 이름은 넣지 않는다.
KEEP_SHORT = {
    "호미",
    "마늘",
    "후추",
    "달걀",
    "우유",
    "감자",
    "강철",
    "루비",
    "아교",
    "잡초",
    "장작",
    "버섯",
    "유황",
    "모루",
    "서대",
    "한지",
    "빈 병",
    "금 열쇠",
    "은 열쇠",
    "닭 모이",
}

# 3글자 실아이템. 까마귀·두더지·집으로 같은 일반어는 제외한다.
KEEP_THREE = {
    "정제수",
    "증류수",
    "크론석",
    "고구마",
    "곡괭이",
    "무화과",
    "수테차",
    "씨감자",
    "아마포",
    "애벌레",
    "잔가지",
    "접착제",
    "토파즈",
    "통나무",
    "함포탄",
    "저격총",
    "화승총",
    "판옥선",
    "델로티아",
    "블랙스톤",
    "사파이어",
    "씨고구마",
    "에메랄드",
    "플라스크",
    "매의 눈",
}

BLOCK = {
    "고고학자",
    "고슴도치",
    "드벤크룬",
    "마그누스",
    "이빨요정",
    "나무 정령",
    "의상 상자",
    "에벤루스",
    "교역 경험치",
    "수렵 경험치",
    "연금 경험치",
    "요리 경험치",
    "재배 경험치",
    "채집 경험치",
    "전투 경험치",
    "항해 경험치",
}


def fetch_names() -> list[str]:
    names: set[str] = set()
    page = 1000
    offset = 0
    while True:
        query = urllib.parse.urlencode(
            {
                "select": "name",
                "exclude": "is.null",
                "name": "not.like.[이벤트]*",
                "item_id": "lt.16777216",
                "order": "name",
            }
        )
        url = f"{SUPABASE_URL}/rest/v1/paz_items?{query}"
        req = urllib.request.Request(
            url,
            headers={
                "apikey": API_KEY,
                "Authorization": f"Bearer {API_KEY}",
                "Range": f"{offset}-{offset + page - 1}",
                "Prefer": "count=exact",
            },
        )
        with urllib.request.urlopen(req) as resp:
            rows = json.loads(resp.read().decode("utf-8"))
            cr = resp.headers.get("Content-Range", "")
        if not rows:
            break
        for row in rows:
            name = (row.get("name") or "").strip()
            if name:
                names.add(name)
        print(f"fetched {offset}-{offset + len(rows) - 1} ({cr}) unique={len(names)}")
        if len(rows) < page:
            break
        offset += page
    return sorted(names)


def post_text() -> str:
    chunks: list[str] = []
    for path in POSTS.glob("*.md"):
        raw = path.read_text(encoding="utf-8")
        body = FRONT_MATTER.sub("", raw)
        body = MD_IMAGE.sub(" ", body)
        body = MD_LINK.sub(r"\1", body)
        body = MD_CODE.sub(" ", body)
        body = HTML_TAG.sub(" ", body)
        chunks.append(body)
    return "\n".join(chunks)


def hangul_len(name: str) -> int:
    return len(HANGUL.findall(name))


def usable(name: str) -> bool:
    if name in BLOCK:
        return False
    if STAT_NAME.match(name):
        return False
    n = hangul_len(name)
    if n < 2:
        return False
    if n == 2:
        return name in KEEP_SHORT
    if n == 3:
        return name in KEEP_THREE
    return True


def appearing(catalog: list[str], text: str) -> list[str]:
    hits: set[str] = set()
    for name in catalog:
        candidates = {name}
        stripped = PREFIX.sub("", name).strip()
        if stripped:
            candidates.add(stripped)
        for cand in candidates:
            if cand in text and usable(cand):
                hits.add(cand)
    redundant = {
        n
        for n in hits
        if n.endswith("의") and any(o != n and o.startswith(n + " ") for o in hits)
    }
    return sorted(hits - redundant, key=lambda n: (-len(n), n))


def main() -> None:
    catalog = fetch_names()
    text = post_text()
    hits = appearing(catalog, text)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(hits, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"catalog={len(catalog)} appearing={len(hits)} -> {OUT}")
    short = [n for n in hits if hangul_len(n) <= 3]
    print(f"short hangul<=3 = {len(short)}")
    for n in short:
        print(f"  {n}")


if __name__ == "__main__":
    main()
