<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { onLoad, onShow, onHide } from '@dcloudio/uni-app'
import * as ws from '@/utils/ws-client'
import { getSharedUrl, getHealthUrl } from '@/utils/config'
import {
  clearAllHostSessions,
  clearHostLobbySession,
  clearHostSession,
  isRejoinRecoverableError,
  loadHostLobbySession,
  loadHostSession,
  saveHostLobbySession,
  saveHostSession,
  syncServerBootSession,
} from '@/utils/script-session'

const courseId = ref('11')
const scriptData = ref(null)
const roomState = ref(null)
const roomCode = ref('——')
const phaseIndex = ref(0)
const gameStarted = ref(false)
const timerSec = ref(0)
const timerRunning = ref(false)
const showClues = ref(false)
const showVote = ref(false)
const showReveal = ref(false)
const connStatus = ref('connecting') // connecting | connected | error
const statusMessage = ref('')
let timerInterval = null
let pendingHostRejoin = false
/** 当前页面内存会话，用于同页网络闪断重连 */
let hostVisitSession = null
let leavingIntentionally = false
let wsHandlersBound = false
let roomBootstrapTimer = null

const phase = computed(() => scriptData.value?.phases?.[phaseIndex.value])
const displayType = computed(() => {
  if (!phase.value || !scriptData.value) return { label: '', icon: '•' }
  return scriptData.value.displayTypes[phase.value.displayType] || { label: phase.value.name, icon: '•' }
})

const roomMeta = computed(() => {
  if (statusMessage.value) return statusMessage.value
  if (connStatus.value === 'error') {
    return '后端未连接 · 请先启动 server（python main.py）'
  }
  if (connStatus.value === 'connecting') return '正在连接后端…'
  if (!roomState.value) return 'WebSocket 已连接，正在创建房间…'
  const r = roomState.value
  return `已连接 ${r.connectionCount}/${r.maxConnections} · 玩家 ${r.playerCount}/${r.maxPlayers} · 已抽卡 ${r.maxPlayers - r.rolesRemaining}/${r.maxPlayers}`
})

const playerChips = computed(() => {
  if (!roomState.value) return []
  return roomState.value.players
    .filter((p) => !p.isHost)
    .map((p) => ({
      text: `${p.connected === false ? '💤 ' : ''}${p.isBot ? '补位 ' : ''}${p.nickname}：${p.roleName || '未抽卡'}${p.hasVoted ? ' · 已答' : ''}`,
      hasRole: !!p.roleName,
    }))
})

const voteSubmissions = computed(() => roomState.value?.voteSubmissions || [])

const inspectorRoleIds = computed(() => {
  const roles = scriptData.value?.roles || []
  return new Set(roles.filter((r) => r.group === 'inspector').map((r) => r.id))
})

const CULPRIT_SEP_RE = /[,，、；;|/\n\r\s]+|和|与|及|还有/g

function matchCulpritsToRoles(culprit = '') {
  const text = String(culprit || '').trim()
  if (!text) return []
  const roles = scriptData.value?.roles || []
  const matchedIds = new Set()
  const matched = []

  for (const role of [...roles].sort((a, b) => b.name.length - a.name.length)) {
    if (role.name && text.includes(role.name) && !matchedIds.has(role.id)) {
      matched.push(role)
      matchedIds.add(role.id)
    }
  }

  for (const part of text.split(CULPRIT_SEP_RE)) {
    const seg = part.trim()
    if (!seg) continue
    for (const role of roles) {
      if (seg === role.name && !matchedIds.has(role.id)) {
        matched.push(role)
        matchedIds.add(role.id)
      }
    }
  }

  return matched
}

function buildVoteTallyFromPlayers(players = []) {
  const counts = new Map()
  let totalWeight = 0
  for (const player of players) {
    if (player.isHost || !player.hasVoted || !player.voteCulprit) continue
    const targets = matchCulpritsToRoles(player.voteCulprit)
    if (!targets.length) continue
    const weight = inspectorRoleIds.value.has(player.roleId) ? 2 : 1
    totalWeight += weight * targets.length
    for (const target of targets) {
      const prev = counts.get(target.id) || { roleId: target.id, roleName: target.name, votes: 0 }
      prev.votes += weight
      counts.set(target.id, prev)
    }
  }
  const tally = Array.from(counts.values()).sort(
    (a, b) => b.votes - a.votes || a.roleName.localeCompare(b.roleName, 'zh-CN'),
  )
  return { tally, totalWeight }
}

