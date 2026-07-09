const { randomBytes } = require('crypto');
const { send } = require('./messaging');

class RoomManager {
  constructor(scriptData, maxPlayers, maxConnections) {
    this.scriptData = scriptData;
    this.maxPlayers = maxPlayers;
    this.maxConnections = maxConnections;
    this.rooms = new Map();
    this.wsRoom = new Map();
  }

  createCode() {
    let code;
    do {
      code = String(Math.floor(100000 + Math.random() * 900000));
    } while (this.rooms.has(code));
    return code;
  }

  createRoom(ws) {
    const code = this.createCode();
    const room = {
      code,
      phaseIndex: 0,
      hostWs: ws,
      members: new Map(),
      votes: {},
      rolesTaken: new Set(),
    };
    this.scriptData.voteOptions.forEach((o) => { room.votes[o.id] = 0; });
    this.rooms.set(code, room);
    this._addMember(room, ws, { isHost: true, nickname: '教师' });
    return room;
  }

  joinRoom(ws, code, nickname) {
    const room = this.rooms.get(code);
    if (!room) return { error: '房间不存在' };
    if (room.members.size >= this.maxConnections) return { error: '房间已满（最多 13 人）' };
    if (room.members.has(ws)) return { room };

    const playerCount = [...room.members.values()].filter((m) => !m.isHost).length;
    if (playerCount >= this.maxPlayers) return { error: '玩家已满（12 个角色）' };

    this._addMember(room, ws, { isHost: false, nickname: nickname || '玩家' });
    return { room };
  }

  _addMember(room, ws, { isHost, nickname }) {
    const id = randomBytes(4).toString('hex');
    const member = {
      id,
      ws,
      nickname,
      isHost,
      roleId: null,
      voteOptionId: null,
    };
    room.members.set(ws, member);
    this.wsRoom.set(ws, room.code);
  }

  getRoom(ws) {
    const code = this.wsRoom.get(ws);
    return code ? this.rooms.get(code) : null;
  }

  getMember(room, ws) {
    return room.members.get(ws);
  }

  leave(ws) {
    const room = this.getRoom(ws);
    if (!room) return;

    const member = room.members.get(ws);
    room.members.delete(ws);
    this.wsRoom.delete(ws);

    if (member?.roleId) {
      room.rolesTaken.delete(member.roleId);
    }
    if (member?.voteOptionId) {
      room.votes[member.voteOptionId] = Math.max(0, (room.votes[member.voteOptionId] || 0) - 1);
    }

    if (room.hostWs === ws) {
      if (room.members.size === 0) {
        this.rooms.delete(room.code);
        return;
      }
      const next = [...room.members.values()].find((m) => m.isHost) ||
        [...room.members.values()][0];
      if (next) {
        next.isHost = true;
        room.hostWs = next.ws;
      }
    }

    this.broadcastRoom(room);
  }

  drawRole(room, ws) {
    const member = room.members.get(ws);
    if (!member || member.isHost) return { error: '教师不能抽取角色' };
    if (member.roleId) return { error: '你已经拥有角色' };
    if (room.phaseIndex > 0) return { error: '游戏已开始，不能抽卡' };

    const available = this.scriptData.roles.filter((r) => !room.rolesTaken.has(r.id));
    if (!available.length) return { error: '角色已被抽完' };

    const picked = available[Math.floor(Math.random() * available.length)];
    member.roleId = picked.id;
    room.rolesTaken.add(picked.id);

    send(ws, { type: 'ROLE_DRAWN', role: this._publicRole(picked) });
    this.sendPlayerContent(room, ws);
    this.broadcastRoom(room);
    return { ok: true };
  }

  nextPhase(room, ws) {
    const member = room.members.get(ws);
    if (!member?.isHost) return { error: '仅教师可操作' };

    if (room.phaseIndex < this.scriptData.phases.length - 1) {
      room.phaseIndex++;
    }
    this.broadcastRoom(room);
    room.members.forEach((_, memberWs) => {
      if (!room.members.get(memberWs).isHost) {
        this.sendPlayerContent(room, memberWs);
      }
    });
    return { ok: true };
  }

