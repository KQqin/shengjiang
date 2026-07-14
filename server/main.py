"""数智红途 · Python 后端入口。"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from api.websocket import handle_message
from config import DEV_MODE, FRONTEND_H5_DIR, HOST, PORT, SHARED_DIR
from services.room_manager import RoomManager
from services.script_loader import load_script_data

room_manager: RoomManager | None = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global room_manager
    script_data = load_script_data()
    room_manager = RoomManager(script_data)
    yield


app = FastAPI(title="数智红途 API", version="0.2.0", lifespan=lifespan)

if SHARED_DIR.is_dir():
    app.mount("/shared", StaticFiles(directory=str(SHARED_DIR)), name="shared")

if (FRONTEND_H5_DIR / "index.html").is_file():
    app.mount("/", StaticFiles(directory=str(FRONTEND_H5_DIR), html=True), name="h5")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "backend": "python",
        "devMode": DEV_MODE,
        "ws": "ready",
    }


@app.websocket("/")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    assert room_manager is not None
    try:
        while True:
            raw = await ws.receive_text()
            await handle_message(ws, raw, room_manager)
    except WebSocketDisconnect:
        await room_manager.disconnect(ws)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
