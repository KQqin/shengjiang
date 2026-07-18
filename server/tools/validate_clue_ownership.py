"""校验私人线索归属：不利/自指线索不应落在持有人手中。"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_JSON = ROOT / "shared" / "script-data.json"

# 持有人姓名出现在线索中，且动作为「自指不利」时的模式
SELF_INCRIMINATING = [
    (re.compile(r"你"), "线索不得使用第二人称「你」"),
]

# 角色 id -> 中文名
NAMES: dict[str, str] = {
    "chen-huaian": "陈怀安",
    "su-xiaohe": "苏小禾",
    "lin-dashan": "林大山",
    "wen-xiuning": "温秀宁",
    "zhou-mingyuan": "周明远",
    "zhao-qishan": "赵启山",
    "wu-qiulan": "吴秋岚",
    "ma-weiguo": "马卫国",
    "jiang-chengye": "江承业",
    "liu-guilan": "刘桂兰",
    "huang-xiaogen": "黄小根",
    "gao-shunping": "高顺平",
}

# 持有人不应在自己线索里直接暴露的核心秘密关键词
HOLDER_SECRET_KEYWORDS: dict[str, list[str]] = {
    "chen-huaian": ["监督履职缺位", "纵容他人违规", "未见其正式登记上报记录"],
    "su-xiaohe": ["苏小禾.*涂改", "反复擦拭账页，身形似苏小禾"],
    "lin-dashan": ["林大山按规领", "林大山按登记领", "林大山.*福利.*出库"],
    "wen-xiuning": ["温秀宁与周明远", "饼留后门", "粗粮饼"],
    "zhou-mingyuan": ["温秀宁与周明远", "饼留后门", "粗粮饼"],
    "zhao-qishan": ["督查流于形式", "前置监管缺位"],
    "wu-qiulan": ["知情不报", "二十号.*未报"],
    "ma-weiguo": ["勘查流程偷懒", "核查不彻底"],
    "gao-shunping": ["压下线报", "未见.*预警", "未见全站预警", "未见对应预警"],
}

# 主观/引导性表述（线索中不应出现）
SUBJECTIVE_PATTERNS = [
    (re.compile(r"矛头"), "含主观指向语「矛头」"),
    (re.compile(r"至少说明|更像|宜与|仅供参考|宜优先|不能单独定案|可缩小|可暂排除|证明不了|细想却|起初像|说不清|扑面|推上风口|更符合|研判·"), "含引导/评价用语"),
    (re.compile(r"——"), "含破折号后评价性补充（宜改为句号分句陈述）"),
]

ROMANCE_RED_HERRING = ["饼留后门", "温秀宁与周明远", "温秀宁归站", "外勤女办事员与值班小伙"]


def load_roles() -> list[dict]:
    data = json.loads(SCRIPT_JSON.read_text(encoding="utf-8"))
    return data.get("roles", [])


def check_self_reference(holder_id: str, holder_name: str, clue: str, idx: int) -> list[str]:
    issues: list[str] = []
    for pat, msg in SELF_INCRIMINATING:
        if pat.search(clue):
            issues.append(f"{holder_name} 线索[{idx}] {msg}: {clue[:40]}…")

    # 持有人姓名作主语 + 不利动作（领福利、压报等）
    bad_verbs = ["按规领", "领个人福利", "压下", "隐瞒", "涂改"]
    if holder_name in clue:
        for v in bad_verbs:
            if v in clue and not clue.strip().startswith("【"):
                pass
        # 姓名紧邻不利描述
        if re.search(rf"{re.escape(holder_name)}.{0,8}(按规领|领.*福利|涂改|压下|预警)", clue):
            issues.append(
                f"{holder_name} 线索[{idx}] 以本人为主语的不利描述: {clue[:50]}…"
            )
    return issues


def check_secret_overlap(holder_id: str, holder_name: str, clue: str, idx: int) -> list[str]:
    issues: list[str] = []
    for pat in HOLDER_SECRET_KEYWORDS.get(holder_id, []):
        if re.search(pat, clue):
            issues.append(
                f"{holder_name} 线索[{idx}] 触及本人秘密关键词「{pat}」: {clue[:50]}…"
            )
    return issues


def check_romance_red_herring(holder_id: str, holder_name: str, clue: str, idx: int) -> list[str]:
    if holder_id not in ("wen-xiuning", "zhou-mingyuan"):
        return []
    issues: list[str] = []
    for kw in ROMANCE_RED_HERRING:
        if kw in clue:
            issues.append(
                f"{holder_name} 线索[{idx}] 温周红鲱鱼不应在本人手中（含「{kw}」）"
            )
    return issues


def check_subjective(clue: str, holder_name: str, idx: int) -> list[str]:
    issues: list[str] = []
    for pat, msg in SUBJECTIVE_PATTERNS:
        if pat.search(clue):
            issues.append(f"{holder_name} 线索[{idx}] {msg}: {clue[:50]}…")
    return issues


def check_public_clues() -> list[str]:
    data = json.loads(SCRIPT_JSON.read_text(encoding="utf-8"))
    issues: list[str] = []
    for item in data.get("publicClues") or []:
        content = item.get("content") or ""
        cid = item.get("id", "?")
        for pat, msg in SUBJECTIVE_PATTERNS:
            if pat.search(content):
                issues.append(f"公共线索 {cid} {msg}: {content[:50]}…")
        if re.search(r"你", content):
            issues.append(f"公共线索 {cid} 含第二人称「你」")
    return issues


def main() -> int:
    if not SCRIPT_JSON.exists():
        print(f"缺少 {SCRIPT_JSON}")
        return 1

    roles = load_roles()
    issues: list[str] = []

    print("=== 私人线索归属校验 ===\n")
    for role in roles:
        rid = role["id"]
        name = role["name"]
        clues = role.get("privateClues") or []
        for i, clue in enumerate(clues):
            issues.extend(check_self_reference(rid, name, clue, i))
            issues.extend(check_secret_overlap(rid, name, clue, i))
            issues.extend(check_romance_red_herring(rid, name, clue, i))
            issues.extend(check_subjective(clue, name, i))

    issues.extend(check_public_clues())

    if issues:
        print(f"发现 {len(issues)} 处问题：\n")
        for item in issues:
            print(f"  - {item}")
        return 1

    print("全部 24 条私人线索 + 4 条公共线索通过校验（客观陈述 / 无自指不利 / 无温周红鲱鱼本人持有）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
