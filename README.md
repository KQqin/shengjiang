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
| 实时 | WebSocket（Python 后端已实现） |

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
| ws://localhost:3001 | WebSocket 联机 |
| http://localhost:3001/shared/script-data.json | 剧本 JSON |

**生产（阿里云 / 单服托管，推荐）**

```bash
cd frontend && npm install && npm run build
cd ../server && pip install -r requirements.txt
export DEV_MODE=0
uvicorn main:app --host 0.0.0.0 --port 3001 --workers 1
```

构建产物在 `frontend/dist/build/h5`，Python 后端会自动托管（见 `server/main.py`）。

**生产环境变量**

| 变量 | 值 | 说明 |
|------|-----|------|
| `DEV_MODE` | `0` | 必须关闭，禁用虚拟玩家等开发工具 |
| `HOST` | `0.0.0.0` | 监听所有网卡 |
| `PORT` | `3001` | 默认端口 |

**对外访问链接（部署后发给师生）**

| 角色 | URL |
|------|-----|
| 学生加入 | `https://你的域名/#/pages/script-role?course=11` |
| 教师大屏 | `https://你的域名/#/pages/script-host?course=11` |

无需同一 WiFi，有网即可；教师页自动创建房间，学生输入 **6 位房间号** 加入。

**Nginx + HTTPS**：反向代理到 `127.0.0.1:3001`，须配置 WebSocket 升级（`Upgrade` / `Connection` 头）。详见 [`server/README.md`](./server/README.md)。

同域部署时 `frontend/.env.production` 留空即可；前后端分离时再配置 `VITE_API_BASE` / `VITE_WS_URL`。

---

## 分工

| 模块 | 目录 | 负责人 | 状态 |
|------|------|--------|------|
| 智学课堂 / 课件 / 剧本杀 UI | `frontend/` | 前端 | ✅ 已完成 |
| Python API + WebSocket | `server/` | 后端 | ✅ MVP 已完成 |
| 剧本与素材数据 | `shared/` | 共用 | ✅ JSON 已有 |

**后端同学请阅读 [`server/README.md`](./server/README.md)** 与 [`frontend/README.md`](./frontend/README.md)（前端协议约定，勿改前端代码）。

---

## 仓库

https://github.com/KQqin/shengjiang
