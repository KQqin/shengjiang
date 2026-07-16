from __future__ import annotations

import asyncio
import random
import secrets
from dataclasses import dataclass, field
from typing import Any

from fastapi import WebSocket

from services.player_content import build_player_content, public_role, unlocked_sections


@dataclass
class Player:
    id: str
    token: str
    nickname: str
    is_host: bool = False
    is_bot: bool = False
    role_id: str | None = None
    vote_truth: str | None = None
    vote_culprit: str | None = None
    websocket: WebSocket | None = None


@dataclass
class Room:
    code: str
    phase_index: int = 0
    host_player_id: str = ""
    players: dict[str, Player] = field(default_factory=dict)
    roles_taken: set[str] = field(default_factory=set)
    shared_clues: list[dict[str, Any]] = field(default_factory=list)


class RoomManager:
    def __init__(self, script_data: dict[str, Any]) -> None:
        self.script_data = script_data
        self.max_players = int(script_data.get("maxPlayers", 12))
        self.max_connections = int(script_data.get("maxConnections", 13))
        self.rooms: dict[str, Room] = {}
        self._ws_index: dict[int, str] = {}
        self._token_index: dict[str, tuple[str, str]] = {}
        self._host_cleanup_tasks: dict[str, asyncio.Task] = {}

    def _new_player_id(self) -> str:
        return secrets.token_hex(4)

    def _new_player_token(self) -> str:
        return secrets.token_urlsafe(16)

    def _register_token(self, room_code: str, player: Player) -> None:
        self._token_index[player.token] = (room_code, player.id)

    def _unregister_token(self, token: str) -> None:
        self._token_index.pop(token, None)

    def _create_code(self) -> str:
        while True:
            code = str(random.randint(100000, 999999))
            if code not in self.rooms:
                return code

    def _role_by_id(self, role_id: str) -> dict[str, Any] | None:
        for role in self.script_data["roles"]:
            if role["id"] == role_id:
                return role
        return None

    def _bind_ws(self, player: Player, ws: WebSocket) -> None:
        player.websocket = ws
        self._ws_index[id(ws)] = player.id

    def _unbind_ws(self, ws: WebSocket) -> None:
        self._ws_index.pop(id(ws), None)

    def get_player_by_ws(self, ws: WebSocket) -> Player | None:
        player_id = self._ws_index.get(id(ws))
        if not player_id:
            return None
        for room in self.rooms.values():
            if player_id in room.players:
                return room.players[player_id]
        return None

    def get_room_by_ws(self, ws: WebSocket) -> Room | None:
        player = self.get_player_by_ws(ws)
        if not player:
            return None
        for room in self.rooms.values():
            if player.id in room.players:
                return room
        return None

    def _count_non_host(self, room: Room) -> int:
        return sum(1 for p in room.players.values() if not p.is_host)

    def _count_real_connections(self, room: Room) -> int:
        return sum(1 for p in room.players.values() if p.websocket is not None)

    def _count_real_players(self, room: Room) -> int:
        return sum(1 for p in room.players.values() if not p.is_host and not p.is_bot)

    def _count_bots(self, room: Room) -> int:
        return sum(1 for p in room.players.values() if p.is_bot)

    def _host_player(self, room: Room) -> Player | None:
        return room.players.get(room.host_player_id)

    def _host_is_online(self, room: Room) -> bool:
        host = self._host_player(room)
        return bool(host and host.websocket is not None)

    def _is_game_started(self, room: Room) -> bool:
        """开局标志：12 个角色全部抽完"""
        return len(room.roles_taken) >= self.max_players

    def _lobby_closed_error(self, room: Room) -> str | None:
        if self._is_game_started(room):
            return None
        if not self._host_is_online(room):
            return "房间已关闭，请向教师索要新房间号"
        return None

    async def create_room(self, ws: WebSocket) -> Room:
        code = self._create_code()
        room = Room(code=code)

        host = Player(
            id=self._new_player_id(),
            token=self._new_player_token(),
            nickname="教师",
            is_host=True,
        )
        self._bind_ws(host, ws)
        room.players[host.id] = host
        room.host_player_id = host.id
        self.rooms[code] = room
        self._register_token(code, host)
        return room

    async def join_room(self, ws: WebSocket, code: str, nickname: str) -> dict[str, Any]:
        room = self.rooms.get(code)
        if not room:
            return {"error": "房间不存在"}
        lobby_err = self._lobby_closed_error(room)
        if lobby_err:
            return {"error": lobby_err}
        if self._is_game_started(room):
            return {"error": "游戏已开始，无法新加入"}
        if self._count_real_connections(room) >= self.max_connections:
            return {"error": "房间已满（最多 13 人）"}
        if self.get_player_by_ws(ws):
            return {"room": room, "player": self.get_player_by_ws(ws)}
        if self._count_non_host(room) >= self.max_players:
            return {"error": "玩家已满（12 个角色）"}

        player = Player(
            id=self._new_player_id(),
            token=self._new_player_token(),
            nickname=nickname or "玩家",
        )
        self._bind_ws(player, ws)
        room.players[player.id] = player
        self._register_token(code, player)
        return {"room": room, "player": player}

    async def rejoin_room(self, ws: WebSocket, code: str, token: str) -> dict[str, Any]:
        code = code.strip()
        token = token.strip()
        if not code or not token:
            return {"error": "缺少房间号或身份凭证"}

        loc = self._token_index.get(token)
        if not loc:
            return {"error": "身份凭证无效或已过期"}

        room_code, player_id = loc
        if room_code != code:
            return {"error": "房间号与身份不匹配"}

        room = self.rooms.get(code)
        if not room:
            return {"error": "房间不存在"}

        player = room.players.get(player_id)
        if not player:
            return {"error": "玩家席位已失效"}

        if not player.is_host:
            lobby_err = self._lobby_closed_error(room)
            if lobby_err:
                return {"error": lobby_err}

        existing = self.get_player_by_ws(ws)
        if existing and existing.id != player.id:
            return {"error": "当前连接已绑定其他玩家"}

        if player.websocket is not None and player.websocket is not ws:
            self._unbind_ws(player.websocket)

        if player.websocket is None and self._count_real_connections(room) >= self.max_connections:
            return {"error": "房间已满（最多 13 人）"}

        self._bind_ws(player, ws)
        if player.is_host:
            self._cancel_host_cleanup(room.code)
        return {"room": room, "player": player}

    async def check_room(self, ws: WebSocket) -> dict[str, Any]:
        room = self.get_room_by_ws(ws)
        player = self.get_player_by_ws(ws)
        if not room or not player:
            return {"closed": True, "reason": "gone"}
        if not player.is_host:
            lobby_err = self._lobby_closed_error(room)
            if lobby_err:
                return {"closed": True, "reason": "host_left"}
        return {
            "ok": True,
            "roomCode": room.code,
            "phaseIndex": room.phase_index,
            "gameStarted": self._is_game_started(room),
            "hostConnected": self._host_is_online(room),
        }

    async def close_room(self, ws: WebSocket) -> dict[str, Any]:
        room = self.get_room_by_ws(ws)
        player = self.get_player_by_ws(ws)
        if not room or not player:
            return {"error": "未加入房间"}
        if not player.is_host:
            return {"error": "仅教师可关闭房间"}
        if self._is_game_started(room):
            return {"error": "游戏已开始，请使用「结束游戏」"}
        await self._destroy_room(room, reason="host_left")
        return {"ok": True}

    async def end_game(self, ws: WebSocket) -> dict[str, Any]:
        room = self.get_room_by_ws(ws)
        player = self.get_player_by_ws(ws)
        if not room or not player:
            return {"error": "未加入房间"}
        if not player.is_host:
            return {"error": "仅教师可结束游戏"}
        if not self._is_game_started(room):
            return {"error": "尚未全员抽卡，无法结束游戏"}
        await self._destroy_room(room, reason="game_ended")
        return {"ok": True}

    def _cancel_host_cleanup(self, room_code: str) -> None:
        task = self._host_cleanup_tasks.pop(room_code, None)
        if task and not task.done():
            task.cancel()

    async def _destroy_room(self, room: Room, *, reason: str = "closed") -> None:
        self._cancel_host_cleanup(room.code)
        closed_payload = {
            "type": "ROOM_CLOSED",
            "reason": reason,
            "roomCode": room.code,
        }
        for player in list(room.players.values()):
            if not player.is_host and player.websocket:
                await self._send(player.websocket, closed_payload)
        if any(
            not p.is_host and p.websocket is not None for p in room.players.values()
        ):
            await asyncio.sleep(0.15)
        for player in list(room.players.values()):
            if not player.is_host and player.websocket:
                try:
                    await player.websocket.close(code=1000, reason="room closed")
                except Exception:
                    pass
        for player in list(room.players.values()):
            self._unregister_token(player.token)
            if player.websocket:
                self._unbind_ws(player.websocket)
                player.websocket = None
        self.rooms.pop(room.code, None)

    async def disconnect(self, ws: WebSocket) -> None:
        player = self.get_player_by_ws(ws)
        room = self.get_room_by_ws(ws)
        if not player or not room:
            return

        self._unbind_ws(ws)
        player.websocket = None

        if player.is_host and not self._is_game_started(room):
            await self._destroy_room(room, reason="host_left")
            return

        await self.broadcast_room(room)

    def _assign_random_role(self, room: Room, player: Player) -> bool:
        if player.is_host or player.role_id:
            return False

        available = [r for r in self.script_data["roles"] if r["id"] not in room.roles_taken]
        if not available:
            return False

        picked = random.choice(available)
        player.role_id = picked["id"]
        room.roles_taken.add(picked["id"])
        return True

    async def draw_role(self, ws: WebSocket) -> dict[str, Any]:
        room = self.get_room_by_ws(ws)
        player = self.get_player_by_ws(ws)
        if not room or not player:
            return {"error": "未加入房间"}
        if player.is_host:
            return {"error": "教师不能抽取角色"}
        if player.role_id:
            return {"error": "你已经拥有角色"}
        if self._is_game_started(room):
            return {"error": "游戏已开始，不能抽卡"}
        if not self._assign_random_role(room, player):
            return {"error": "角色已被抽完"}

        role = self._role_by_id(player.role_id)
        if role and player.websocket:
            await self._send(player.websocket, {"type": "ROLE_DRAWN", "role": public_role(role)})
            await self.send_player_content(room, player)
        await self.broadcast_room(room)
        return {"ok": True}

    async def next_phase(self, ws: WebSocket) -> dict[str, Any]:
        return await self._change_phase(ws, 1)

    async def prev_phase(self, ws: WebSocket) -> dict[str, Any]:
        return await self._change_phase(ws, -1)

    async def _change_phase(self, ws: WebSocket, delta: int) -> dict[str, Any]:
        room = self.get_room_by_ws(ws)
        player = self.get_player_by_ws(ws)
        if not room or not player:
            return {"error": "未加入房间"}
        if not player.is_host:
            return {"error": "仅教师可操作"}

        if delta > 0 and room.phase_index < len(self.script_data["phases"]) - 1:
            room.phase_index += 1
        elif delta < 0 and room.phase_index > 0:
            room.phase_index -= 1

        await self.broadcast_room(room)
        for p in room.players.values():
            if not p.is_host and p.role_id and p.websocket:
                await self.send_player_content(room, p)
        await self._auto_share_bot_clues(room)
        await self.broadcast_room(room)
        return {"ok": True}

    async def cast_vote(self, ws: WebSocket, truth: Any, culprit: Any) -> dict[str, Any]:
        room = self.get_room_by_ws(ws)
        player = self.get_player_by_ws(ws)
        if not room or not player:
            return {"error": "未加入房间"}
        if player.is_host:
            return {"error": "教师不能提交答案"}
        if room.phase_index != 5:
            return {"error": "当前不是投票阶段"}

        truth_text = str(truth or "").strip()
        culprit_text = str(culprit or "").strip()
        if not truth_text:
            return {"error": "请填写事件真相"}
        if not culprit_text:
            return {"error": "请填写核心元凶"}
        if len(truth_text) > 200:
            return {"error": "事件真相不超过 200 字"}
        if len(culprit_text) > 20:
            return {"error": "核心元凶不超过 20 字"}

        player.vote_truth = truth_text
        player.vote_culprit = culprit_text

        await self.broadcast_room(room)
        return {"ok": True}

    def _share_player_clue(self, room: Room, player: Player, clue_key: str) -> bool:
        """将玩家私人线索写入公开池；成功返回 True，已存在或无效返回 False。"""
        if player.is_host or not player.role_id:
            return False
        if clue_key not in unlocked_sections(room.phase_index):
            return False

        role = self._role_by_id(player.role_id)
        if not role:
            return False

        clue_index = 0 if clue_key == "clue1" else 1 if clue_key == "clue2" else -1
        if clue_index < 0 or clue_index >= len(role["privateClues"]):
            return False

        share_id = f"{player.id}:{clue_key}"
        if any(s.get("id") == share_id for s in room.shared_clues):
            return False

        label = "私人线索 ①" if clue_key == "clue1" else "私人线索 ②"
        room.shared_clues.append(
            {
                "id": share_id,
                "playerId": player.id,
                "playerName": player.nickname,
                "roleName": role["name"],
                "clueKey": clue_key,
                "title": f"{role['name']} · {label}",
                "content": role["privateClues"][clue_index],
                "sharedAt": int(__import__("time").time() * 1000),
                "fromBot": player.is_bot,
            }
        )
        return True

    async def _auto_share_bot_clues(self, room: Room) -> int:
        shared = 0
        for clue_key in ("clue1", "clue2"):
            for player in room.players.values():
                if not player.is_bot:
                    continue
                if self._share_player_clue(room, player, clue_key):
                    shared += 1
        return shared

    async def share_clue(self, ws: WebSocket, clue_key: str) -> dict[str, Any]:
        room = self.get_room_by_ws(ws)
        player = self.get_player_by_ws(ws)
        if not room or not player:
            return {"error": "未加入房间"}
        if player.is_host:
            return {"error": "教师不能公开线索"}
        if not player.role_id:
            return {"error": "请先抽取角色"}
        if player.is_bot:
            return {"error": "补位玩家线索由系统自动公开"}

        if clue_key not in unlocked_sections(room.phase_index):
            return {"error": "该线索尚未解锁"}

        role = self._role_by_id(player.role_id)
        if not role:
            return {"error": "角色数据异常"}

        clue_index = 0 if clue_key == "clue1" else 1 if clue_key == "clue2" else -1
        if clue_index < 0 or clue_index >= len(role["privateClues"]):
            return {"error": "无效线索"}

        share_id = f"{player.id}:{clue_key}"
        if any(s.get("id") == share_id for s in room.shared_clues):
            return {"error": "该线索已在主页公开"}

        self._share_player_clue(room, player, clue_key)
        await self.broadcast_room(room)
        return {"ok": True}

    def _add_bot(self, room: Room, nickname: str) -> Player:
        bot = Player(
            id=self._new_player_id(),
            token=self._new_player_token(),
            nickname=nickname,
            is_bot=True,
        )
        room.players[bot.id] = bot
        return bot

    async def auto_fill_roster(self, ws: WebSocket) -> dict[str, Any]:
        """教师：用补位玩家凑满 12 人，不影响真实玩家，并自动抽卡与公开线索。"""
        room = self.get_room_by_ws(ws)
        player = self.get_player_by_ws(ws)
        if not room or not player or not player.is_host:
            return {"error": "仅教师可操作"}
        if self._is_game_started(room):
            return {"error": "游戏已开始，无法补位"}

        missing = self.max_players - self._count_non_host(room)
        if missing <= 0:
            return {"error": "人数已满，无需补位"}

        bot_count = self._count_bots(room)
        added = 0
        for i in range(missing):
            self._add_bot(room, f"补位{bot_count + i + 1}")
            added += 1

        drawn = 0
        for p in room.players.values():
            if p.is_host or p.role_id:
                continue
            if self._assign_random_role(room, p):
                drawn += 1

        clues_shared = await self._auto_share_bot_clues(room)
        await self.broadcast_room(room)
        return {"ok": True, "added": added, "drawn": drawn, "cluesShared": clues_shared}

    async def dev_fill_players(self, ws: WebSocket, count: int = 11) -> dict[str, Any]:
        room = self.get_room_by_ws(ws)
        player = self.get_player_by_ws(ws)
        if not room or not player or not player.is_host:
            return {"error": "仅教师可操作"}

        bot_count = self._count_bots(room)
        slots = min(count, max(0, self.max_players - self._count_non_host(room)))
        for i in range(slots):
            self._add_bot(room, f"测试玩家{bot_count + i + 1}")

        await self.broadcast_room(room)
        return {"ok": True, "added": slots}

    async def dev_draw_all(self, ws: WebSocket) -> dict[str, Any]:
        room = self.get_room_by_ws(ws)
        player = self.get_player_by_ws(ws)
        if not room or not player or not player.is_host:
            return {"error": "仅教师可操作"}

        drawn = 0
        for p in room.players.values():
            if not p.is_host and not p.role_id and self._assign_random_role(room, p):
                if p.websocket and p.role_id:
                    role = self._role_by_id(p.role_id)
                    if role:
                        await self._send(p.websocket, {"type": "ROLE_DRAWN", "role": public_role(role)})
                        await self.send_player_content(room, p)
                drawn += 1

        await self.broadcast_room(room)
        return {"ok": True, "drawn": drawn}

    async def dev_auto_vote(self, ws: WebSocket) -> dict[str, Any]:
        room = self.get_room_by_ws(ws)
        player = self.get_player_by_ws(ws)
        if not room or not player or not player.is_host:
            return {"error": "仅教师可操作"}
        if room.phase_index != 5:
            return {"error": "当前不是投票阶段"}

        truths = [
            "苏小禾涂改账本引发连锁反应，无人贪污",
            "三人互泼脏水，根子在账册涂改",
            "陈怀安知情未报，小问题酿成大风波",
            "林大山盘点马虎，账房库房互相推责",
        ]
        culprits = [r["name"] for r in self.script_data["roles"]]
        voted = 0
        for p in room.players.values():
            if p.is_host or (p.vote_truth and p.vote_culprit):
                continue
            p.vote_truth = random.choice(truths)
            p.vote_culprit = random.choice(culprits)
            voted += 1

        await self.broadcast_room(room)
        return {"ok": True, "voted": voted}

    async def dev_clear_bots(self, ws: WebSocket) -> dict[str, Any]:
        room = self.get_room_by_ws(ws)
        player = self.get_player_by_ws(ws)
        if not room or not player or not player.is_host:
            return {"error": "仅教师可操作"}

        removed = 0
        to_delete: list[str] = []
        for pid, p in room.players.items():
            if p.is_bot:
                if p.role_id:
                    room.roles_taken.discard(p.role_id)
                to_delete.append(pid)

        for pid in to_delete:
            del room.players[pid]
            removed += 1

        await self.broadcast_room(room)
        return {"ok": True, "removed": removed}

    async def send_player_content(self, room: Room, player: Player) -> None:
        if player.is_host or not player.role_id or not player.websocket:
            return
        role = self._role_by_id(player.role_id)
        if not role:
            return
        content = build_player_content(role, room.phase_index, self.script_data)
        await self._send(
            player.websocket,
            {"type": "PLAYER_CONTENT", "content": content, "phaseIndex": room.phase_index},
        )

    def serialize_room(self, room: Room) -> dict[str, Any]:
        phase = self.script_data["phases"][room.phase_index]
        players = []
        vote_submissions = []
        for p in room.players.values():
            role = self._role_by_id(p.role_id) if p.role_id else None
            has_voted = bool(p.vote_truth and p.vote_culprit)
            players.append(
                {
                    "id": p.id,
                    "nickname": p.nickname,
                    "isHost": p.is_host,
                    "isBot": p.is_bot,
                    "connected": p.websocket is not None,
                    "roleId": p.role_id,
                    "roleName": role["name"] if role else None,
                    "roleTitle": role["title"] if role else None,
                    "hasVoted": has_voted,
                    "voteTruth": p.vote_truth,
                    "voteCulprit": p.vote_culprit,
                }
            )
            if not p.is_host and has_voted:
                vote_submissions.append(
                    {
                        "playerId": p.id,
                        "nickname": p.nickname,
                        "roleName": role["name"] if role else None,
                        "truth": p.vote_truth,
                        "culprit": p.vote_culprit,
                    }
                )

        student_count = sum(1 for p in players if not p["isHost"])
        real_student_count = sum(1 for p in players if not p["isHost"] and not p["isBot"])
        voted_count = sum(1 for p in players if not p["isHost"] and p["hasVoted"])

        return {
            "code": room.code,
            "phaseIndex": room.phase_index,
            "phase": phase,
            "playerCount": student_count,
            "realPlayerCount": real_student_count,
            "botCount": sum(1 for p in players if p["isBot"]),
            "maxPlayers": self.max_players,
            "connectionCount": self._count_real_connections(room),
            "maxConnections": self.max_connections,
            "players": players,
            "voteSubmissions": vote_submissions,
            "votedCount": voted_count,
            "rolesRemaining": len(self.script_data["roles"]) - len(room.roles_taken),
            "rolesDrawn": len(room.roles_taken),
            "gameStarted": self._is_game_started(room),
            "hostConnected": self._host_is_online(room),
            "publicCluesReleased": room.phase_index >= 4,
            "sharedClues": list(room.shared_clues),
            "incident": self.script_data["incident"] if room.phase_index >= 1 else None,
        }

    async def _send(self, ws: WebSocket, payload: dict[str, Any]) -> None:
        try:
            await ws.send_json(payload)
        except Exception:
            pass

    async def broadcast_room(self, room: Room) -> None:
        state = self.serialize_room(room)
        for player in room.players.values():
            if player.websocket is not None:
                await self._send(player.websocket, {"type": "ROOM_STATE", "room": state})
