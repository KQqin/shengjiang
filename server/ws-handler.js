const { send } = require('./messaging');

const isDevMode = process.env.NODE_ENV !== 'production' || process.env.DEV_MODE === '1';

function handleMessage(ws, msg, rooms, scriptData) {
  switch (msg.type) {
    case 'CREATE_ROOM': {
      const room = rooms.createRoom(ws);
      send(ws, { type: 'ROOM_CREATED', roomCode: room.code });
      rooms.broadcastRoom(room);
      break;
    }
    case 'JOIN_ROOM': {
      const result = rooms.joinRoom(ws, String(msg.roomCode || '').trim(), msg.nickname);
      if (result.error) {
        send(ws, { type: 'ERROR', message: result.error });
        return;
      }
      const member = rooms.getMember(result.room, ws);
      send(ws, {
        type: 'JOINED',
        roomCode: result.room.code,
        isHost: member.isHost,
        playerId: member.id,
      });
      if (member.roleId) rooms.sendPlayerContent(result.room, ws);
      rooms.broadcastRoom(result.room);
      break;
    }
    case 'DRAW_ROLE': {
      const room = rooms.getRoom(ws);
      if (!room) return send(ws, { type: 'ERROR', message: '未加入房间' });
      const result = rooms.drawRole(room, ws);
      if (result.error) send(ws, { type: 'ERROR', message: result.error });
      break;
    }
    case 'NEXT_PHASE': {
      const room = rooms.getRoom(ws);
      if (!room) return send(ws, { type: 'ERROR', message: '未加入房间' });
      const result = rooms.nextPhase(room, ws);
      if (result.error) send(ws, { type: 'ERROR', message: result.error });
      break;
    }
    case 'PREV_PHASE': {
      const room = rooms.getRoom(ws);
      if (!room) return send(ws, { type: 'ERROR', message: '未加入房间' });
      const result = rooms.prevPhase(room, ws);
      if (result.error) send(ws, { type: 'ERROR', message: result.error });
      break;
    }
    case 'CAST_VOTE': {
      const room = rooms.getRoom(ws);
      if (!room) return send(ws, { type: 'ERROR', message: '未加入房间' });
      const result = rooms.castVote(room, ws, msg.optionId);
      if (result.error) send(ws, { type: 'ERROR', message: result.error });
      break;
    }
    case 'SHARE_CLUE': {
      const room = rooms.getRoom(ws);
      if (!room) return send(ws, { type: 'ERROR', message: '未加入房间' });
      const result = rooms.shareClue(room, ws, msg.clueKey);
      if (result.error) send(ws, { type: 'ERROR', message: result.error });
      break;
    }
    case 'PING':
      send(ws, { type: 'PONG' });
      break;
    case 'DEV_FILL_PLAYERS':
    case 'DEV_DRAW_ALL':
    case 'DEV_AUTO_VOTE':
    case 'DEV_CLEAR_BOTS': {
      if (!isDevMode) {
        send(ws, { type: 'ERROR', message: '开发者模式未启用' });
        break;
      }
      const room = rooms.getRoom(ws);
      if (!room) return send(ws, { type: 'ERROR', message: '未加入房间' });
      let result;
      if (msg.type === 'DEV_FILL_PLAYERS') {
        result = rooms.devFillPlayers(room, ws, msg.count || 12);
      } else if (msg.type === 'DEV_DRAW_ALL') {
        result = rooms.devDrawAll(room, ws);
      } else if (msg.type === 'DEV_AUTO_VOTE') {
        result = rooms.devAutoVote(room, ws);
      } else {
        result = rooms.devClearBots(room, ws);
      }
      if (result.error) send(ws, { type: 'ERROR', message: result.error });
      else send(ws, { type: 'DEV_OK', action: msg.type, ...result });
      break;
    }
    default:
      send(ws, { type: 'ERROR', message: '未知消息类型: ' + msg.type });
  }
}

module.exports = { handleMessage };
