"""建立剧情/推演/人物图与 history-choice-data 的映射，写入 assets 并更新数据。"""
from __future__ import annotations

import json
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCX = next(f for f in (ROOT.parent).glob("*.docx") if f.stat().st_size > 100_000_000)
OUT_DIR = ROOT / "shared" / "assets" / "history-choice"
RAW_DIR = OUT_DIR / "_raw"
DATA_JS = ROOT / "frontend" / "src" / "data" / "history-choice-data.js"

CHAR_IDS = {
    "刘启耀": "liu-qiyao",
    "张其德": "zhang-qide",
    "毛泽民": "mao-zemin",
    "何叔衡": "he-shuheng",
}


def norm(s: str) -> str:
    return re.sub(r"\s+", "", s)


def load_sequence() -> list[dict]:
    with zipfile.ZipFile(DOCX) as z:
        rels = z.read("word/_rels/document.xml.rels").decode("utf-8")
        doc = z.read("word/document.xml").decode("utf-8")

    rid_map: dict[str, str] = {}
    for m in re.finditer(r'Id="(rId\d+)"[^>]*Target="media/(image\d+\.(?:png|jpeg|jpg))"', rels):
        rid_map[m.group(1)] = m.group(2)

    sequence: list[dict] = []
    pending_text = ""
    for p in doc.split("</w:p>"):
        texts = re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p)
        text = "".join(texts).strip()
        blips = re.findall(r'r:embed="(rId\d+)"', p)
        if text:
            pending_text = text
        for rid in blips:
            img = rid_map.get(rid)
            if img:
                sequence.append({"text": pending_text or text, "image": img})
                pending_text = ""
    return sequence


def is_deduction(text: str) -> bool:
    return bool(re.match(r"^[ABC]?推演[：:]", text) or text.startswith("推演："))


def is_summary(text: str) -> bool:
    return text.startswith("总结：")


def find_image(text: str, seq: list[dict], used: set[str]) -> str | None:
    key = norm(text)[:40]
    for item in seq:
        if item["image"] in used:
            continue
        if norm(item["text"])[:40] == key:
            return item["image"]
    for item in seq:
        if item["image"] in used:
            continue
        if key in norm(item["text"]) or norm(item["text"])[:40] in key:
            return item["image"]
    return None


def copy_image(img: str, subpath: str) -> str:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    src = RAW_DIR / img
    if not src.exists():
        with zipfile.ZipFile(DOCX) as z:
            src.parent.mkdir(parents=True, exist_ok=True)
            with z.open(f"word/media/{img}") as s, open(src, "wb") as d:
                d.write(s.read())
    dest = OUT_DIR / subpath
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.resolve() == src.resolve():
        return f"shared/assets/history-choice/{subpath.replace(chr(92), '/')}"
    if not dest.exists() or dest.stat().st_size != src.stat().st_size:
        try:
            shutil.copy2(src, dest)
        except OSError:
            if not dest.exists():
                raise
    return f"shared/assets/history-choice/{subpath.replace(chr(92), '/')}"


def find_portraits(seq: list[dict]) -> dict[str, str]:
    """人物卡：文档中角色名段落附近的独立图片。"""
    portraits: dict[str, str] = {}
    for i, item in enumerate(seq):
        for name, cid in CHAR_IDS.items():
            if name in item["text"] and len(item["text"]) < 30 and name not in portraits:
                # 向前找最近一张非推演图
                for j in range(max(0, i - 3), i + 1):
                    t = seq[j]["text"]
                    if not is_deduction(t) and not is_summary(t):
                        portraits[name] = seq[j]["image"]
                        break
    # 兜底：各角色第一轮剧情前一张图（文档顺序）
    markers = {
        "刘启耀": "第五次反",
        "张其德": "闽浙赣苏区物资匮乏",
        "毛泽民": "中华苏维埃国家银行",
        "何叔衡": "临时最高法庭",
    }
    for name, marker in markers.items():
        if name in portraits:
            continue
        for item in seq:
            if marker in item["text"] and not is_deduction(item["text"]):
                # 人物肖像通常在剧情图之前；用 imageN-1 不可靠，搜角色名独立行
                break
    return portraits


