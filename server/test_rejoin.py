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


def skip_broadcast(ws) -> None:
    """消费一次 ROOM_STATE 广播（若存在）"""
    try:
        msg = json.loads(ws.receive_text())
        if msg.get("type") != "ROOM_STATE":
            raise AssertionError(f"expected ROOM_STATE, got {msg.get('type')}")
    except Exception:
        pass


def test_student_rejoin_while_host_online() -> None:
    """未开局时教师在线：学生断线可重连"""
    app_main.room_manager = RoomManager(load_script_data())
    client = TestClient(app)

    with client.websocket_connect("/") as host_ws:
        host_ws.send_text(json.dumps({"type": "CREATE_ROOM"}))
        created = json.loads(host_ws.receive_text())
        assert created["type"] == "ROOM_CREATED"
        room_code = created["roomCode"]
        skip_broadcast(host_ws)

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
            skip_broadcast(student_ws)

            student_ws.send_text(json.dumps({"type": "DRAW_ROLE"}))
            msgs = recv_until(student_ws, {"ROLE_DRAWN"})
            assert any(m["type"] == "ROLE_DRAWN" for m in msgs)

        # 仅学生断线，教师仍在线

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

            msgs = recv_until(rejoin_ws, {"ROLE_DRAWN", "PLAYER_CONTENT"})
            types = {m["type"] for m in msgs}
            assert "ROLE_DRAWN" in types
            assert "PLAYER_CONTENT" in types


def test_lobby_closed_when_host_leaves() -> None:
    """未开局时教师离开：房间销毁，学生无法加入或重连"""
    app_main.room_manager = RoomManager(load_script_data())
    client = TestClient(app)
    room_code = ""
    student_token = ""

    with client.websocket_connect("/") as host_ws:
        host_ws.send_text(json.dumps({"type": "CREATE_ROOM"}))
        created = json.loads(host_ws.receive_text())
        room_code = created["roomCode"]
        skip_broadcast(host_ws)

        with client.websocket_connect("/") as student_ws:
            student_ws.send_text(
                json.dumps(
                    {"type": "JOIN_ROOM", "roomCode": room_code, "nickname": "小红"}
                )
            )
            joined = json.loads(student_ws.receive_text())
            assert joined["type"] == "JOINED"
            student_token = joined["playerToken"]
            skip_broadcast(student_ws)

    # host_ws 与 student_ws 均已关闭 → 教师离开且未开局，房间应销毁

    with client.websocket_connect("/") as join_ws:
        join_ws.send_text(
            json.dumps(
                {"type": "JOIN_ROOM", "roomCode": room_code, "nickname": "新人"}
            )
        )
        err = json.loads(join_ws.receive_text())
        assert err["type"] == "ERROR"
        assert "房间不存在" in err["message"]

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
        err = json.loads(rejoin_ws.receive_text())
        assert err["type"] == "ERROR"
        assert (
            "房间" in err["message"]
            or "身份凭证" in err["message"]
        )


def run_test() -> None:
    test_student_rejoin_while_host_online()
    test_lobby_closed_when_host_leaves()
    print("REJOIN test OK")


if __name__ == "__main__":
    run_test()
