from __future__ import annotations

import json
from typing import Any

from fastapi import WebSocket

from config import DEV_MODE
from services.player_content import public_role
from services.room_manager import RoomManager


async def handle_message(ws: WebSocket, raw: str, rooms: RoomManager) -> None:
    try:
        msg: dict[str, Any] = json.loads(raw)
    except json.JSONDecodeError:
        await _send(ws, {"type": "ERROR", "message": "消息格式错误"})
        return

    msg_type = msg.get("type")
    if not msg_type:
        await _send(ws, {"type": "ERROR", "message": "缺少 type 字段"})
        return

    if msg_type == "CREATE_ROOM":
        room = await rooms.create_room(ws)
        host = room.players[room.host_player_id]
        await _send(
            ws,
            {
                "type": "ROOM_CREATED",
                "roomCode": room.code,
                "playerToken": host.token,
            },
        )
        await rooms.broadcast_room(room)
        return

    if msg_type == "JOIN_ROOM":
        result = await rooms.join_room(ws, str(msg.get("roomCode", "")).strip(), str(msg.get("nickname", "")))
        if result.get("error"):
            await _send(ws, {"type": "ERROR", "message": result["error"]})
            return
        player = result["player"]
        room = result["room"]
        await _send_joined(ws, room, player)
        if player.role_id:
            role = rooms._role_by_id(player.role_id)
            if role:
                await _send(ws, {"type": "ROLE_DRAWN", "role": public_role(role)})
            await rooms.send_player_content(room, player)
        await rooms.broadcast_room(room)
        return

    if msg_type == "REJOIN_ROOM":
        result = await rooms.rejoin_room(
            ws,
            str(msg.get("roomCode", "")).strip(),
            str(msg.get("playerToken", "")),
        )
        if result.get("error"):
            await _send(ws, {"type": "ERROR", "message": result["error"]})
            return
        player = result["player"]
        room = result["room"]
        await _send_joined(ws, room, player, rejoined=True)
        if player.role_id:
            role = rooms._role_by_id(player.role_id)
            if role:
                await _send(ws, {"type": "ROLE_DRAWN", "role": public_role(role)})
            await rooms.send_player_content(room, player)
        await rooms.broadcast_room(room)
        return

    if msg_type == "CLOSE_ROOM":
        result = await rooms.close_room(ws)
        if result.get("error"):
            await _send(ws, {"type": "ERROR", "message": result["error"]})
        else:
            await _send(ws, {"type": "ROOM_CLOSED"})
        return

    if msg_type == "END_GAME":
        result = await rooms.end_game(ws)
        if result.get("error"):
            await _send(ws, {"type": "ERROR", "message": result["error"]})
        else:
            await _send(ws, {"type": "ROOM_CLOSED", "reason": "game_ended"})
        return

    if msg_type == "DRAW_ROLE":
        result = await rooms.draw_role(ws)
        if result.get("error"):
            await _send(ws, {"type": "ERROR", "message": result["error"]})
        return

    if msg_type == "NEXT_PHASE":
        result = await rooms.next_phase(ws)
        if result.get("error"):
            await _send(ws, {"type": "ERROR", "message": result["error"]})
        return

    if msg_type == "PREV_PHASE":
        result = await rooms.prev_phase(ws)
        if result.get("error"):
            await _send(ws, {"type": "ERROR", "message": result["error"]})
        return

    if msg_type == "CAST_VOTE":
        result = await rooms.cast_vote(ws, msg.get("truth"), msg.get("culprit"))
        if result.get("error"):
            await _send(ws, {"type": "ERROR", "message": result["error"]})
        return

    if msg_type == "SHARE_CLUE":
        result = await rooms.share_clue(ws, str(msg.get("clueKey", "")))
        if result.get("error"):
            await _send(ws, {"type": "ERROR", "message": result["error"]})
        return

    if msg_type == "AUTO_FILL_ROSTER":
        result = await rooms.auto_fill_roster(ws)
        if result.get("error"):
            await _send(ws, {"type": "ERROR", "message": result["error"]})
        else:
            await _send(ws, {"type": "HOST_OK", "action": msg_type, **result})
        return

    if msg_type == "CHECK_ROOM":
        result = await rooms.check_room(ws)
        if result.get("closed"):
            await _send(ws, {"type": "ROOM_CLOSED", "reason": result.get("reason", "gone")})
        else:
            await _send(ws, {"type": "ROOM_OK", **result})
        return

    if msg_type == "PING":
        await _send(ws, {"type": "PONG"})
        return

    if msg_type in {"DEV_FILL_PLAYERS", "DEV_DRAW_ALL", "DEV_AUTO_VOTE", "DEV_CLEAR_BOTS"}:
        if not DEV_MODE:
            await _send(ws, {"type": "ERROR", "message": "开发者模式未启用"})
            return
        if msg_type == "DEV_FILL_PLAYERS":
            result = await rooms.dev_fill_players(ws, int(msg.get("count") or 11))
        elif msg_type == "DEV_DRAW_ALL":
            result = await rooms.dev_draw_all(ws)
        elif msg_type == "DEV_AUTO_VOTE":
            result = await rooms.dev_auto_vote(ws)
        else:
            result = await rooms.dev_clear_bots(ws)

        if result.get("error"):
            await _send(ws, {"type": "ERROR", "message": result["error"]})
        else:
            await _send(ws, {"type": "DEV_OK", "action": msg_type, **result})
        return

    await _send(ws, {"type": "ERROR", "message": f"未知消息类型: {msg_type}"})


async def _send_joined(
    ws: WebSocket,
    room,
    player,
    *,
    rejoined: bool = False,
) -> None:
    payload: dict[str, Any] = {
        "type": "JOINED",
        "roomCode": room.code,
        "isHost": player.is_host,
        "playerId": player.id,
        "playerToken": player.token,
    }
    if rejoined:
        payload["rejoined"] = True
    await _send(ws, payload)


async def _send(ws: WebSocket, payload: dict[str, Any]) -> None:
    try:
        await ws.send_json(payload)
    except Exception:
        pass
