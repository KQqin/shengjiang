"""断线重连冒烟测试（本地执行：python test_rejoin.py）"""

from __future__ import annotations

import json

from fastapi.testclient import TestClient

import main as app_main
from main import app
from services.room_manager import RoomManager
from services.script_loader import load_script_data


def recv_until(ws, wanted: set[str], limit: int = 8) -> list[dict]:
    out: list[dict] = []
    seen: set[str] = set()
    for _ in range(limit):
        msg = json.loads(ws.receive_text())
        out.append(msg)
        seen.add(msg["type"])
        if wanted.issubset(seen):
            break
    return out


def run_test() -> None:
    app_main.room_manager = RoomManager(load_script_data())
    client = TestClient(app)

    with client.websocket_connect("/") as host_ws:
        host_ws.send_text(json.dumps({"type": "CREATE_ROOM"}))
        created = json.loads(host_ws.receive_text())
        assert created["type"] == "ROOM_CREATED"
        assert created.get("playerToken")
        room_code = created["roomCode"]
        # 消费广播的 ROOM_STATE
        json.loads(host_ws.receive_text())

        with client.websocket_connect("/") as student_ws:
            student_ws.send_text(
                json.dumps(
                    {"type": "JOIN_ROOM", "roomCode": room_code, "nickname": "小明"}
                )
            )
            joined = json.loads(student_ws.receive_text())
            assert joined["type"] == "JOINED"
            student_token = joined["playerToken"]
            player_id = joined["playerId"]

            # 消费广播 ROOM_STATE
            json.loads(student_ws.receive_text())

            student_ws.send_text(json.dumps({"type": "DRAW_ROLE"}))
            msgs = recv_until(student_ws, {"ROLE_DRAWN"})
            assert any(m["type"] == "ROLE_DRAWN" for m in msgs)

        # student_ws 关闭 = 断线，席位应保留

    with client.websocket_connect("/") as rejoin_ws:
        rejoin_ws.send_text(
            json.dumps(
                {
                    "type": "REJOIN_ROOM",
                    "roomCode": room_code,
                    "playerToken": student_token,
                }
            )
        )
        rejoined = json.loads(rejoin_ws.receive_text())
        assert rejoined["type"] == "JOINED"
        assert rejoined.get("rejoined") is True
        assert rejoined["playerId"] == player_id
        assert rejoined["playerToken"] == student_token

        msgs = recv_until(rejoin_ws, {"ROLE_DRAWN", "PLAYER_CONTENT"})
        types = {m["type"] for m in msgs}
        assert "ROLE_DRAWN" in types
        assert "PLAYER_CONTENT" in types

        # ROOM_STATE 中该玩家应 connected=true
        state_msgs = [m for m in msgs if m["type"] == "ROOM_STATE"]
        if state_msgs:
            me = next(p for p in state_msgs[-1]["room"]["players"] if p["id"] == player_id)
            assert me["connected"] is True
            assert me["roleId"] is not None

    print("REJOIN test OK")


if __name__ == "__main__":
    run_test()
