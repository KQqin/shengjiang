from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from config import SHARED_DIR

_CACHE: dict[str, Any] | None = None


def load_script_data() -> dict[str, Any]:
    global _CACHE
    if _CACHE is not None:
        return _CACHE

    path = SHARED_DIR / "script-data.json"
    if not path.is_file():
        raise FileNotFoundError(f"剧本数据不存在: {path}")

    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    required = ("phases", "roles", "voteForm", "maxPlayers", "maxConnections")
    for key in required:
        if key not in data:
            raise ValueError(f"script-data.json 缺少字段: {key}")

    _CACHE = data
    return data
