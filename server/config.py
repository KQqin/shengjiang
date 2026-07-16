from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHARED_DIR = ROOT / "shared"
FRONTEND_H5_DIR = ROOT / "frontend" / "dist" / "build" / "h5"

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "3001"))

MAX_PLAYERS = 12
MAX_CONNECTIONS = 13
DEV_MODE = os.getenv("DEV_MODE", "0") == "1"
