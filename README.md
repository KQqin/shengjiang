# 胜疆 · 红色剧本杀后端说明

《苏区账目风波》联机剧本杀后端文档，供后端同学接入与扩展。

## 项目概述

- **模式**：教师大屏主持 + 12 名学生手机联机（共 13 连接）
- **讨论**：线下课堂口头进行，**不需要**讨论区后端
- **后端职责**：房间联机、角色抽卡、私人线索按阶段推送、投票汇总广播

## 技术栈

- Node.js
- Express（静态资源 + HTTP）
- ws（WebSocket 实时通信）
- 数据：`shared/script-data.json`（剧本、角色、线索、阶段）

## 快速启动

```bash
cd server
npm install
npm start
```

服务默认端口 **3001**：

| 地址 | 用途 |
|------|------|
| http://localhost:3001/client/host.html | 教师大屏 |
| http://localhost:3001/client/role.html | 学生手机 |
| ws://localhost:3001 | WebSocket |

课堂局域网：`http://教师电脑IP:3001/client/role.html`

## 目录结构

```
script-murder/
├── shared/
│   └── script-data.json    # 剧本数据（前后端共用，勿随意改字段名）
├── server/
│   ├── server.js           # HTTP 入口
│   ├── ws.js               # WebSocket 挂载
│   ├── ws-handler.js       # 消息路由
│   ├── room.js             # 房间 / 抽卡 / 线索 / 投票
│   └── messaging.js        # 消息发送工具
└── client/                 # 前端（另一同学维护，联调参考）
```

## 人数规则

| 类型 | 上限 |
|------|------|
| 总连接数 | 13（1 教师 + 12 学生） |
| 可抽卡玩家 | 12 |
| 教师 | 不抽卡、不投票 |

## 游戏阶段（phaseIndex 0–8）

| id | key | 名称 | 学生端解锁 |
|----|-----|------|-----------|
| 0 | lobby | 入场 | 抽卡 |
| 1 | incident | 风波起 | 公开身份 |
| 2 | intro | 自我介绍 | 公开身份 |
| 3 | inquiry1 | 第一轮问询 | + 秘密任务 |
| 4 | search1 | 搜证 I | + 私人线索 ① |
| 5 | discuss | 公开讨论 | （无新内容） |
| 6 | search2 | 搜证 II | + 私人线索 ②；大屏公共线索 |
| 7 | vote | 讨论 + 投票 | + 投票选项 |
| 8 | reveal | 揭晓 | + 真相 |

阶段由教师端发送 `NEXT_PHASE` / `PREV_PHASE` 推进。

## WebSocket 协议

所有消息为 JSON：`{ "type": "...", ... }`

### 客户端 → 服务端

#### CREATE_ROOM
教师打开大屏时自动发送。

```json
{ "type": "CREATE_ROOM" }
```

#### JOIN_ROOM
学生加入。

```json
{ "type": "JOIN_ROOM", "roomCode": "972371", "nickname": "张三" }
```

#### DRAW_ROLE
学生随机抽取未占用角色（仅 phase 0、且未抽过）。

```json
{ "type": "DRAW_ROLE" }
```

#### NEXT_PHASE / PREV_PHASE
仅教师（isHost）。

```json
{ "type": "NEXT_PHASE" }
```

#### CAST_VOTE
仅学生、仅阶段 7，可改票。

```json
{ "type": "CAST_VOTE", "optionId": 5 }
```

### 服务端 → 客户端

#### ROOM_CREATED（仅教师）

```json
{ "type": "ROOM_CREATED", "roomCode": "972371" }
```

#### JOINED

```json
{
  "type": "JOINED",
  "roomCode": "972371",
  "isHost": false,
  "playerId": "a1b2c3d4"
}
```

#### ROOM_STATE（广播全员）

