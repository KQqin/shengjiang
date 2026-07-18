"""交叉校验时间线事件与各角色个人剧本。"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2].parent
SCRIPT_TXT = ROOT / "_extract_《苏区账目风波·物资总站的一天》12人玩家纯第一视角个人剧本.txt"
SCRIPT_JSON = Path(__file__).resolve().parents[2] / "shared" / "script-data.json"

SU_XIAOHE_MAR15 = (
    "上月十五号下午，你在账房涂改一笔粮油数目，纸面擦得发毛。"
    "陈会计从门口经过，只淡淡说了句「下次仔细点，尽量少涂改」，"
    "你红着脸点头，心里却松了口气——他没有声张，你也便把这件事抛在脑后。"
)

KEYWORDS = {
    "上月10号": ["上月十号", "10号"],
    "上月15号": ["十五号", "15号"],
    "上月18号": ["十八号", "18号"],
    "上月20号": ["二十号", "20号"],
    "上月23号": ["二十三", "23号"],
    "上月27号": ["二十七", "27号"],
    "上月29号": ["二十九", "29号"],
    "本月1号": ["本月一号", "本月1号", "一号清晨"],
}

EVENTS = [
    ("上月10号", ["苏小禾"], ["陈怀安"]),
    ("上月15号", ["陈怀安", "苏小禾"], []),
    ("上月18号", ["林大山", "苏小禾"], []),
    ("上月20号", ["陈怀安", "林大山", "刘桂兰"], ["吴秋岚"]),
    ("上月23号", ["温秀宁", "周明远", "黄小根"], []),
    ("上月27号", ["苏小禾", "吴秋岚"], []),
    ("上月29号", ["高顺平"], []),
    ("本月1号", ["马卫国"], []),
]


def parse_roles(raw: str) -> dict[str, str]:
    roles: dict[str, str] = {}
    chunks = re.split(r"角色\d+：", raw)
    names = re.findall(r"角色\d+：([^【]+)【人物简介", raw)
    for name, chunk in zip(names, chunks[1:]):
        name = name.split("｜")[0].strip()
        m = re.search(r"【个人剧本·仅自己可见】(.*?)【本场任务】", chunk, re.S)
        roles[name] = m.group(1) if m else ""
    return roles


def has_event(text: str, event_key: str) -> bool:
    return any(k in text for k in KEYWORDS[event_key])


def parse_roles_from_json() -> dict[str, str]:
    import json

    data = json.loads(SCRIPT_JSON.read_text(encoding="utf-8"))
    return {r["name"]: "\n".join(r.get("personalScript") or []) for r in data.get("roles", [])}


def main() -> None:
    if SCRIPT_JSON.exists():
        roles = parse_roles_from_json()
        source = "script-data.json"
    else:
        raw = SCRIPT_TXT.read_text(encoding="utf-8")
        roles = parse_roles(raw)
        source = "extracted txt"
    print(f"数据源: {source}")
    issues: list[str] = []

    print("=== 时间线事件剧本覆盖 ===")
    for event_key, required, must_not in EVENTS:
        print(f"\n[{event_key}]")
        for name in required:
            ok = has_event(roles.get(name, ""), event_key)
            print(f"  {name}: {'OK' if ok else 'MISSING'}")
            if not ok:
                issues.append(f"{event_key} 缺少 {name} 的记录")
        for name in must_not:
            if has_event(roles.get(name, ""), event_key):
                print(f"  {name}: 有记录 (时间线表标注为不应复述)")
            else:
                print(f"  {name}: 无记录 (符合私密事件设计)")

    # 林大山18号与苏小禾描述一致性
    lin = roles.get("林大山", "")
    su = roles.get("苏小禾", "")
    if "福利" in lin and "福利" in su:
        print("\n[上月18号 语义] 林大山/苏小禾均提及福利申领: OK")
    else:
        issues.append("上月18号 福利申领表述可能不一致")

    print("\n=== 问题汇总 ===")
    if issues:
        for item in issues:
            print("-", item)
        raise SystemExit(1)
    print("全部通过")


if __name__ == "__main__":
    main()