const voteTally = computed(() => buildVoteTallyFromPlayers(roomState.value?.players || []).tally)

const voteTallyMax = computed(() => {
  const rows = voteTally.value
  if (!rows.length) return 1
  return Math.max(...rows.map((r) => r.votes || 0), 1)
})

const voteProgress = computed(() => {
  if (!roomState.value) return ''
  const max = roomState.value.playerCount || 12
  const submitted = roomState.value.votedCount || 0
  const { totalWeight } = buildVoteTallyFromPlayers(roomState.value.players || [])
  return `（${submitted}/${max} 人已提交 · 有效计票 ${totalWeight} 票）`
})

function matchedCulpritsForItem(item) {
  if (Array.isArray(item.matchedCulprits)) return item.matchedCulprits
  return matchCulpritsToRoles(item.culprit).map((r) => r.name)
}

const VOTE_BAR_TRACK_RPX = 420

function avatarColor(name = '') {
  const colors = ['#8B4513', '#6B2737', '#2D5016', '#4A4A6A', '#9B2335', '#3D5C1A']
  let sum = 0
  for (const ch of name) sum += ch.charCodeAt(0)
  return colors[sum % colors.length]
}

function voteBarStyle(votes = 0) {
  const max = voteTallyMax.value || 1
  const ratio = Math.max(votes, 0) / max
  const widthRpx = Math.max(Math.round(ratio * VOTE_BAR_TRACK_RPX), votes > 0 ? 36 : 0)
  return {
    width: `${widthRpx}rpx`,
    background: '#e84855',
  }
}

const fillableSlots = computed(() => {
  if (!roomState.value || gameStarted.value) return 0
  const max = roomState.value.maxPlayers || 12
  const total = roomState.value.playerCount ?? 0
  return Math.max(0, max - total)
})

const hostMsg = ref('')

const timerText = computed(() => {
  const m = Math.floor(timerSec.value / 60)
  const s = timerSec.value % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})

onLoad((q) => {
  if (q?.course) courseId.value = q.course
})

function rememberHostSession(session) {
  if (!session?.roomCode || !session?.playerToken) return
  hostVisitSession = {
    roomCode: session.roomCode,
    playerToken: session.playerToken,
  }
  if (gameStarted.value) {
    saveHostSession(hostVisitSession)
    clearHostLobbySession()
  } else {
    saveHostLobbySession(hostVisitSession)
  }
}

function persistHostSessionIfStarted() {
  if (!hostVisitSession || !gameStarted.value) return
  saveHostSession(hostVisitSession)
  clearHostLobbySession()
}

function leaveHostRoom({ intentional = false } = {}) {
  if (gameStarted.value && hostVisitSession) {
    saveHostSession(hostVisitSession)
    clearHostLobbySession()
    return
  }

  if (intentional && !gameStarted.value && hostVisitSession) {
    ws.send('CLOSE_ROOM')
    hostVisitSession = null
    roomState.value = null
    clearAllHostSessions()
  }
}

function closeLobbyRoom() {
  if (gameStarted.value || !hostVisitSession) return
  ws.send('CLOSE_ROOM')
  hostVisitSession = null
  roomState.value = null
  clearAllHostSessions()
}

function clearRoomBootstrapTimer() {
  if (roomBootstrapTimer) {
    clearTimeout(roomBootstrapTimer)
    roomBootstrapTimer = null
  }
}

function requestHostRoom() {
  const session =
    hostVisitSession || loadHostSession() || loadHostLobbySession()
  if (session?.playerToken && session?.roomCode) {
    pendingHostRejoin = true
    roomCode.value = session.roomCode
    hostVisitSession = session
    ws.send('REJOIN_ROOM', {
      roomCode: session.roomCode,
      playerToken: session.playerToken,
    })
    return
  }
  ws.send('CREATE_ROOM')
}