def main() -> None:
    seq = load_sequence()
    print(f"sequence items: {len(seq)}")

    # raw 已由 extract_choice_images.py 提取时可跳过
    if not RAW_DIR.exists() or not any(RAW_DIR.glob("image*.png")):
        with zipfile.ZipFile(DOCX) as z:
            for name in z.namelist():
                if name.startswith("word/media/image") and not name.endswith("/"):
                    copy_image(Path(name).name, f"_raw/{Path(name).name}")

    # 人物肖像：在「页面2」区域，文本仅为角色名或身份短句
    portraits_raw: dict[str, str] = {}
    for item in seq:
        t = item["text"].strip()
        for name in CHAR_IDS:
            if t == name or (name in t and "（" in t and len(t) < 40):
                portraits_raw.setdefault(name, item["image"])

    # 若未命中，按各角色剧情起点前一张非推演图
    char_starts = [
        ("刘启耀", "第五次反"),
        ("张其德", "闽浙赣苏区物资匮乏"),
        ("毛泽民", "国家银行"),
        ("何叔衡", "最高法庭"),
    ]
    for name, marker in char_starts:
        if name in portraits_raw:
            continue
        for i, item in enumerate(seq):
            if marker in item["text"] and not is_deduction(item["text"]):
                if i > 0 and not is_deduction(seq[i - 1]["text"]):
                    portraits_raw[name] = seq[i - 1]["image"]
                break

    portrait_paths: dict[str, str] = {}
    for name, img in portraits_raw.items():
        cid = CHAR_IDS[name]
        ext = Path(img).suffix
        portrait_paths[cid] = copy_image(img, f"characters/{cid}{ext}")

    # 加载现有 data
    raw_js = DATA_JS.read_text(encoding="utf-8")
    m = re.search(r"export const historyChoiceGame = (\{[\s\S]+\})\s*$", raw_js)
    if not m:
        raise SystemExit("cannot parse history-choice-data.js")
    data = json.loads(m.group(1))

    used: set[str] = set(portraits_raw.values())
    img_index: dict[str, str] = {}

    def assign_story(story: str, prefix: str) -> str | None:
        img = find_image(story, seq, used)
        if not img:
            return None
        used.add(img)
        safe = re.sub(r"[^\w\-]+", "-", prefix).strip("-")[:80]
        rel = copy_image(img, f"scenes/{safe}{Path(img).suffix}")
        img_index[norm(story)[:60]] = rel
        return rel

    def assign_deduction(deduction: str, prefix: str) -> str | None:
        img = find_image(deduction, seq, used)
        if not img:
            # 推演文案在文档带 A推演： 前缀
            for item in seq:
                if item["image"] in used:
                    continue
                body = re.sub(r"^[ABC]推演[：:]", "", item["text"])
                body = re.sub(r"^推演[：:]", "", body)
                body = re.sub(r"【标记：.+?】", "", body).strip()
                if norm(body)[:30] == norm(deduction)[:30]:
                    img = item["image"]
                    break
        if not img:
            return None
        used.add(img)
        safe = re.sub(r"[^\w\-]+", "-", prefix).strip("-")[:80]
        rel = copy_image(img, f"deductions/{safe}{Path(img).suffix}")
        return rel

    for char in data["characters"]:
        cid = char["id"]

        r1_img = assign_story(char["round1"]["story"], f"{cid}-r1")
        if r1_img:
            char["round1"]["sceneImage"] = r1_img
        for opt in char["round1"]["options"]:
            d = assign_deduction(opt["deduction"], f"{cid}-r1-{opt['key']}")
            if d:
                opt["deductionImage"] = d

        for bk, branch in char["round2"].items():
            si = assign_story(branch["story"], f"{cid}-r2-{bk}")
            if si:
                branch["sceneImage"] = si
            for opt in branch["options"]:
                d = assign_deduction(opt["deduction"], f"{cid}-r2-{bk}-{opt['key']}")
                if d:
                    opt["deductionImage"] = d

        for nid, node in char["round3"].items():
            si = assign_story(node["story"], f"{cid}-r3-{nid}")
            if si:
                node["sceneImage"] = si
            for opt in node["options"]:
                d = assign_deduction(opt["deduction"], f"{cid}-r3-{nid}-{opt['key']}")
                if d:
                    opt["deductionImage"] = d

        for rule in char.get("endingRules", []):
            for item in seq:
                if item["image"] in used:
                    continue
                if rule["summary"][:20] in item["text"]:
                    used.add(item["image"])
                    eid = rule["id"]
                    rel = copy_image(item["image"], f"endings/{cid}-{eid}{Path(item['image']).suffix}")
                    rule["image"] = rel
                    break

        if char["round1"].get("sceneImage"):
            char["portrait"] = char["round1"]["sceneImage"]
        elif cid in portrait_paths:
            char["portrait"] = portrait_paths[cid]

    data["assetsBase"] = "shared/assets/history-choice"
    data["teacherMode"] = True

    js = "/** 历史抉择生成器 · 由 server/tools/build_choice_data.py + map_choice_images.py 生成 */\n"
    js += f"export const historyChoiceGame = {json.dumps(data, ensure_ascii=False, indent=2)}\n"
    DATA_JS.write_text(js, encoding="utf-8")

    stats = {"portraits": len(portrait_paths), "used": len(used), "total_seq": len(seq)}
    (OUT_DIR / "image-map-stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print("portraits:", portrait_paths)
    print("stats:", stats)
    print(f"updated {DATA_JS}")


if __name__ == "__main__":
    main()
