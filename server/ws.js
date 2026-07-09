const fs = require('fs');
const path = require('path');
const { WebSocketServer } = require('ws');
const { RoomManager } = require('./room');
const { handleMessage } = require('./ws-handler');
const { send } = require('./messaging');

const scriptData = JSON.parse(
  fs.readFileSync(path.join(__dirname, '../shared/script-data.json'), 'utf8')
);

const MAX_PLAYERS = scriptData.maxPlayers || 12;
const MAX_CONNECTIONS = scriptData.maxConnections || 13;

function attachWebSocket(server) {
  const wss = new WebSocketServer({ server });
  const rooms = new RoomManager(scriptData, MAX_PLAYERS, MAX_CONNECTIONS);

  wss.on('connection', (ws) => {
    ws.isAlive = true;
    ws.on('pong', () => { ws.isAlive = true; });

    ws.on('message', (raw) => {
      let msg;
      try {
        msg = JSON.parse(raw.toString());
      } catch {
        send(ws, { type: 'ERROR', message: '无效 JSON' });
        return;
      }
      handleMessage(ws, msg, rooms, scriptData);
    });

    ws.on('close', () => {
      rooms.leave(ws);
    });
  });

  const interval = setInterval(() => {
    wss.clients.forEach((ws) => {
      if (!ws.isAlive) return ws.terminate();
      ws.isAlive = false;
      ws.ping();
    });
  }, 30000);

  wss.on('close', () => clearInterval(interval));
}

module.exports = { attachWebSocket };