function scheduleRoomBootstrapTimeout() {
  clearRoomBootstrapTimer()
  roomBootstrapTimer = setTimeout(() => {
    if (roomState.value) return
    if (connStatus.value === 'connected') {
      statusMessage.value = '房间创建超时，正在重试…'
      pendingHostRejoin = false
      ws.send('CREATE_ROOM')
      scheduleRoomBootstrapTimeout()
      return
    }
    connStatus.value = 'error'
    statusMessage.value = 'WebSocket 连接超时 · 请确认后端已启动（python main.py）并重启前端 dev'
  }, 8000)
}

function bindWsHandlers() {
  if (wsHandlersBound) return
  wsHandlersBound = true

  ws.on('connected', () => {
    connStatus.value = 'connected'
    statusMessage.value = ''
    requestHostRoom()
    scheduleRoomBootstrapTimeout()
  })
  ws.on('ROOM_CREATED', (msg) => {
    roomCode.value = msg.roomCode
    pendingHostRejoin = false
    statusMessage.value = ''
    if (msg.playerToken) {
      rememberHostSession({ roomCode: msg.roomCode, playerToken: msg.playerToken })
    }
  })
  ws.on('JOINED', (msg) => {
    if (!msg.isHost) return
    roomCode.value = msg.roomCode
    pendingHostRejoin = false
    statusMessage.value = ''
    if (msg.playerToken) {
      rememberHostSession({ roomCode: msg.roomCode, playerToken: msg.playerToken })
    }
  })
  ws.on('ROOM_STATE', (msg) => {
    roomState.value = msg.room
    roomCode.value = msg.room.code
    statusMessage.value = ''
    clearRoomBootstrapTimer()
    if (msg.room.gameStarted) gameStarted.value = true
    if (msg.room.phaseIndex !== phaseIndex.value) applyPhase(msg.room.phaseIndex)
    else updateVotes()
    persistHostSessionIfStarted()
  })
  ws.on('ROOM_CLOSED', () => {
    hostVisitSession = null
    roomState.value = null
    gameStarted.value = false
    clearAllHostSessions()
    statusMessage.value = '本局已结束'
  })
  ws.on('ERROR', (msg) => {
    if (pendingHostRejoin && isRejoinRecoverableError(msg.message)) {
      pendingHostRejoin = false
      const hadGameSession = !!loadHostSession()
      hostVisitSession = null
      clearHostLobbySession()
      if (hadGameSession || gameStarted.value) {
        clearHostSession()
        statusMessage.value = '房间已失效，请返回课件后重新开课'
        connStatus.value = 'connected'
        return
      }
      ws.send('CREATE_ROOM')
      scheduleRoomBootstrapTimeout()
      return
    }
    if (roomState.value) roomState.value._error = msg.message
    if (isDev) devMsg.value = msg.message
  })
  ws.on('DEV_OK', (msg) => {
    if (!isDev) return
    if (msg.action === 'DEV_FILL_PLAYERS') devMsg.value = `已填充 ${msg.added} 名测试玩家`
    else if (msg.action === 'DEV_DRAW_ALL') devMsg.value = `已为 ${msg.drawn} 名玩家抽卡`
    else if (msg.action === 'DEV_AUTO_VOTE') devMsg.value = `已模拟 ${msg.voted} 票`
    else if (msg.action === 'DEV_CLEAR_BOTS') devMsg.value = `已移除 ${msg.removed} 名测试玩家`
  })
  ws.on('HOST_OK', (msg) => {
    if (msg.action === 'AUTO_FILL_ROSTER') {
      hostMsg.value = `已补位 ${msg.added} 人 · 抽卡 ${msg.drawn} · 公开线索 ${msg.cluesShared || 0} 条`
    }
  })
  ws.on('error', () => {
    if (!roomState.value) {
      connStatus.value = 'error'
      statusMessage.value = 'WebSocket 连接失败 · 请确认后端已启动'
    }
  })
  ws.on('disconnected', () => {
    if (!roomState.value) {
      connStatus.value = 'connecting'
      statusMessage.value = '连接断开，正在重试…'
    }
  })
}

