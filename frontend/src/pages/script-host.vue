<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import * as ws from '@/utils/ws-client'
import { getSharedUrl } from '@/utils/config'
import {
  clearHostSession,
  isRejoinRecoverableError,
  loadHostSession,
  saveHostSession,
} from '@/utils/script-session'

const courseId = ref('11')
const scriptData = ref(null)
const roomState = ref(null)
const roomCode = ref('——')
const phaseIndex = ref(0)
const timerSec = ref(0)
const timerRunning = ref(false)
const showClues = ref(false)
const showVote = ref(false)
const showReveal = ref(false)
const connStatus = ref('connecting') // connecting | connected | error
let timerInterval = null
let pendingHostRejoin = false

const phase = computed(() => scriptData.value?.phases?.[phaseIndex.value])
const displayType = computed(() => {
  if (!phase.value || !scriptData.value) return { label: '', icon: '•' }
  return scriptData.value.displayTypes[phase.value.displayType] || { label: phase.value.name, icon: '•' }
})

const roomMeta = computed(() => {
  if (connStatus.value === 'error') {
    return '后端未连接 · 请先启动 server（python main.py）'
  }
  if (!roomState.value) return '连接中…'
  const r = roomState.value
  return `已连接 ${r.connectionCount}/${r.maxConnections} · 玩家 ${r.playerCount}/${r.maxPlayers} · 已抽卡 ${r.maxPlayers - r.rolesRemaining}/${r.maxPlayers}`
})

const playerChips = computed(() => {
  if (!roomState.value) return []
  return roomState.value.players
    .filter((p) => !p.isHost)
    .map((p) => ({
      text: `${p.connected === false ? '💤 ' : ''}${p.isBot ? '🤖 ' : ''}${p.nickname}：${p.roleName || '未抽卡'}${p.hasVoted ? ' · 已答' : ''}`,
      hasRole: !!p.roleName,
    }))
})

const voteSubmissions = computed(() => roomState.value?.voteSubmissions || [])

const voteProgress = computed(() => {
  if (!roomState.value) return ''
  const max = roomState.value.playerCount || 12
  return `（${roomState.value.votedCount}/${max} 人已提交）`
})

const voteReference = computed(() => scriptData.value?.voteForm?.referenceAnswer || null)

const timerText = computed(() => {
  const m = Math.floor(timerSec.value / 60)
  const s = timerSec.value % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})

onLoad((q) => {
  if (q?.course) courseId.value = q.course
})

onMounted(async () => {
  try {
    const res = await uni.request({ url: getSharedUrl('script-data.json') })
    if (res.statusCode !== 200 || !res.data) throw new Error('load failed')
    scriptData.value = res.data
    if (scriptData.value?.phases?.length) applyPhase(0)
  } catch {
    connStatus.value = 'error'
    return
  }

  ws.on('connected', () => {
    connStatus.value = 'connected'
    const session = loadHostSession()
    if (session?.playerToken && session?.roomCode) {
      pendingHostRejoin = true
      roomCode.value = session.roomCode
      ws.send('REJOIN_ROOM', {
        roomCode: session.roomCode,
        playerToken: session.playerToken,
      })
      return
    }
    ws.send('CREATE_ROOM')
  })
  ws.on('ROOM_CREATED', (msg) => {
    roomCode.value = msg.roomCode
    pendingHostRejoin = false
    if (msg.playerToken) {
      saveHostSession({ roomCode: msg.roomCode, playerToken: msg.playerToken })
    }
  })
  ws.on('JOINED', (msg) => {
    if (!msg.isHost) return
    roomCode.value = msg.roomCode
    pendingHostRejoin = false
    if (msg.playerToken) {
      saveHostSession({ roomCode: msg.roomCode, playerToken: msg.playerToken })
    }
  })
  ws.on('ROOM_STATE', (msg) => {
    roomState.value = msg.room
    roomCode.value = msg.room.code
    if (msg.room.phaseIndex !== phaseIndex.value) applyPhase(msg.room.phaseIndex)
    else updateVotes()
  })
  ws.on('ERROR', (msg) => {
    if (pendingHostRejoin && isRejoinRecoverableError(msg.message)) {
      pendingHostRejoin = false
      clearHostSession()
      ws.send('CREATE_ROOM')
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
  ws.on('error', () => {
    if (!roomState.value) connStatus.value = 'error'
  })
  ws.on('disconnected', () => {
    if (!roomState.value) connStatus.value = 'error'
  })

  ws.connect()
})

onUnmounted(() => {
  stopTimer()
})

function applyPhase(i) {
  phaseIndex.value = i
  const p = scriptData.value.phases[i]
  timerSec.value = p.durationSec
  stopTimer()
  showClues.value = p.key === 'search2'
  showVote.value = p.key === 'vote'
  showReveal.value = p.key === 'reveal'
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

function resetTimer() {
  stopTimer()
  timerSec.value = scriptData.value.phases[phaseIndex.value].durationSec
}

function goBack() {
  uni.navigateBack()
}

function prevPhase() {
  ws.send('PREV_PHASE')
}

function nextPhase() {
  ws.send('NEXT_PHASE')
}

const isDev = import.meta.env.DEV
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
      <button class="btn ghost" @click="resetTimer">重置</button>
      <view class="dots">
        <view
          v-for="(p, i) in scriptData?.phases || []"
          :key="i"
          :class="['dot', i === phaseIndex ? 'active' : '', i < phaseIndex ? 'done' : '']"
        />
      </view>
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
        <text class="overlay-title">🗳️ 学生作答汇总 {{ voteProgress }}</text>
        <scroll-view scroll-y class="vote-scroll">
          <view v-if="!voteSubmissions.length" class="vote-empty">暂无提交，等待学生填写…</view>
          <view v-for="item in voteSubmissions" :key="item.playerId" class="vote-card">
            <text class="vote-card-head">{{ item.nickname }}（{{ item.roleName || '未抽卡' }}）</text>
            <text class="vote-card-line"><text class="vote-card-label">事件真相：</text>{{ item.truth }}</text>
            <text class="vote-card-line"><text class="vote-card-label">核心元凶：</text>{{ item.culprit }}</text>
          </view>
        </scroll-view>
        <view v-if="voteReference" class="vote-ref">
          <text class="vote-ref-title">参考答案（仅教师可见）</text>
          <text class="vote-ref-line">事件真相：{{ voteReference.truth }}</text>
          <text class="vote-ref-line">核心元凶：{{ voteReference.culprit }}</text>
        </view>
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
  z-index: 100;
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
.btn.ghost { background: rgba(255, 255, 255, 0.1); color: #fff; }

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
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.vote-scroll {
  flex: 1;
  max-height: 50vh;
  margin-bottom: 20rpx;
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

.vote-ref {
  padding: 20rpx;
  margin-bottom: 20rpx;
  background: rgba(255, 209, 102, 0.08);
  border-radius: 12rpx;
  border: 1px solid rgba(255, 209, 102, 0.2);
}

.vote-ref-title {
  display: block;
  font-size: 24rpx;
  color: #ffd166;
  margin-bottom: 8rpx;
}

.vote-ref-line {
  display: block;
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
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
