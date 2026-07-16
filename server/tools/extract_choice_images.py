"""从 历史抉择生成器.docx 提取图片并建立映射，输出 manifest.json。"""
from __future__ import annotations

import json
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCX = next(f for f in (ROOT.parent).glob("*.docx") if f.stat().st_size > 100_000_000)
OUT_DIR = ROOT / "shared" / "assets" / "history-choice"
MANIFEST = OUT_DIR / "manifest.json"

CHAR_NAMES = ["刘启耀", "张其德", "毛泽民", "何叔衡"]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    chars_dir = OUT_DIR / "characters"
    scenes_dir = OUT_DIR / "scenes"
    chars_dir.mkdir(exist_ok=True)
    scenes_dir.mkdir(exist_ok=True)

    with zipfile.ZipFile(DOCX) as z:
        rels = z.read("word/_rels/document.xml.rels").decode("utf-8")
        doc = z.read("word/document.xml").decode("utf-8")

        rid_map: dict[str, str] = {}
        for m in re.finditer(r'Id="(rId\d+)"[^>]*Target="media/(image\d+\.(?:png|jpeg|jpg))"', rels):
            rid_map[m.group(1)] = m.group(2)

        # 按段落顺序收集：文本 + 紧随其后的图片
        paras = doc.split("</w:p>")
        sequence: list[dict] = []
        pending_text = ""

        for p in paras:
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

        # 提取全部 media 到临时目录
        media_files = [n for n in z.namelist() if n.startswith("word/media/image") and not n.endswith("/")]
        extracted: dict[str, str] = {}
        for name in media_files:
            src_name = Path(name).name
            dest = OUT_DIR / "_raw" / src_name
            dest.parent.mkdir(parents=True, exist_ok=True)
            with z.open(name) as src, open(dest, "wb") as dst:
                shutil.copyfileobj(src, dst)
            extracted[src_name] = str(dest.relative_to(ROOT)).replace("\\", "/")

    # 分析：找人物卡图片（文本含角色名）
    char_portraits: dict[str, str] = {}
    for item in sequence:
        for name in CHAR_NAMES:
            if name in item["text"] and name not in char_portraits:
                char_portraits[name] = item["image"]

    # 找场景图：含「第X轮」或「主线剧情」附近的图
    scene_hints: list[dict] = []
    for i, item in enumerate(sequence):
        t = item["text"]
        if any(k in t for k in ("第一轮", "第二轮", "第三轮", "主线剧情", "分支")):
            scene_hints.append({"hint": t[:100], "image": item["image"], "index": i})

    # 复制人物肖像
    char_files: dict[str, str] = {}
    for name, img in char_portraits.items():
        cid = {"刘启耀": "liu-qiyao", "张其德": "zhang-qide", "毛泽民": "mao-zemin", "何叔衡": "he-shuheng"}[name]
        ext = Path(img).suffix
        dest_name = f"{cid}{ext}"
        shutil.copy2(OUT_DIR / "_raw" / img, chars_dir / dest_name)
        char_files[cid] = f"shared/assets/history-choice/characters/{dest_name}"

    manifest = {
        "source": DOCX.name,
        "charPortraits": char_files,
        "sequenceSample": sequence[:30],
        "sceneHints": scene_hints[:40],
        "totalImages": len(extracted),
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"docx: {DOCX.name}")
    print(f"extracted {len(extracted)} images")
    print("char portraits:", char_files)
    print(f"scene hints: {len(scene_hints)}")
    print(f"wrote {MANIFEST}")


if __name__ == "__main__":
    main()