async function bootstrapHostConnection() {
  connStatus.value = 'connecting'
  statusMessage.value = '正在检测后端…'
  try {
    const health = await uni.request({ url: getHealthUrl(), timeout: 5000 })
    if (health.statusCode !== 200) throw new Error('health bad')
  } catch {
    connStatus.value = 'error'
    statusMessage.value = '后端未连接 · 请在 shengjiang/server 运行 python main.py（端口 3001）'
    return
  }

  await syncServerBootSession(getHealthUrl)
  bindWsHandlers()
  if (!ws.isConnected()) {
    ws.connect()
  } else {
    requestHostRoom()
    scheduleRoomBootstrapTimeout()
  }
}

onMounted(async () => {
  try {
    const res = await uni.request({ url: getSharedUrl('script-data.json') })
    if (res.statusCode !== 200 || !res.data) throw new Error('load failed')
    scriptData.value = res.data
    if (scriptData.value?.phases?.length) applyPhase(0)
  } catch {
    connStatus.value = 'error'
    statusMessage.value = '剧本数据加载失败 · 请确认前端 dev 或后端 /shared 可访问'
    return
  }

  await bootstrapHostConnection()
})

onShow(() => {
  if (!scriptData.value || connStatus.value === 'error') return
  if (!ws.isConnected()) {
    ws.connect()
    return
  }
  if (!roomState.value) {
    requestHostRoom()
    scheduleRoomBootstrapTimeout()
  }
})

onHide(() => {
  clearRoomBootstrapTimer()
  ws.disconnect()
})

onUnmounted(() => {
  stopTimer()
  clearRoomBootstrapTimer()
  if (!leavingIntentionally) {
    leaveHostRoom({ intentional: false })
  } else if (gameStarted.value) {
    leaveHostRoom({ intentional: true })
  }
  wsHandlersBound = false
  ws.clearHandlers()
  ws.disconnect()
})

function applyPhase(i) {
  phaseIndex.value = i
  const p = scriptData.value.phases[i]
  timerSec.value = p.durationSec
  stopTimer()
  showClues.value = false
  showVote.value = false
  showReveal.value = false
}

function updateVotes() {
  /* reactive via roomState */
}

function startTimer() {
  if (timerRunning.value) {
    stopTimer()
    return
  }
  timerRunning.value = true
  timerInterval = setInterval(() => {
    if (timerSec.value > 0) timerSec.value--
    else stopTimer()
  }, 1000)
}

