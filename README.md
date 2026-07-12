# 胜jiang · 数智红途《苏区账目风波》

红色剧本杀联机项目：**1 教师大屏 + 12 学生手机**，服务于课程 11《革命年代青年榜样故事》。

```
shengjiang/
├── frontend/          # uni-app H5 前端（智学课堂 + 剧本杀）← 详见 frontend/README.md
├── server/            # Node.js + Express + WebSocket 后端
├── shared/            # 剧本数据 script-data.json + 后续素材 assets/
└── client/            # 旧版静态 HTML（已废弃，仅作参考）
```

---

## 快速启动（推荐）

**后端**

```bash
cd server
npm install
set DEV_MODE=1
npm start
```

**前端（开发）**

```bash
cd frontend
npm install
npm run dev
```

- 前端：http://localhost:5173  
- 后端：http://localhost:3001  
- 剧本数据：http://localhost:3001/shared/script-data.json  

**生产（单服托管）**

```bash
cd frontend && npm run build
cd ../server && npm start
```

访问 http://localhost:3001 即为打包后的 H5。

---

## 分工说明

| 模块 | 目录 | 负责人 | 状态 |
|------|------|--------|------|
| 智学课堂首页/课件 | `frontend/src/pages/index.vue` `classroom.vue` | 前端 | 已迁移完成 |
| 教师大屏 | `frontend/src/pages/script-host.vue` | 前端 | 已对接 WS |
| 学生端 | `frontend/src/pages/script-role.vue` | 前端 | UI 已完成，待接素材图 |
| 房间/抽卡/投票 | `server/room.js` | 后端 | 已实现 |
| 公开线索推送 | `SHARE_CLUE` | 后端 | 已实现（需联调确认） |
| 剧本素材 | `shared/assets/` | 运营/后端 | 待上传 |

**后端同学请优先阅读 [`frontend/README.md`](./frontend/README.md)**，内含页面说明、WS 协议扩展、素材路径约定与待办清单。

---

## 后端核心文档（节选）

完整协议见原 README 下文；人数规则：13 连接（1 教师 + 12 学生），12 个角色。

### 游戏阶段（phaseIndex 0–8）

| id | 名称 | 学生端解锁 |
|----|------|-----------|
| 0 | 入场 | 抽卡 |
| 3 | 第一轮问询 | + 秘密任务 |
| 4 | 搜证 I | + 私人线索 ① |
| 6 | 搜证 II | + 私人线索 ②；公共线索 |
| 7 | 投票 | + 投票选项 |
| 8 | 揭晓 | + 真相 |

### WebSocket 入口

`server/ws-handler.js` 路由，`server/room.js` 房间逻辑。

### 开发者模式

`DEV_MODE=1` 时支持：`DEV_FILL_PLAYERS`、`DEV_DRAW_ALL`、`DEV_AUTO_VOTE`、`DEV_CLEAR_BOTS`。

---

## 课堂部署

1. 教师电脑运行 `server`（建议先 `frontend` build）
2. 防火墙放行 **3001**
3. 学生手机同 WiFi 访问 `http://教师IP:3001`
4. 教师大屏创建房间 → 学生输入 6 位房间号加入抽卡

---

## 仓库说明

- 前端源码：`frontend/`（uni-app，勿提交 `node_modules`、`dist`）
- 后端源码：`server/`
- 数据与素材：`shared/`
- GitHub：`https://github.com/KQqin/shengjiang`

---

## WebSocket 协议（后端详表）

所有消息为 JSON：`{ "type": "...", ... }`

### 客户端 → 服务端

| type | 说明 |
|------|------|
| `CREATE_ROOM` | 教师创建房间 |
| `JOIN_ROOM` | `{ roomCode, nickname }` 学生加入 |
| `DRAW_ROLE` | 学生抽卡 |
| `NEXT_PHASE` / `PREV_PHASE` | 教师推进/回退环节 |
| `CAST_VOTE` | `{ optionId }` 学生投票（仅阶段 7） |
| `SHARE_CLUE` | `{ clueKey: "clue1" \| "clue2" }` 学生公开私人线索 |
| `DEV_*` | 开发者模式（需 `DEV_MODE=1`） |

### 服务端 → 客户端

| type | 说明 |
|------|------|
| `ROOM_CREATED` | 教师收到房间号 |
| `JOINED` | 加入成功，含 `playerId`、`isHost` |
| `ROOM_STATE` | 房间状态广播（含 `sharedClues`、`publicCluesReleased`） |
| `ROLE_DRAWN` | 抽卡结果 |
| `PLAYER_CONTENT` | 按阶段解锁的私人内容 |
| `ERROR` | 错误信息 |

### ROOM_STATE 主要字段

```json
{
  "code": "972371",
  "phaseIndex": 6,
  "players": [{ "id", "nickname", "roleName", "hasVoted" }],
  "votes": { "1": 0, "5": 8 },
  "publicCluesReleased": true,
  "sharedClues": [{ "id", "roleName", "title", "content", "clueKey" }]
}
```

### 核心逻辑（room.js）

1. `createRoom` — 教师连接创建房间  
2. `drawRole` — 随机分配未占用角色  
3. `nextPhase` — 推进环节并单播 `PLAYER_CONTENT`  
4. `shareClue` — 学生自愿公开线索，写入 `sharedClues` 并广播  
5. `castVote` — 阶段 7 收票汇总  

数据文件：`shared/script-data.json`（角色、阶段、公共线索、投票选项）

