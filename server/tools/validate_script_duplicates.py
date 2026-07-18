"""检查个人剧本段落重复、任务重复、任务误入剧本。"""

from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from pathlib import Path

SCRIPT_JSON = Path(__file__).resolve().parents[2] / "shared" / "script-data.json"


def norm(text: str) -> str:
    return re.sub(r"\s+", "", text)


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, norm(a), norm(b)).ratio()


def has_long_overlap(a: str, b: str, min_len: int = 24) -> bool:
    na, nb = norm(a), norm(b)
    if len(na) < min_len or len(nb) < min_len:
        return False
    for i in range(len(na) - min_len + 1):
        if na[i : i + min_len] in nb:
            return True
    return False


def main() -> None:
    data = json.loads(SCRIPT_JSON.read_text(encoding="utf-8"))
    issues: list[str] = []
    semantic_notes: list[str] = []

    for role in data["roles"]:
        name = role["name"]
        script = role.get("personalScript") or []
        tasks = role.get("secretTasks") or []

        seen: dict[str, int] = {}
        for i, paragraph in enumerate(script):
            key = norm(paragraph)
            if key in seen:
                issues.append(f"[{name}] 段落完全重复: 第{seen[key] + 1}段 与 第{i + 1}段")
            else:
                seen[key] = i

        for i in range(len(script)):
            for j in range(i + 1, len(script)):
                ratio = similarity(script[i], script[j])
                if ratio >= 0.82 and norm(script[i]) != norm(script[j]):
                    issues.append(
                        f"[{name}] 段落高度相似({ratio:.0%}): 第{i + 1}段 与 第{j + 1}段"
                    )
                if has_long_overlap(script[i], script[j]):
                    issues.append(
                        f"[{name}] 段落长句重叠: 第{i + 1}段 ↔ 第{j + 1}段"
                    )

        task_seen: set[str] = set()
        for task in tasks:
            key = norm(task)
            if key in task_seen:
                issues.append(f"[{name}] 任务条目重复: {task}")
            task_seen.add(key)

        joined = "".join(script)
        for idx, task in enumerate(tasks):
            core = task.strip("。；; ")
            if len(core) >= 8 and core in joined:
                issues.append(f"[{name}] 任务#{idx + 1}原文出现在个人剧本: {task}")

        # 语义层：常见「风波后」二次展开
        storm_blocks = [p for p in script if "风波" in p and ("爆发后" in p or "突发" in p or "出来之后" in p)]
        if len(storm_blocks) >= 3:
            semantic_notes.append(f"[{name}] 「风波后」心理段落较多({len(storm_blocks)}处)，建议人工通读是否啰嗦")

    # 跨角色：不应出现 secretTasks 被写进 personalScript 的标准任务句式
    standard_task_phrases = [
        "公正开展核查工作",
        "如实记录站内人员的反常行为",
        "依托现场客观痕迹与实物证据开展核查工作",
    ]
    for role in data["roles"]:
        joined = "".join(role.get("personalScript") or [])
        for phrase in standard_task_phrases:
            if phrase in joined:
                issues.append(f"[{role['name']}] 剧本含疑似任务模板句: {phrase}")

    print("=== 个人剧本重复/任务检查 ===")
    print(f"角色数: {len(data['roles'])}")

    unique_issues = list(dict.fromkeys(issues))
    if unique_issues:
        print(f"\n硬性问题 {len(unique_issues)} 条:")
        for item in unique_issues:
            print("-", item)
    else:
        print("\n未发现：完全重复段落 / 任务条目重复 / 任务原文粘贴进剧本")

    if semantic_notes:
        print(f"\n软性提示 {len(semantic_notes)} 条:")
        for item in semantic_notes:
            print("-", item)

    if unique_issues:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