function stopTimer() {
  timerRunning.value = false
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

function navigateBackToCourse() {
  showClues.value = false
  showVote.value = false
  showReveal.value = false
  const pages = getCurrentPages()
  if (pages.length > 1) {
    uni.navigateBack()
    return
  }
  uni.redirectTo({ url: `/pages/classroom?course=${courseId.value}` })
}

function goBack() {
  leavingIntentionally = true
  if (!gameStarted.value) {
    closeLobbyRoom()
  } else if (hostVisitSession) {
    saveHostSession(hostVisitSession)
    clearHostLobbySession()
  }
  ws.disconnect()
  navigateBackToCourse()
}

function endGame() {
  if (!gameStarted.value) return
  ws.send('END_GAME')
}

function prevPhase() {
  ws.send('PREV_PHASE')
}

function nextPhase() {
  ws.send('NEXT_PHASE')
}

function autoFillRoster() {
  if (!fillableSlots.value) return
  hostMsg.value = '正在补位…'
  ws.send('AUTO_FILL_ROSTER')
}

/** 仅当 .env 显式设置 VITE_DEV_TOOLS=1 时显示（生产默认关闭） */
const isDev = import.meta.env.VITE_DEV_TOOLS === '1'
const devMsg = ref('')

function devFill() {
  ws.send('DEV_FILL_PLAYERS', { count: 11 })
}
function devDrawAll() {
  ws.send('DEV_DRAW_ALL')
}
function devAutoVote() {
  ws.send('DEV_AUTO_VOTE')
}
function devClear() {
  ws.send('DEV_CLEAR_BOTS')
}
function goDevPreview() {
  uni.navigateTo({ url: '/pages/script-dev' })
}
</script>

<template>
  <view class="host-page">
    <view class="float-back" @click="goBack">← 返回课件</view>

    <view class="stage">
      <text class="badge">{{ scriptData?.title || '苏区账目风波' }}</text>
      <view class="room-bar">
        <text class="room-label">房间号：</text>
        <text class="room-code">{{ roomCode }}</text>
        <text class="room-meta">{{ roomMeta }}</text>
      </view>

      <view :class="['visual', phase ? `type-${phase.displayType}` : '']">
        <text class="visual-icon">{{ displayType.icon }}</text>
      </view>
      <text class="type-label">{{ displayType.label }}</text>
      <text class="phase-name">阶段 {{ phase?.id }} · {{ phase?.name }}</text>
      <text v-if="phase?.showTimer" class="timer">{{ timerText }}</text>
      <text class="hint">{{ phase?.hostHint }}</text>

      <view v-if="roomState?.sharedClues?.length" class="shared-strip">
        <text class="shared-strip-title">📌 玩家公开线索</text>
        <scroll-view scroll-x class="shared-scroll">
          <view v-for="c in roomState.sharedClues" :key="c.id" class="shared-chip">
            <text class="shared-chip-title">{{ c.title }}</text>
            <text class="shared-chip-body">{{ c.content }}</text>
          </view>
        </scroll-view>
      </view>

      <view class="player-strip">
        <text
          v-for="(chip, idx) in playerChips"
          :key="idx"
          :class="['chip', chip.hasRole ? 'has-role' : '']"
        >{{ chip.text }}</text>
      </view>
    </view>

    <view class="panel">
      <button class="btn ghost" @click="prevPhase">← 上一环节</button>
      <button class="btn primary" @click="nextPhase">下一环节 →</button>
      <button class="btn gold" @click="startTimer">{{ timerRunning ? '暂停' : '开始计时' }}</button>
      <button
        v-if="fillableSlots > 0"
        class="btn fill"
        @click="autoFillRoster"
      >自动补齐 {{ fillableSlots }} 人</button>
      <button v-if="phase?.key === 'search2'" class="btn ghost" @click="showClues = true">查看公共线索</button>
      <button v-if="phase?.key === 'vote'" class="btn ghost" @click="showVote = true">查看投票汇总</button>
      <button v-if="phase?.key === 'reveal'" class="btn ghost" @click="showReveal = true">真相揭晓</button>
      <button v-if="gameStarted" type="button" class="btn danger" @click="endGame">结束游戏</button>
      <view class="dots">
        <view
          v-for="(p, i) in scriptData?.phases || []"
          :key="i"
          :class="['dot', i === phaseIndex ? 'active' : '', i < phaseIndex ? 'done' : '']"
        />
      </view>
    </view>

    <view v-if="hostMsg" class="host-msg-bar">
      <text class="host-msg-text">{{ hostMsg }}</text>
    </view>

    <view v-if="isDev" class="dev-panel">
      <text class="dev-title">🧪 开发者模式</text>
      <text class="dev-hint">测试玩家不占连接位，你可同时用学生端加入；默认留 1 个角色位给你</text>
      <view class="dev-btns">
        <button class="btn dev" @click="devFill">填充 11 人</button>
        <button class="btn dev" @click="devDrawAll">全员抽卡</button>
        <button class="btn dev" @click="devAutoVote">随机投票</button>
        <button class="btn dev ghost" @click="devClear">清空测试</button>
        <button class="btn dev gold" @click="goDevPreview">角色预览</button>
      </view>
      <text v-if="devMsg" class="dev-msg">{{ devMsg }}</text>
    </view>

    <view v-if="showClues" class="overlay" @click="showClues = false">
      <view class="overlay-box" @click.stop>
        <text class="overlay-title">📋 公共线索</text>
        <view v-for="c in scriptData?.publicClues" :key="c.id" class="clue-card">
          <text class="clue-title">{{ c.title }}</text>
          <text class="clue-body">{{ c.content }}</text>
        </view>
        <button class="btn ghost" @click="showClues = false">关闭</button>
      </view>
    </view>

    <view v-if="showVote" class="overlay" @click="showVote = false">
      <view class="overlay-box vote-overlay" @click.stop>
        <text class="overlay-title">🗳️ 投票汇总 {{ voteProgress }}</text>
        <scroll-view scroll-y class="vote-scroll" :show-scrollbar="true">
          <view class="vote-tally-section">
            <text class="vote-section-title">核心元凶 · 票权统计</text>
            <text class="vote-section-hint">仅统计与剧本角色姓名完全匹配的项；多人用顿号/逗号分隔；同一人重复填写去重；督查组每有效 1 人计 2 票</text>
            <view v-if="!voteTally.length" class="vote-tally-empty">暂无有效投票，等待学生填写…</view>
            <view v-for="item in voteTally" :key="item.roleId" class="vote-bar-row">
              <view class="vote-bar-avatar-wrap">
                <view class="vote-bar-avatar" :style="{ background: avatarColor(item.roleName) }">
                  <text class="vote-bar-avatar-text">{{ (item.roleName || '?').slice(0, 1) }}</text>
                </view>
                <text class="vote-bar-name">{{ item.roleName }}</text>
              </view>
              <view class="vote-bar-body">
                <view class="vote-bar-meta">
                  <text class="vote-bar-count">{{ item.votes }} 票</text>
                </view>
                <view class="vote-bar-track">
                  <view class="vote-bar-fill" :style="voteBarStyle(item.votes)" />
                </view>
              </view>
            </view>
          </view>

          <view class="vote-detail-section">
            <text class="vote-section-title">逐人作答明细</text>
            <view v-if="!voteSubmissions.length" class="vote-empty">暂无提交，等待学生填写…</view>
            <view v-for="item in voteSubmissions" :key="item.playerId" class="vote-card">
              <text class="vote-card-head">
                {{ item.nickname }}（{{ item.roleName || '未抽卡' }}）
                <text v-if="item.isInspector" class="vote-weight-tag">督查组 · 2 票权</text>
              </text>
              <text class="vote-card-line"><text class="vote-card-label">事件真相：</text>{{ item.truth }}</text>
              <text class="vote-card-line"><text class="vote-card-label">核心元凶：</text>{{ item.culprit }}</text>
              <text v-if="matchedCulpritsForItem(item).length" class="vote-card-line vote-card-valid">
                <text class="vote-card-label">有效计票：</text>{{ matchedCulpritsForItem(item).join('、') }}
              </text>
              <text v-else class="vote-card-line vote-card-invalid">
                <text class="vote-card-label">有效计票：</text>未匹配到剧本角色姓名
              </text>
            </view>
          </view>
        </scroll-view>
        <button class="btn ghost" @click="showVote = false">关闭</button>
      </view>
    </view>

    <view v-if="showReveal" class="overlay" @click="showReveal = false">
      <view class="overlay-box" @click.stop>
        <text class="overlay-title">✨ 真相揭晓</text>
        <text class="truth-summary">{{ scriptData?.truth?.summary }}</text>
        <view v-for="(item, i) in scriptData?.truth?.timeline" :key="i" class="truth-item">{{ item }}</view>
        <text class="truth-moral">{{ scriptData?.truth?.moral }}</text>
        <button class="btn ghost" @click="showReveal = false">关闭</button>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
.host-page {
  min-height: 100vh;
  background: #0d0d12;
  color: #fff;
  display: flex;
  flex-direction: column;
}

.float-back {
  position: fixed;
  top: 20rpx;
  left: 20rpx;
  z-index: 300;
  padding: 10rpx 24rpx;
  font-size: 24rpx;
  background: rgba(0, 0, 0, 0.55);
  border-radius: 12rpx;
}

.stage {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80rpx 40rpx 24rpx;
  background: radial-gradient(ellipse at 50% 0%, rgba(232, 72, 85, 0.18), transparent 60%),
    linear-gradient(180deg, #1a0a0a 0%, #0d0d12 100%);
}

.badge {
  font-size: 26rpx;
  color: #ffd166;
  letter-spacing: 0.15em;
}

.room-bar {
  margin: 20rpx 0;
  text-align: center;
}

.room-label {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.6);
}

.room-code {
  font-size: 56rpx;
  color: #ffd166;
  font-weight: 700;
  letter-spacing: 0.1em;
}

.room-meta {
  display: block;
  margin-top: 8rpx;
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.5);
}

