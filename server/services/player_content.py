from __future__ import annotations

from typing import Any


def unlocked_sections(phase_index: int) -> list[str]:
    sections = ["public"]
    if phase_index >= 1:
        sections.extend(["script", "secret", "allRoles", "background"])
    if phase_index >= 3:
        sections.append("clue1")
    if phase_index >= 4:
        sections.append("clue2")
    if phase_index >= 5:
        sections.append("vote")
    if phase_index >= 6:
        sections.append("reveal")
    return sections


def public_role(role: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": role["id"],
        "name": role["name"],
        "gender": role["gender"],
        "title": role["title"],
        "tag": role["tag"],
        "publicIntro": role["publicIntro"],
        "poster": role.get("poster"),
    }


def build_all_roles(script_data: dict[str, Any]) -> list[dict[str, Any]]:
    roles = []
    for role in script_data.get("roles", []):
        roles.append(
            {
                "id": role["id"],
                "name": role["name"],
                "title": role["title"],
                "publicIntro": role["publicIntro"],
                "introOrder": role.get("introOrder", 99),
            }
        )
    roles.sort(key=lambda r: r["introOrder"])
    return roles


def build_player_content(role: dict[str, Any], phase_index: int, script_data: dict[str, Any]) -> dict[str, Any]:
    unlocked = unlocked_sections(phase_index)
    content: dict[str, Any] = {"unlocked": unlocked}

    if "public" in unlocked:
        content["public"] = public_role(role)
    if "background" in unlocked:
        content["background"] = script_data.get("background", "")
    if "script" in unlocked:
        content["personalScript"] = role.get("personalScript", [])
    if "secret" in unlocked:
        content["secretTasks"] = role.get("secretTasks", [])
    if "allRoles" in unlocked:
        content["allRoles"] = build_all_roles(script_data)
    if "clue1" in unlocked:
        content["clue1"] = role["privateClues"][0]
    if "clue2" in unlocked:
        content["clue2"] = role["privateClues"][1]
    if "vote" in unlocked:
        content["voteForm"] = script_data.get("voteForm", {})
    if "reveal" in unlocked:
        content["truth"] = script_data["truth"]

    return content
