"""核对「找的」文件夹与首页 courses.js 是否一一对应。"""
from __future__ import annotations

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ZHAO = Path(r"c:\Users\覃均昊\Desktop\1.0\造个新号\首页的图片\首页的图片\找的")
PAO = Path(r"c:\Users\覃均昊\Desktop\1.0\造个新号\首页的图片\首页的图片\跑的")
COURSES_JS = ROOT / "frontend" / "src" / "data" / "courses.js"
COVERS = ROOT / "shared" / "assets" / "course-covers"


def main() -> None:
    zhao = sorted(os.path.splitext(f)[0] for f in os.listdir(ZHAO))
    pao = sorted(os.path.splitext(f)[0] for f in os.listdir(PAO))
    js = COURSES_JS.read_text(encoding="utf-8")
    titles = re.findall(r"title: '([^']+)'", js)
    covers = re.findall(r"cover: '([^']+)'", js)

    print("=== 找的文件夹 ===")
    for t in zhao:
        print(f"  {t}")

    print("\n=== 跑的文件夹 ===")
    for t in pao:
        print(f"  {t}")

    print(f"\n首页 courses 共 {len(titles)} 门")
    missing = [t for t in zhao if t not in titles]
    extra = [t for t in titles if t not in zhao and t not in pao]
    print("找的有但首页无:", missing or "无")
    print("首页有但找的不含(应为跑的):", extra or "无")

    print("\n=== 封面文件 ===")
    for c in courses_with_cover(js):
        cid, title, cover = c
        path = ROOT / "shared" / cover.replace("assets/", "assets/")
        ok = path.is_file()
        print(f"  [{ 'OK' if ok else 'MISSING' }] id={cid} {title} -> {cover}")

    if missing:
        raise SystemExit(1)
    print("\n全部「找的」课件已在首页 courses 中。")


def courses_with_cover(js: str) -> list[tuple[int, str, str]]:
    rows: list[tuple[int, str, str]] = []
    for block in re.findall(r"\{ id: (\d+), title: '([^']+)'.*?cover: '([^']+)' \}", js):
        rows.append((int(block[0]), block[1], block[2]))
    return rows


if __name__ == "__main__":
    main()