.visual {
  width: 280rpx;
  height: 280rpx;
  border-radius: 50%;
  border: 4rpx solid rgba(255, 209, 102, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 24rpx 0;
}

.visual-icon {
  font-size: 120rpx;
}

.type-label {
  font-size: 56rpx;
  font-weight: 700;
}

.phase-name {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 8rpx;
}

.timer {
  font-size: 72rpx;
  color: #ffd166;
  font-weight: 700;
  margin-top: 16rpx;
}

.hint {
  margin-top: 20rpx;
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.6);
  text-align: center;
  max-width: 600rpx;
}

.shared-strip {
  width: 100%;
  max-width: 900rpx;
  margin-top: 24rpx;
  padding: 16rpx 20rpx;
  border-radius: 12rpx;
  background: rgba(201, 162, 39, 0.12);
  border: 1px solid rgba(201, 162, 39, 0.25);
}

.shared-strip-title {
  display: block;
  font-size: 24rpx;
  color: #e8c96a;
  margin-bottom: 12rpx;
}

.shared-scroll {
  white-space: nowrap;
}

.shared-chip {
  display: inline-block;
  vertical-align: top;
  width: 280rpx;
  margin-right: 16rpx;
  padding: 14rpx;
  border-radius: 10rpx;
  background: rgba(0, 0, 0, 0.35);
  white-space: normal;
}