  prevPhase(room, ws) {
    const member = room.members.get(ws);
    if (!member?.isHost) return { error: '仅教师可操作' };
    if (room.phaseIndex > 0) room.phaseIndex--;
    this.broadcastRoom(room);
    room.members.forEach((_, memberWs) => {
      if (!room.members.get(memberWs).isHost) {
        this.sendPlayerContent(room, memberWs);
      }
    });
    return { ok: true };
  }

  castVote(room, ws, optionId) {
    const member = room.members.get(ws);
    if (!member || member.isHost) return { error: '教师不能投票' };
    if (room.phaseIndex !== 7) return { error: '当前不是投票阶段' };

    const valid = this.scriptData.voteOptions.some((o) => o.id === optionId);
    if (!valid) return { error: '无效选项' };

    if (member.voteOptionId) {
      room.votes[member.voteOptionId] = Math.max(0, room.votes[member.voteOptionId] - 1);
    }
    member.voteOptionId = optionId;
    room.votes[optionId] = (room.votes[optionId] || 0) + 1;

    this.broadcastRoom(room);
    return { ok: true };
  }

  _unlockedSections(phaseIndex) {
    const sections = ['public'];
    if (phaseIndex >= 3) sections.push('secret');
    if (phaseIndex >= 4) sections.push('clue1');
    if (phaseIndex >= 6) sections.push('clue2');
    if (phaseIndex >= 7) sections.push('vote');
    if (phaseIndex >= 8) sections.push('reveal');
    return sections;
  }

  _publicRole(role) {
    return {
      id: role.id,
      name: role.name,
      gender: role.gender,
      title: role.title,
      tag: role.tag,
      publicIntro: role.publicIntro,
    };
  }

  sendPlayerContent(room, ws) {
    const member = room.members.get(ws);
    if (!member || member.isHost || !member.roleId) return;

    const role = this.scriptData.roles.find((r) => r.id === member.roleId);
    const unlocked = this._unlockedSections(room.phaseIndex);
    const content = { unlocked };

    if (unlocked.includes('public')) {
      content.public = this._publicRole(role);
    }
    if (unlocked.includes('secret')) {
      content.secret = {
        relations: role.relations,
        secretTask: role.secretTask,
      };
    }
    if (unlocked.includes('clue1')) {
      content.clue1 = role.privateClues[0];
    }
    if (unlocked.includes('clue2')) {
      content.clue2 = role.privateClues[1];
    }
    if (unlocked.includes('vote')) {
      content.voteOptions = this.scriptData.voteOptions.map(({ id, text }) => ({ id, text }));
    }
    if (unlocked.includes('reveal')) {
      content.truth = this.scriptData.truth;
    }

    send(ws, { type: 'PLAYER_CONTENT', content, phaseIndex: room.phaseIndex });
  }

  serializeRoom(room) {
    const phase = this.scriptData.phases[room.phaseIndex];
    const players = [...room.members.values()].map((m) => {
      const role = m.roleId
        ? this.scriptData.roles.find((r) => r.id === m.roleId)
        : null;
      return {
        id: m.id,
        nickname: m.nickname,
        isHost: m.isHost,
        roleId: m.roleId,
        roleName: role?.name || null,
        roleTitle: role?.title || null,
        hasVoted: !!m.voteOptionId,
        voteOptionId: m.voteOptionId,
      };
    });

    const studentCount = players.filter((p) => !p.isHost).length;
    const votedCount = players.filter((p) => !p.isHost && p.hasVoted).length;

    return {
      code: room.code,
      phaseIndex: room.phaseIndex,
      phase,
      playerCount: studentCount,
      maxPlayers: this.maxPlayers,
      connectionCount: room.members.size,
      maxConnections: this.maxConnections,
      players,
      votes: { ...room.votes },
      voteTotal: Object.values(room.votes).reduce((a, b) => a + b, 0),
      votedCount,
      rolesRemaining: this.scriptData.roles.length - room.rolesTaken.size,
      publicCluesReleased: room.phaseIndex >= 6,
      incident: room.phaseIndex >= 1 ? this.scriptData.incident : null,
    };
  }

  broadcastRoom(room) {
    const state = this.serializeRoom(room);
    room.members.forEach((member) => {
      send(member.ws, { type: 'ROOM_STATE', room: state });
    });
  }
}

module.exports = { RoomManager };
