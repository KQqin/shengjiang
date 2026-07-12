# 数智红途 · 前端（uni-app + Vue 3）

本目录为《苏区账目风波》剧本杀及智学课堂的 **uni-app H5 前端**，供后端同学联调与后续扩展。

> 后端仓库同级的 `server/`、`shared/` 为 Node.js WebSocket 服务与剧本数据。  
> 旧版静态页 `client/` 已逐步废弃，请以本目录为准。

---

## 技术栈

| 项 | 说明 |
|----|------|
| 框架 | uni-app 3.x + Vue 3 Composition API（`<script setup>`） |
| 构建 | Vite 5 + `@uni-helper/unh` |
| 样式 | Sass，`rpx` 适配手机 |
| 字体 | Noto Sans SC、PingFang SC（见 `src/styles/fonts.scss`） |
| 实时通信 | `src/utils/ws-client.js` |

---

## 目录结构

```
frontend/
├── src/
│   ├── pages/
│   │   ├── index.vue           # 智学课堂首页（轮播、排行榜、瀑布流）
│   │   ├── classroom.vue       # 课件播放页（时间线、章节、游戏入口）
│   │   ├── script-host.vue     # 教师大屏（房间号、阶段、投票汇总、开发者工具）
│   │   ├── script-role.vue     # 学生端（抽卡、人物卡、剧本书、线索卡池）
│   │   └── script-dev.vue      # 角色预览（无需联机，调试用）
│   ├── utils/
│   │   ├── config.js           # API / WebSocket / shared 资源地址
│   │   ├── ws-client.js        # WebSocket 封装
│   │   └── script-content.js   # 与后端 room.js 一致的环节解锁逻辑
│   ├── data/
│   │   ├── courses.js          # 课程列表
│   │   └── course-content.js   # 课件章节内容
│   ├── styles/                 # 首页、课件页全局样式
│   └── pages.json              # 路由与导航栏配置
├── .env.development            # 本地：VITE_WS_URL=ws://localhost:3001
├── .env.production             # 生产：可配置 VITE_API_BASE / VITE_WS_URL
├── vite.config.js              # 开发代理 /shared → 3001
└── package.json
```

---

## 本地开发（前后端联调）

需要 **两个终端**：

**终端 1 — 后端（必须先启动）**

```bash
cd server
npm install
# 开发者模式（虚拟玩家、填充房间等）
set DEV_MODE=1    # Windows
npm start
# → http://localhost:3001
```

**终端 2 — 前端**

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

| 地址 | 用途 |
|------|------|
| http://localhost:5173 | uni-app H5 开发服 |
| ws://localhost:3001 | WebSocket |
| http://localhost:3001/shared/script-data.json | 剧本 JSON（Vite 已代理 `/shared`） |

### 学生端免联机预览

```
http://localhost:5173/#/pages/script-role?preview=1&role=5&phase=6
```

| 参数 | 含义 |
|------|------|
| `preview=1` | 跳过加入房间/抽卡 |
| `role=0~11` | 角色序号（5=赵启山） |
| `phase=0~8` | 游戏环节（6=搜证 II，公共线索已出） |

---

## 页面与功能说明

### 1. 智学课堂（index / classroom）

- 自 `homepage-mockup/` 1:1 迁移的首页与课件页
- 课程 11 入口可跳转剧本杀教师端/学生端

### 2. 教师大屏 `script-host.vue`

- 自动 `CREATE_ROOM`，显示 6 位房间号
- `NEXT_PHASE` / `PREV_PHASE` 推进环节
- 投票汇总、公共线索弹层、真相揭晓
- 开发者工具栏（仅 `import.meta.env.DEV`）：填充 11 虚拟玩家、全员抽卡、随机投票等

### 3. 学生端 `script-role.vue`（重点）

**流程：** 加入房间 → 抽卡 → 人物卡 → 主界面

**主界面布局：**