.shared-chip-title {
  display: block;
  font-size: 22rpx;
  font-weight: 700;
  color: #e8c96a;
  margin-bottom: 6rpx;
}

.shared-chip-body {
  display: block;
  font-size: 20rpx;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.75);
}

.player-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  justify-content: center;
  margin-top: 32rpx;
}

.chip {
  font-size: 22rpx;
  padding: 8rpx 20rpx;
  border-radius: 20rpx;
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.6);
}

.chip.has-role {
  background: rgba(232, 72, 85, 0.25);
  color: #fff;
}

.panel {
  padding: 24rpx;
  background: #16161f;
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  align-items: center;
}

.btn {
  font-size: 24rpx;
  padding: 12rpx 24rpx;
  border-radius: 12rpx;
  border: none;
}

.btn.primary { background: #e84855; color: #fff; }
.btn.gold { background: #ffd166; color: #1a1a1a; }
.btn.danger { background: #8b2e2e; color: #fff; border: 1px solid rgba(255, 120, 120, 0.35); }
.btn.ghost { background: rgba(255, 255, 255, 0.1); color: #fff; }
.btn.fill { background: rgba(100, 180, 255, 0.22); color: #9fd4ff; border: 1px solid rgba(100, 180, 255, 0.35); }

.host-msg-bar {
  padding: 12rpx 24rpx 0;
  background: #16161f;
}

.host-msg-text {
  display: block;
  font-size: 22rpx;
  color: rgba(159, 212, 255, 0.85);
  text-align: center;
}

.dots {
  display: flex;
  gap: 8rpx;
  flex: 1;
  flex-wrap: wrap;
}

.dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
}

.dot.active { background: #e84855; transform: scale(1.3); }
.dot.done { background: rgba(255, 209, 102, 0.6); }

.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  z-index: 200;
  padding: 60rpx 40rpx;
  overflow-y: auto;
}

.overlay-box {
  max-width: 700rpx;
  margin: 0 auto;
}

.overlay-title {
  display: block;
  font-size: 36rpx;
  color: #ffd166;
  font-weight: 700;
  margin-bottom: 24rpx;
}

.clue-card {
  padding: 24rpx;
  margin-bottom: 16rpx;
  background: rgba(255, 255, 255, 0.06);
  border-left: 6rpx solid #ffd166;
  border-radius: 12rpx;
}

.clue-title {
  display: block;
  font-size: 28rpx;
  font-weight: 600;
  margin-bottom: 8rpx;
}

.clue-body {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.6);
  line-height: 1.7;
}

.vote-overlay {
  max-height: 88vh;
  width: min(92vw, 720rpx);
  display: flex;
  flex-direction: column;
  background: rgba(22, 22, 30, 0.98);
  border-radius: 20rpx;
  padding: 28rpx 24rpx 20rpx;
  box-sizing: border-box;
}

.vote-scroll {
  height: 62vh;
  margin-bottom: 20rpx;
}

.vote-tally-section {
  padding-bottom: 28rpx;
  margin-bottom: 28rpx;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}

.vote-detail-section {
  padding-bottom: 12rpx;
}

.vote-section-title {
  display: block;
  font-size: 28rpx;
  font-weight: 700;
  color: #ffd166;
  margin-bottom: 8rpx;
}

.vote-section-hint {
  display: block;
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.45);
  margin-bottom: 24rpx;
  line-height: 1.5;
}

.vote-tally-empty {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.45);
  text-align: center;
  padding: 32rpx 0 12rpx;
}

.vote-bar-row {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin-bottom: 24rpx;
}

.vote-bar-avatar-wrap {
  flex-shrink: 0;
  width: 88rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
}

.vote-bar-avatar {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2rpx solid rgba(255, 209, 102, 0.35);
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.25);
}

