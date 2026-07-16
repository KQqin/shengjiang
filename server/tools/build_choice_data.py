"""从 _choice_extracted.txt 生成 frontend/src/data/history-choice-data.js。"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT.parent / "_choice_extracted.txt"
OUT = ROOT / "frontend" / "src" / "data" / "history-choice-data.js"

CHAR_IDS = {
    "刘启耀": "liu-qiyao",
    "张其德": "zhang-qide",
    "毛泽民": "mao-zemin",
    "何叔衡": "he-shuheng",
}

MARK_RE = re.compile(r"【标记：(\S+?)】|（(失范|摇摆|正向)）")


def parse_mark(text: str) -> str:
    m = re.search(r"【标记：(\S+?)】", text)
    if m:
        return m.group(1)
    marks = MARK_RE.findall(text)
    for _, tag in reversed(marks):
        if tag in ("失范", "摇摆", "正向"):
            return tag
    return "摇摆"


def clean_option_text(text: str) -> str:
    text = MARK_RE.sub("", text).strip()
    text = re.sub(r"^选项", "", text)
    return text.strip("：: ").strip()


def parse_option_line(line: str) -> tuple[str, str] | None:
    m = re.match(r"^(?:选项)?([ABC])[：:]\s*(.+)$", line.strip())
    if not m:
        return None
    return m.group(1), m.group(2).strip()


def parse_deduction_line(line: str) -> tuple[str, str, str] | None:
    m = re.match(r"^([ABC])推演[：:]\s*(.+)$", line.strip())
    if m:
        body = m.group(2)
        return m.group(1), body, parse_mark(body)
    m = re.match(r"^推演[：:]\s*(.+)$", line.strip())
    if m:
        body = m.group(1)
        return "", body, parse_mark(body)
    return None


def split_story(lines: list[str]) -> str:
    return "\n".join(x.strip() for x in lines if x.strip())


def parse_choice_section(text: str, *, infer_node: bool) -> dict:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    story_lines: list[str] = []
    options: list[dict] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("跳转") and options:
            if infer_node:
                nm = re.search(r"第三轮(\w+)", line)
                if nm:
                    options[-1]["node"] = nm.group(1)
            i += 1
            continue
        parsed = parse_option_line(line)
        if parsed:
            key, txt = parsed
            options.append(
                {
                    "key": key,
                    "text": clean_option_text(txt),
                    "deduction": "",
                    "mark": "摇摆",
                    **({"node": ""} if infer_node else {}),
                }
            )
            i += 1
            continue
        ded = parse_deduction_line(line)
        if ded and options:
            k, body, mark = ded
            target = options[-1] if not k else next((o for o in options if o["key"] == k), options[-1])
            target["deduction"] = MARK_RE.sub("", body).strip()
            target["mark"] = mark
            nm = re.search(r"第三轮(\w+)", line)
            if infer_node and nm:
                target["node"] = nm.group(1)
            i += 1
            if infer_node and i < len(lines) and lines[i].startswith("跳转"):
                nm2 = re.search(r"第三轮(\w+)", lines[i])
                if nm2:
                    target["node"] = nm2.group(1)
                i += 1
            continue
        if not options:
            story_lines.append(line)
        i += 1
    return {"story": split_story(story_lines), "options": options}


def parse_round1(content: str) -> dict:
    m = re.search(r"第一轮主线剧情\n(.+?)\n分支1", content, re.S)
    if not m:
        return {"story": "", "options": []}
    return parse_choice_section(m.group(1), infer_node=False)


def parse_characters(raw: str) -> list[dict]:
    chars: list[dict] = []
    parts = re.split(r"角色[一二三四]：", raw)[1:]
    for part in parts:
        header, body = part.split("\n", 1)
        name = header.split("（")[0].strip()
        cid = CHAR_IDS.get(name)
        if not cid:
            continue
        end = body.find("综合结局判定标准")
        if end < 0:
            continue
        content = body[:end]
        endings_block = body[end:]

        round1 = parse_round1(content)
        # attach branch keys to round1 options
        for opt in round1["options"]:
            opt["branch"] = opt["key"]

        r2_branches: dict[str, dict] = {}
        for branch_key in ("A", "B", "C"):
            bm = re.search(
                rf"分支\d+：第一轮选{branch_key}.+?→ 第二轮剧情\n(.+?)(?=\n分支\d+：|\n第三轮|\Z)",
                content,
                re.S,
            )
            if bm:
                r2_branches[branch_key] = parse_choice_section(bm.group(1), infer_node=True)

        r3_nodes: dict[str, dict] = {}
        for nm in re.finditer(r"\n第三轮(\w+)\s*(?:（[^）]*）)*\s*\n", content):
            start = nm.end()
            nxt = re.search(
                r"\n第三轮(\w+)\s*(?:（[^）]*）)*\s*\n|\n分支\d+：|\n[\u4e00-\u9fff]+综合结局",
                content[start:],
            )
            end = start + nxt.start() if nxt else len(content)
            block = content[start:end]
            sec = parse_choice_section(block, infer_node=False)
            if sec["options"] and nm.group(1) not in r3_nodes:
                for opt in sec["options"]:
                    if not opt.get("deduction"):
                        opt["deduction"] = f"你选择了：{opt['text']}"
                r3_nodes[nm.group(1)] = sec

        ending_rules = []
        for em in re.finditer(r"(\d+)\.\s*(.+?)→【(.+?)】\n总结：(.+?)(?=\n\d+\.|\n统一|\Z)", endings_block, re.S):
            ending_rules.append(
                {
                    "id": em.group(3),
                    "rule": em.group(2).strip(),
                    "summary": em.group(4).strip(),
                }
            )

        chars.append(
            {
                "id": cid,
                "name": name,
                "title": header[header.find("（") + 1 : header.find("）")] if "（" in header else "",
                "intro": "",
                "round1": round1,
                "round2": r2_branches,
                "round3": r3_nodes,
                "endingRules": ending_rules,
            }
        )
    return chars


def load_card_intros(raw: str) -> dict[str, str]:
    intros = {}
    block = re.search(r"4套人物素材卡完整文案\n(.+?)页面3", raw, re.S)
    if not block:
        return intros
    lines = [l.strip() for l in block.group(1).splitlines() if l.strip()]
    i = 0
    while i < len(lines):
        if lines[i] in CHAR_IDS and i + 2 < len(lines):
            intros[lines[i]] = lines[i + 2]
            i += 3
        else:
            i += 1
    return intros


def main() -> None:
    raw = SRC.read_text(encoding="utf-8")
    stop = raw.find("第二部分 组件C")
    game_raw = raw[:stop] if stop > 0 else raw

    title_m = re.search(r"游戏大标题\s*(.+)", game_raw)
    title = title_m.group(1).strip() if title_m else "历史抉择生成器 · 青春守初心 廉洁担使命"

    announce_m = re.search(r"三、公告固定文案（弹窗内容）\n(.+?)页面2", game_raw, re.S)
    announcement = announce_m.group(1).strip() if announce_m else ""

    global_endings = {}
    ge = re.search(r"统一结局四档通用思政总结文案\n(.+?)第二部分", raw, re.S)
    if ge:
        for em in re.finditer(r"(\d+)\.\s*【(.+?)】\n(.+?)(?=\n\d+\.\s*【|\Z)", ge.group(1), re.S):
            global_endings[em.group(2)] = em.group(3).strip()

    characters = parse_characters(game_raw)
    intros = load_card_intros(game_raw)
    for c in characters:
        if intros.get(c["name"]):
            c["intro"] = intros[c["name"]]

    # fallback intros from doc table
    fallback = {
        "刘启耀": "自带干粮办公的省主席，苏区突围后身负重伤，贴身保管党组织13根金条，乞讨两年分文未动公款",
        "张其德": "苏区好管家，手握财政大权，厉行勤俭节约，拒绝公物私用，带领群众突破经济封锁",
        "毛泽民": "红色财经奠基人，严守财务纪律，倡导不乱花一个铜板，打造廉洁苏区金融体系",
        "何叔衡": "苏区包公，铁面反腐，不惧恐吓威胁，坚决查处党内贪腐分子，守护苏区清风正气",
    }
    for c in characters:
        if not c.get("intro"):
            c["intro"] = fallback.get(c["name"], "")

    data = {
        "title": title,
        "announcement": announcement,
        "characters": characters,
        "globalEndings": global_endings,
        "endingOrder": ["赤胆守廉者", "迷途知返者", "底线摇摆者", "初心失守者"],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    js = "/** 历史抉择生成器 · 由 server/tools/build_choice_data.py 生成，请勿手改 */\n"
    js += f"export const historyChoiceGame = {json.dumps(data, ensure_ascii=False, indent=2)}\n"
    OUT.write_text(js, encoding="utf-8")

    for c in characters:
        r2n = len(c["round2"])
        r3n = len(c["round3"])
        r1n = len(c["round1"]["options"])
        print(f"{c['name']}: r1={r1n} opts, r2 branches={r2n}, r3 nodes={r3n}, endings={len(c['endingRules'])}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