- 左右：玩家头像列
- 中央羊皮纸：**公开卡池**（公共线索 + 玩家推送线索）
- 底部导航：人物 / 剧本 / 线索 / 投票 / 更多

**人物按钮：** 长方形人物卡（海报占位 + 姓名 + 性格）

**剧本按钮：** 摊开双页书（左页公开身份/背景，右页秘密任务）

**线索按钮：** 私人线索卡片网格，每张卡下方有 **「推送到公开卡池」**

**公开卡池：**

- 公共线索：苏区文书风卡片（印章、分类、主题色），点击可居中放大
- 玩家公开：学生自愿 `SHARE_CLUE` 后的线索

### 4. 角色预览 `script-dev.vue`

- 无需 WebSocket，按角色/环节预览解锁内容

---

## 前端已使用的 WebSocket 消息

除 `README.md`（后端根目录）已列协议外，前端还依赖：

### 客户端 → 服务端

| type | 发送方 | 说明 |
|------|--------|------|
| `SHARE_CLUE` | 学生 | `{ clueKey: "clue1" \| "clue2" }` 将私人线索推到公开卡池 |

### 服务端 → 客户端（ROOM_STATE 扩展字段）

```json
{
  "room": {
    "sharedClues": [
      {
        "id": "playerId:clue1",
        "playerId": "...",
        "roleName": "赵启山",
        "title": "赵启山 · 私人线索 ①",
        "content": "线索正文",
        "clueKey": "clue1",
        "sharedAt": 1710000000000
      }
    ],
    "publicCluesReleased": true
  }
}
```

`publicCluesReleased` 在 `phaseIndex >= 6` 时为 `true`，前端才渲染 `script-data.json` 中的 `publicClues`。

---

## 素材存储约定（待后端/运营上传）

图片、PDF **不要**打进前端包，统一放后端静态目录：

```
shared/
├── script-data.json
└── assets/suqu-account-dispute/
    ├── public-clues/          # P1.jpg ~ P4.jpg
    └── roles/
        └── {role-id}/
            ├── poster.jpg     # 人物海报
            ├── clue-1.jpg     # 私人线索①图
            ├── clue-2.jpg
            └── script.pdf     # 个人剧本
```

`script-data.json` 中增加路径字段，前端通过 `getSharedUrl()` 加载：

```js
// utils/config.js
getSharedUrl('assets/suqu-account-dispute/roles/zhao-qishan/poster.jpg')
// → /shared/assets/...（由 server.js 静态托管）
```

当前 UI 已留占位区，接入时改 `script-role.vue` 中 poster / 线索图 / 剧本区即可。

---

## 后端待办（交给后端同学）

- [ ] 确认 `SHARE_CLUE` 与 `sharedClues` 广播已实现（见 `server/room.js`）
- [ ] `shared/script-data.json` 为唯一数据源，改字段需同步 `frontend/src/utils/script-content.js`
- [ ] 素材目录 `shared/assets/` 与 JSON 路径字段
- [ ] 生产部署：`npm run build` 后由 `server.js` 托管 `frontend/dist/build/h5`
- [ ] 可选：断线重连保留角色、房间持久化、教师素材上传接口

---

## 云部署

```bash
cd frontend && npm install && npm run build
cd ../server && npm install && NODE_ENV=production npm start
```

访问 `http://服务器:3001/` 即为 H5 前端（`server.js` 自动托管构建产物）。

前后端分离时，配置 `frontend/.env.production`：

```env
VITE_API_BASE=https://api.example.com
VITE_WS_URL=wss://api.example.com
```

---

## 联系方式与联调注意

1. 必须先 `npm start` 后端，再开前端；否则教师端无房间号、学生端 WebSocket 失败
2. 修改 `shared/script-data.json` 后 **重启后端**
3. 课堂局域网：学生手机访问 `http://教师IP:3001`（生产构建）或 `http://教师IP:5173`（开发）
4. 旧版 `client/host.html`、`client/role.html` 不再维护，联调以本前端为准
