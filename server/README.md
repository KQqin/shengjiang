# 数智红途 · Python 后端

**FastAPI + uvicorn + WebSocket**，对齐 `frontend/README.md` 协议。

## 快速启动

```bash
cd server
pip install -r requirements.txt
python main.py
```

- 健康检查：http://localhost:3001/health
- 剧本数据：http://localhost:3001/shared/script-data.json
- WebSocket：ws://localhost:3001

开发者模式默认开启（`DEV_MODE=1`），支持教师端 `DEV_*` 虚拟玩家。

## 前端联调

```bash
# 终端 1
cd server && python main.py

# 终端 2
cd frontend && npm run dev
```

访问 http://localhost:5173 ，教师大屏会自动 `CREATE_ROOM`。

## 已实现协议

| 客户端 → 服务端 | 说明 |
|----------------|------|
| `CREATE_ROOM` | 教师创建房间 |
| `JOIN_ROOM` | 学生加入 |
| `REJOIN_ROOM` | 凭 `playerToken` 断线恢复 |
| `DRAW_ROLE` | 抽卡 |
| `NEXT_PHASE` / `PREV_PHASE` | 推进环节 |
| `CAST_VOTE` | 提交作答 `{ truth, culprit }` |
| `SHARE_CLUE` | 公开私人线索 |
| `DEV_*` | 开发工具（需 DEV_MODE=1） |
| `PING` | 心跳 |

| 服务端 → 客户端 | 说明 |
|----------------|------|
| `ROOM_CREATED` / `JOINED` / `ROOM_STATE` | 房间状态（含 `playerToken`、`connected`） |
| `ROLE_DRAWN` / `PLAYER_CONTENT` | 角色与解锁内容 |
| `ERROR` / `DEV_OK` / `PONG` | 辅助 |

## 目录

```
server/
├── main.py
├── config.py
├── api/websocket.py
└── services/
    ├── script_loader.py
    ├── player_content.py
    └── room_manager.py
```

## 环节（6+1）

| 序号 | 环节 | 学生端解锁 |
|------|------|------------|
| 0 | 入场抽卡 | 公开身份 |
| 1 | 读剧本 | 个人剧本、本场任务、全员简介 |
| 2 | 自我介绍 | （线下） |
| 3 | 一轮线索+公聊 | 私人线索① |
| 4 | 二轮线索 | 私人线索② + 公共线索 P1–P4 |
| 5 | 讨论投票 | 投票 |
| 6 | 揭晓 | 真相 |

重新生成剧本 JSON：`python tools/build_script_data.py`（读取工作区 doc 提取文本）

断线后**席位与角色保留**，凭 `playerToken` 重连：

```json
{ "type": "REJOIN_ROOM", "roomCode": "123456", "playerToken": "..." }
```

成功时仍返回 `JOINED`（`rejoined: true`），若已有角色会补发 `ROLE_DRAWN` + `PLAYER_CONTENT`。

`ROOM_STATE.players[]` 新增 `connected` 字段，教师端可区分在线/离线。

### 前端对接（最小改动）

**学生端 `script-role.vue`**

1. `JOINED` 后：`localStorage.setItem('szht_player_token', msg.playerToken)`，同时存 `roomCode`
2. `ws.on('connected')` 时：若有 token → `ws.send('REJOIN_ROOM', { roomCode, playerToken })`，否则保持原流程
3. `JOINED` 且 `msg.rejoined`：恢复 `joined`/`hasRole`/`drawVisible` 等 UI 状态
4. 可选：展示身份码供学生截图（`playerToken` 前 8 位）

**教师端 `script-host.vue`**

1. `ROOM_CREATED` 后存 `playerToken`
2. 刷新后 `connected` 时发 `REJOIN_ROOM` 而非 `CREATE_ROOM`（有 token 时）

## 待办

- [x] `REJOIN_ROOM` + `playerToken` 断线恢复
- [ ] 全组联调彩排
- [ ] 阿里云部署
