let playerContent = null;
let roomState = null;
let currentTab = 'public';
let joined = false;
let hasRole = false;

function $(id) { return document.getElementById(id); }

WSClient.connect();

WSClient.on('connected', () => {
  $('status-line').textContent = '已连接服务器，请输入房间号';
});

WSClient.on('JOINED', (msg) => {
  joined = true;
  $('join-panel').classList.add('hidden');
  $('status-line').textContent = `已加入房间 ${msg.roomCode}`;

  if (msg.isHost) {
    $('status-line').textContent = '你是教师，请使用教师大屏页面';
    return;
  }
  $('draw-panel').classList.remove('hidden');
});

WSClient.on('ROLE_DRAWN', (msg) => {
  hasRole = true;
  $('draw-panel').classList.add('hidden');
  $('role-reveal').classList.remove('hidden');
  $('tabs').classList.remove('hidden');
  $('content').classList.remove('hidden');

  const r = msg.role;
  $('reveal-name').textContent = r.name;
  $('reveal-meta').textContent = `${r.gender} · ${r.title}`;
  $('reveal-tag').textContent = r.tag;
  $('status-line').textContent = `你是：${r.name}`;
});

WSClient.on('PLAYER_CONTENT', (msg) => {
  playerContent = msg.content;
  updateTabs();
  renderContent();
});

WSClient.on('ROOM_STATE', (msg) => {
  roomState = msg.room;
  if ($('roles-left')) {
    $('roles-left').textContent = roomState.rolesRemaining;
  }
  if (joined && !hasRole && roomState.phaseIndex > 0) {
    $('draw-panel').classList.add('hidden');
    $('status-line').textContent = '游戏已开始，未能抽卡';
  }
});

WSClient.on('ERROR', (msg) => {
  $('status-line').textContent = '⚠ ' + msg.message;
});

$('btn-join').onclick = () => {
  const code = $('room-code').value.trim();
  const nickname = $('nickname').value.trim() || '玩家';
  if (code.length !== 6) {
    $('status-line').textContent = '请输入 6 位房间号';
    return;
  }
  WSClient.send('JOIN_ROOM', { roomCode: code, nickname });
};

$('btn-draw').onclick = () => {
  WSClient.send('DRAW_ROLE');
};

document.querySelectorAll('.role-tab').forEach(tab => {
  tab.onclick = () => {
    if (tab.classList.contains('locked')) return;
    currentTab = tab.dataset.tab;
    document.querySelectorAll('.role-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    renderContent();
  };
});

function updateTabs() {
  if (!playerContent) return;
  const u = playerContent.unlocked || [];
  document.querySelectorAll('.role-tab').forEach(tab => {
    const key = tab.dataset.tab;
    const locked = !u.includes(key);
    tab.classList.toggle('locked', locked);
    tab.style.opacity = locked ? '0.35' : '1';
  });
}

function renderContent() {
  const el = $('content');
  if (!playerContent) {
    el.innerHTML = '<p style="color:var(--muted)">等待教师推进环节…</p>';
    return;
  }

  const u = playerContent.unlocked || [];

  if (currentTab === 'public' && u.includes('public')) {
    const r = playerContent.public;
    el.innerHTML = `
      <h2>${r.name}</h2>
      <p class="meta">${r.gender} · ${r.title}</p>
      <span class="tag">${r.tag}</span>
      <p><strong>公开介绍：</strong>${r.publicIntro}</p>`;
  } else if (currentTab === 'secret' && u.includes('secret')) {
    el.innerHTML = `
      <h2>秘密任务</h2>
      <p><strong>人物关系：</strong>${playerContent.secret.relations}</p>
      <p><strong>你的任务：</strong>${playerContent.secret.secretTask}</p>`;
  } else if (currentTab === 'clue1' && u.includes('clue1')) {
    el.innerHTML = `<h2>私人线索 ①</h2><p>${playerContent.clue1}</p>`;
  } else if (currentTab === 'clue2' && u.includes('clue2')) {
    el.innerHTML = `<h2>私人线索 ②</h2><p>${playerContent.clue2}</p>`;
  } else if (currentTab === 'vote' && u.includes('vote')) {
    el.innerHTML = '<h2>选择答案</h2>' + playerContent.voteOptions.map(o =>
      `<button type="button" class="vote-option-btn" data-id="${o.id}">${o.text}</button>`
    ).join('');
    el.querySelectorAll('.vote-option-btn').forEach(btn => {
      btn.onclick = () => {
        WSClient.send('CAST_VOTE', { optionId: Number(btn.dataset.id) });
        el.querySelectorAll('.vote-option-btn').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
      };
    });
  } else if (currentTab === 'reveal' && u.includes('reveal')) {
    const t = playerContent.truth;
    el.innerHTML = `
      <h2>真相揭晓</h2>
      <p>${t.summary}</p>
      <ul style="margin-top:12px;padding-left:0;list-style:none">
        ${t.timeline.map(i => `<li style="padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.08)">${i}</li>`).join('')}
      </ul>
      <p style="margin-top:16px;color:var(--gold)">${t.moral}</p>`;
  } else {
    el.innerHTML = '<p style="color:var(--muted)">🔒 该内容尚未解锁，请等待教师推进环节</p>';
  }
}