.vote-bar-avatar-text {
  font-size: 30rpx;
  font-weight: 700;
  color: #fff;
}

.vote-bar-name {
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.72);
  text-align: center;
  line-height: 1.2;
  max-width: 88rpx;
  word-break: break-all;
}

.vote-bar-body {
  flex: 1;
  min-width: 0;
}

.vote-bar-meta {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 8rpx;
}

.vote-bar-count {
  font-size: 24rpx;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.88);
}

.vote-bar-track {
  width: 420rpx;
  max-width: 100%;
  height: 36rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.14);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.vote-bar-fill {
  display: block;
  height: 100%;
  min-width: 36rpx;
  border-radius: 999rpx;
  box-shadow: 0 0 12rpx rgba(232, 72, 85, 0.45);
}

.vote-empty {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.45);
  text-align: center;
  padding: 40rpx 0;
}

.vote-card {
  padding: 24rpx;
  margin-bottom: 16rpx;
  background: rgba(255, 255, 255, 0.06);
  border-left: 6rpx solid #e84855;
  border-radius: 12rpx;
}

.vote-card-head {
  display: block;
  font-size: 28rpx;
  font-weight: 600;
  margin-bottom: 12rpx;
  line-height: 1.5;
}

.vote-weight-tag {
  display: inline-block;
  margin-left: 8rpx;
  padding: 2rpx 10rpx;
  font-size: 20rpx;
  font-weight: 500;
  color: #ffd166;
  background: rgba(255, 209, 102, 0.12);
  border: 1px solid rgba(255, 209, 102, 0.28);
  border-radius: 999rpx;
  vertical-align: middle;
}

.vote-card-line {
  display: block;
  font-size: 26rpx;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: 8rpx;
}

.vote-card-label {
  color: #ffd166;
}

.vote-card-valid {
  color: rgba(144, 238, 144, 0.92);
}

.vote-card-invalid {
  color: rgba(255, 160, 160, 0.85);
}

.truth-summary {
  display: block;
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.6);
  line-height: 1.8;
  margin-bottom: 24rpx;
}

.truth-item {
  padding: 16rpx;
  margin-bottom: 8rpx;
  background: rgba(255, 255, 255, 0.05);
  border-left: 4rpx solid #e84855;
  border-radius: 8rpx;
  font-size: 26rpx;
}

.truth-moral {
  display: block;
  margin-top: 24rpx;
  padding: 16rpx;
  border-left: 4rpx solid #ffd166;
  color: #ffd166;
  line-height: 1.8;
}

.dev-panel {
  padding: 20rpx 24rpx 32rpx;
  background: rgba(255, 209, 102, 0.08);
  border-top: 1px solid rgba(255, 209, 102, 0.25);
}

.dev-title {
  display: block;
  font-size: 26rpx;
  color: #ffd166;
  font-weight: 700;
}

.dev-hint {
  display: block;
  margin-top: 6rpx;
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.45);
}

.dev-btns {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-top: 16rpx;
}

.btn.dev {
  font-size: 22rpx;
  padding: 10rpx 20rpx;
  background: rgba(255, 209, 102, 0.2);
  color: #ffd166;
  border: 1px solid rgba(255, 209, 102, 0.35);
}

.dev-msg {
  display: block;
  margin-top: 12rpx;
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.55);
}
</style>