```json
{
  "type": "ROOM_STATE",
  "room": {
    "code": "972371",
    "phaseIndex": 4,
    "phase": { "id": 4, "key": "search1", "name": "搜证 I", ... },
    "playerCount": 10,
    "maxPlayers": 12,
    "connectionCount": 11,
    "maxConnections": 13,
    "rolesRemaining": 2,
    "players": [
      {
        "id": "a1b2c3d4",
        "nickname": "张三",
        "isHost": false,
        "roleId": "su-xiaohe",
        "roleName": "苏小禾",
        "roleTitle": "青年记账员",
        "hasVoted": false,
        "voteOptionId": null
      }
    ],
    "votes": { "1": 0, "2": 1, "3": 0, "4": 0, "5": 8 },
    "voteTotal": 9,
    "votedCount": 9,
    "publicCluesReleased": false,
    "incident": { "title": "...", "body": "..." }
  }
}
```

#### ROLE_DRAWN（单播抽卡学生）

```json
{
  "type": "ROLE_DRAWN",
  "role": {
    "id": "su-xiaohe",
    "name": "苏小禾",
    "gender": "女",
    "title": "青年记账员",
    "tag": "入职三月新手、胆小怯懦、风波源头",
    "publicIntro": "..."
  }
}
```

#### PLAYER_CONTENT（单播，按阶段解锁）

```json
{
  "type": "PLAYER_CONTENT",
  "phaseIndex": 4,
  "content": {
    "unlocked": ["public", "secret", "clue1"],
    "public": { "name": "苏小禾", "title": "...", "publicIntro": "..." },
    "secret": { "relations": "...", "secretTask": "..." },
    "clue1": "私人线索①全文",
    "clue2": null,
    "voteOptions": null,
    "truth": null
  }
}
```

#### ERROR

```json
{ "type": "ERROR", "message": "房间已满（最多 13 人）" }
```

## 核心逻辑说明（room.js）

1. **createRoom**：首个 WebSocket 连接发 `CREATE_ROOM` 时创建房间，连接者为教师。
2. **drawRole**：从 `script-data.json` 的 `roles` 中随机选未占用角色。
3. **nextPhase**：phaseIndex++，向每位学生单播更新后的 `PLAYER_CONTENT`。
4. **castVote**：阶段 7 收票，自动减旧票加新票，广播 `ROOM_STATE`。
5. **leave**：断开时释放角色、回退该玩家票数。

## 投票选项

| optionId | 内容 | 是否正确 |
|----------|------|----------|
| 1 | 林大山监守自盗 | ✗ |
| 2 | 温秀宁、周明远合伙转移物资 | ✗ |
| 3 | 白区特务 / 外部破坏 | ✗ |
| 4 | 虚报采购、负责人舞弊 | ✗ |
| 5 | 苏小禾涂改账本引发连锁反应 + 三人互泼脏水，无实质性贪污 | ✓ |

## 前后端分工

| 前端（已实现） | 后端（本仓库） |
|---------------|---------------|
| host.html 大屏 UI、计时 | 房间创建、阶段广播 |
| role.html 加入、抽卡、投票 UI | 抽卡、线索单播、票型汇总 |
| ws-client.js 消息封装 | ws-handler + room 逻辑 |

**前端不依赖讨论接口**；大屏环节示意与计时为本地 UI，阶段切换需与后端 `phaseIndex` 同步。

## 课堂部署

1. 教师电脑运行 `npm start`
2. 确认防火墙放行 **3001** 端口
3. 学生手机连同一 WiFi，访问 `http://教师IP:3001/client/role.html?course=11`
4. 教师大屏显示房间号，学生输入后加入并抽卡

## 后续可扩展

- [ ] 二维码生成房间号
- [ ] 断线重连保留角色
- [ ] Redis 持久化房间（多机部署）
- [ ] 我的足迹 / 课堂报告存档

## 联调注意

- 必须通过 `npm start` 启动，不能直接双击 HTML（WebSocket 需要服务）
- 修改 `script-data.json` 后重启服务
- 接口字段变更需与前端同学同步 `ws-client.js` / `host.js` / `role.js`
