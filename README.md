# 胜jiang · 数智红途《苏区账目风波》

红色剧本杀联机项目：**1 教师大屏 + 12 学生手机**，服务于课程 11《革命年代青年榜样故事》。

```
shengjiang/
├── frontend/          # uni-app H5 前端（智学课堂 + 剧本杀）← 勿改，详见 frontend/README.md
├── server/            # Python FastAPI 后端（正式开发）
├── shared/            # 剧本数据 script-data.json + 素材 assets/
└── client/            # 旧版静态 HTML（已废弃，仅作参考）
```

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | uni-app 3.x + Vue 3 + Vite 5 |
| 后端 | **Python 3 + FastAPI + uvicorn** |
| 数据 | JSON 文件（`shared/`），MVP 无数据库 |
| 实时 | WebSocket（待 Python 后端实现） |

> 原 Node.js 测试后端已移除，不再维护。

---

## 快速启动

**后端（Python）**

```bash
cd server
pip install -r requirements.txt
python main.py
```

**前端（开发）**

```bash
cd frontend
npm install
npm run dev
```

| 地址 | 用途 |
|------|------|
| http://localhost:5173 | uni-app H5 开发服 |
| http://localhost:3001 | Python 后端 |
| ws://localhost:3001 | WebSocket（联机功能开发中） |
| http://localhost:3001/shared/script-data.json | 剧本 JSON |

**生产（单服托管，后端 WS 完成后）**

```bash
cd frontend && npm run build
cd ../server && python main.py
```

---

## 分工

| 模块 | 目录 | 负责人 | 状态 |
|------|------|--------|------|
| 智学课堂 / 课件 / 剧本杀 UI | `frontend/` | 前端 | ✅ 已完成 |
| Python API + WebSocket | `server/` | 后端 | ⏳ 开发中 |
| 剧本与素材数据 | `shared/` | 共用 | ✅ JSON 已有 |

**后端同学请阅读 [`server/README.md`](./server/README.md)** 与 [`frontend/README.md`](./frontend/README.md)（前端协议约定，勿改前端代码）。

---

## 仓库

https://github.com/KQqin/shengjiang
