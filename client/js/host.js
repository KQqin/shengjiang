let scriptData = null;
let roomState = null;
let phaseIndex = 0;
let timerSec = 0;
let timerInterval = null;

async function init() {
  const res = await fetch('/shared/script-data.json');
  scriptData = await res.json();
  document.getElementById('script-title').textContent = scriptData.title;

  renderPhaseDots();
  renderPublicClues();
  renderTruth();
  renderVoteBars();

  WSClient.connect();
  WSClient.on('connected', () => {
    WSClient.send('CREATE_ROOM');
  });
  WSClient.on('ROOM_CREATED', (msg) => {
    document.getElementById('room-code').textContent = msg.roomCode;
  });
  WSClient.on('ROOM_STATE', (msg) => {
    roomState = msg.room;
    document.getElementById('room-code').textContent = roomState.code;
    document.getElementById('room-meta').textContent =
      `已连接 ${roomState.connectionCount}/${roomState.maxConnections} · 玩家 ${roomState.playerCount}/${roomState.maxPlayers} · 已抽卡 ${roomState.maxPlayers - roomState.rolesRemaining}/${roomState.maxPlayers}`;
    renderPlayerStrip();
    if (roomState.phaseIndex !== phaseIndex) {
      showPhase(roomState.phaseIndex);
    }
    updateVotes(roomState.votes, roomState.voteTotal, roomState.votedCount);
  });
  WSClient.on('ERROR', (msg) => {
    document.getElementById('room-meta').textContent = '⚠ ' + msg.message;
  });
}

function renderPhaseDots() {
  document.getElementById('phase-dots').innerHTML = scriptData.phases.map((p, i) =>
    `<div class="phase-dot" data-i="${i}" title="${p.name}"></div>`
  ).join('');
}

function renderPlayerStrip() {
  if (!roomState) return;
  const el = document.getElementById('player-strip');
  el.innerHTML = roomState.players
    .filter(p => !p.isHost)
    .map(p => {
      const status = p.roleName ? p.roleName : '未抽卡';
      const voted = p.hasVoted ? ' · 已投' : '';
      return `<span class="player-chip ${p.roleName ? 'has-role' : ''}">${p.nickname}：${status}${voted}</span>`;
    }).join('');
}

function showPhase(i) {
  phaseIndex = i;
  const phase = scriptData.phases[i];
  const dt = scriptData.displayTypes[phase.displayType] || { label: phase.name, icon: '•' };

  document.getElementById('visual').textContent = dt.icon;
  document.getElementById('visual').className = 'host-visual type-' + phase.displayType;
  document.getElementById('type-label').textContent = dt.label;
  document.getElementById('phase-name').textContent = `阶段 ${phase.id} · ${phase.name}`;
  document.getElementById('hint').textContent = phase.hostHint;

  const timerEl = document.getElementById('timer');
  timerEl.classList.toggle('hidden', !phase.showTimer);
  timerSec = phase.durationSec;
  updateTimerDisplay();
  stopTimer();
  document.getElementById('btn-timer').textContent = '开始计时';

  document.querySelectorAll('.phase-dot').forEach((d, idx) => {
    d.classList.toggle('active', idx === i);
    d.classList.toggle('done', idx < i);
  });

  if (phase.key === 'search2') openOverlay('overlay-clues');
  if (phase.key === 'vote') openOverlay('overlay-vote');
  if (phase.key === 'reveal') openOverlay('overlay-reveal');
}

function updateTimerDisplay() {
  const m = Math.floor(timerSec / 60);
  const s = timerSec % 60;
  document.getElementById('timer').textContent =
    String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
}

function startTimer() {
  stopTimer();
  timerInterval = setInterval(() => {
    if (timerSec > 0) { timerSec--; updateTimerDisplay(); }
    else stopTimer();
  }, 1000);
}

function stopTimer() {
  if (timerInterval) { clearInterval(timerInterval); timerInterval = null; }
}

function renderPublicClues() {
  document.getElementById('public-clues').innerHTML = scriptData.publicClues.map(c =>
    `<div class="clue-card"><h4>${c.title}</h4><p>${c.content}</p></div>`
  ).join('');
}

function renderVoteBars() {
  document.getElementById('vote-bars').innerHTML = scriptData.voteOptions.map(o =>
    `<div class="vote-row" data-id="${o.id}">
      <span class="label">${o.text}${o.correct ? ' ✓' : ''}</span>
      <div class="bar-wrap"><div class="bar" style="width:0%"></div></div>
      <span class="count">0</span>
    </div>`
  ).join('');
}

function updateVotes(votes, total, votedCount) {
  const max = roomState?.playerCount || 12;
  scriptData.voteOptions.forEach(o => {
    const count = votes[o.id] || 0;
    const row = document.querySelector(`.vote-row[data-id="${o.id}"]`);
    if (row) {
      row.querySelector('.count').textContent = count;
      row.querySelector('.bar').style.width = (count / max * 100) + '%';
    }
  });
  const el = document.getElementById('vote-progress');
  if (el) el.textContent = `（${votedCount}/${max} 人已投票，共 ${total} 票）`;
}

function renderTruth() {
  const t = scriptData.truth;
  document.getElementById('truth-summary').textContent = t.summary;
  document.getElementById('truth-timeline').innerHTML = t.timeline.map(item => `<li>${item}</li>`).join('');
  document.getElementById('truth-moral').textContent = t.moral;
}

function openOverlay(id) { document.getElementById(id).classList.add('open'); }
function closeOverlay(id) { document.getElementById(id).classList.remove('open'); }

document.getElementById('btn-prev').onclick = () => WSClient.send('PREV_PHASE');
document.getElementById('btn-next').onclick = () => WSClient.send('NEXT_PHASE');
document.getElementById('btn-timer').onclick = () => {
  if (timerInterval) { stopTimer(); document.getElementById('btn-timer').textContent = '开始计时'; }
  else { startTimer(); document.getElementById('btn-timer').textContent = '暂停'; }
};
document.getElementById('btn-reset-timer').onclick = () => {
  stopTimer();
  timerSec = scriptData.phases[phaseIndex].durationSec;
  updateTimerDisplay();
  document.getElementById('btn-timer').textContent = '开始计时';
};
document.getElementById('btn-fullscreen').onclick = () => {
  if (!document.fullscreenElement) document.documentElement.requestFullscreen();
  else document.exitFullscreen();
};

init();
