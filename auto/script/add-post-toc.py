#!/usr/bin/env python3
"""Insert a ## 목차 before the first section of posts that do not have one."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POSTS = ROOT / "_posts"

CHO = ["g", "kk", "n", "d", "tt", "r", "m", "b", "pp", "s", "ss", "", "j", "jj", "ch", "k", "t", "p", "h"]
JUNG = [
    "a", "ae", "ya", "yae", "eo", "e", "yeo", "ye", "o", "wa", "wae", "oe",
    "yo", "u", "wo", "we", "wi", "yu", "eu", "ui", "i",
]
JONG = [
    "", "k", "k", "k", "n", "n", "n", "t", "l", "l", "l", "l", "l", "l", "l", "l",
    "m", "p", "p", "t", "t", "ng", "t", "t", "k", "t", "p", "h",
]
SHORT = {
    "체크리스트": "checklist",
    "출발 전 체크리스트": "checklist",
    "짧은 체크리스트": "checklist",
    "관련 글": "related",
    "참고": "references",
    "정리": "summary",
}
HEADING = re.compile(r"^(#{1,4})\s+(.+?)\s*$")
ID_IN_IAL = re.compile(r"#[A-Za-z][A-Za-z0-9_-]*")
LEADING_NUM = re.compile(r"^\d+(?:-\d+)*\.\s+")


def romanize(text: str) -> str:
    out = []
    for ch in text:
        code = ord(ch)
        if 0xAC00 <= code <= 0xD7A3:
            idx = code - 0xAC00
            out.append(CHO[idx // 588])
            out.append(JUNG[(idx % 588) // 28])
            out.append(JONG[idx % 28])
        else:
            out.append(ch)
    slug = "".join(out).lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    if len(slug) > 48:
        slug = slug[:48].rstrip("-")
    return slug


def split_heading(text: str) -> tuple[str, str | None]:
    ial = re.search(r"\s*\{([^}]*)\}\s*$", text)
    if not ial:
        return text.strip(), None
    body = text[: ial.start()].strip()
    found = ID_IN_IAL.search(ial.group(1))
    return body, (found.group(0)[1:] if found else None)


def link_text(title: str) -> str:
    title = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", title)
    title = title.replace("**", "").replace("`", "")
    title = LEADING_NUM.sub("", title).strip()
    title = title.replace("[", "").replace("]", "")
    return title


class Item:
    def __init__(self, level: int, title: str, anchor: str) -> None:
        self.level = level
        self.title = title
        self.anchor = anchor
        self.children: list[Item] = []


def parse(lines: list[str]) -> tuple[list[tuple[int, int, str, str | None]], set[str]]:
    """Return (line_index, level, title, existing_id) and every explicit id."""
    headings = []
    used: set[str] = set()
    fence = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            fence = not fence
            continue
        if fence:
            continue
        match = HEADING.match(line)
        if not match:
            continue
        level = len(match.group(1))
        title, anchor = split_heading(match.group(2))
        if anchor:
            used.add(anchor)
        if level <= 3:
            headings.append((i, level, title, anchor))
        elif anchor:
            pass
    return headings, used


def assign(headings, used: set[str]) -> list[tuple[int, int, str, str, bool]]:
    """Return line, level, title, anchor, needs_write."""
    assigned = []
    for line, level, title, anchor in headings:
        if anchor:
            assigned.append((line, level, title, anchor, False))
            continue
        base = SHORT.get(link_text(title)) or romanize(title) or "part"
        if base[:1].isdigit():
            base = f"s-{base}"
        slug = base
        n = 2
        while slug in used:
            slug = f"{base}-{n}"
            n += 1
        used.add(slug)
        assigned.append((line, level, title, slug, True))
    return assigned


def build_tree(assigned) -> list[Item]:
    roots: list[Item] = []
    seen_h1 = 0
    current: Item | None = None
    for _line, level, title, anchor, _write in assigned:
        item = Item(level, link_text(title), anchor)
        if level == 1:
            seen_h1 += 1
            if seen_h1 == 1:
                continue
            roots.append(item)
            current = item
            continue
        if level == 2 and seen_h1 <= 1:
            roots.append(item)
            current = item
            continue
        if current is None:
            roots.append(item)
            current = item
            continue
        current.children.append(item)
    return roots


def render(roots: list[Item]) -> str:
    lines = ["## 목차", ""]
    for i, item in enumerate(roots, start=1):
        lines.append(f"{i}. [{item.title}](#{item.anchor})")
        for child in item.children:
            lines.append(f"    - [{child.title}](#{child.anchor})")
    lines.extend(["", "---", ""])
    return "\n".join(lines)


def first_section_line(assigned) -> int | None:
    seen_h1 = 0
    for line, level, _title, _anchor, _write in assigned:
        if level == 1:
            seen_h1 += 1
            if seen_h1 == 1:
                continue
            return line
        return line
    return None


def main() -> None:
    changed = 0
    for path in sorted(POSTS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if re.search(r"^## 목차\s*$", text, re.M):
            continue
        lines = text.splitlines()
        headings, used = parse(lines)
        assigned = assign(headings, used)
        insert_at = first_section_line(assigned)
        if insert_at is None:
            print("skip", path.name)
            continue
        title_seen = False
        for line, level, title, anchor, needs in assigned:
            if level == 1 and not title_seen:
                title_seen = True
                continue
            if not needs:
                continue
            raw = lines[line]
            hashes, rest = raw.split(" ", 1)
            body, _old = split_heading(rest)
            lines[line] = f"{hashes} {body} {{#{anchor}}}"
        block = render(build_tree(assigned)).splitlines()
        block.append("")
        if insert_at > 0 and lines[insert_at - 1].strip() != "":
            block = [""] + block
        lines[insert_at:insert_at] = block
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        changed += 1
        print(path.name, "sections", len(build_tree(assigned)))
    print("updated", changed)


if __name__ == "__main__":
    main()
