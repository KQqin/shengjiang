<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import * as ws from '@/utils/ws-client'
import { getSharedUrl } from '@/utils/config'
import { buildPlayerContent, buildAllRoles } from '@/utils/script-content'
import {
  clearPlayerSession,
  formatIdentityCode,
  isRejoinRecoverableError,
  loadPlayerSession,
  savePlayerSession,
} from '@/utils/script-session'

const courseId = ref('11')
const isPreview = ref(false)
const previewRoleIndex = ref(5)
const previewPhaseIndex = ref(6)
const scriptData = ref(null)
const statusLine = ref('加入房间并抽取角色')
const roomCode = ref('')
const nickname = ref('')
const joined = ref(false)
const hasRole = ref(false)
const drawVisible = ref(false)
const roleReveal = ref(null)
const playerContent = ref(null)
const roomState = ref(null)
const voteTruth = ref('')
const voteCulprit = ref('')
const voteSubmitted = ref(false)

const showCharacter = ref(false)
const showScript = ref(false)
const clueView = ref('table')
const focusedClue = ref(null)
const activeSheet = ref('')
const myPlayerId = ref('')
const expandedRoleId = ref('')
const posterLoadFailed = ref(false)
const playerToken = ref('')
const pendingRejoin = ref(false)
let lastSyncedPhase = -1

const identityCode = computed(() => formatIdentityCode(playerToken.value))

const allRolesList = computed(() => {
  if (playerContent.value?.allRoles?.length) return playerContent.value.allRoles
  if (scriptData.value?.roles?.length) return buildAllRoles(scriptData.value)
  return []
})

const rolePosterUrl = computed(() => {
  const poster = roleReveal.value?.poster || playerContent.value?.public?.poster
  if (!poster) return ''
  return getSharedUrl(poster)
})

const scriptReadable = computed(() => unlocked.value.includes('script'))

const unlocked = computed(() => playerContent.value?.unlocked || [])

const phaseName = computed(() => {
  const idx = roomState.value?.phaseIndex ?? 0
  return scriptData.value?.phases?.[idx]?.name || '等待开始'
})

const sidePlayers = computed(() => {
  const list = roomState.value?.players?.filter((p) => !p.isHost) || []
  const mid = Math.ceil(list.length / 2)
  return { left: list.slice(0, mid), right: list.slice(mid) }
})

function mapPublicClue(c, i) {
  const title = c.title || ''
  return {
    id: c.id,
    type: 'public',
    title,
    shortTitle: title.length > 7 ? `${title.slice(0, 7)}…` : title,
    content: c.content,
    subtitle: c.subtitle || '中央苏区供给站',
    category: c.category || '公共线索',
    icon: c.icon || '📜',
    accent: c.accent || '#8B4513',
    seal: c.seal || '公',
    cardNo: `P-${String(i + 1).padStart(2, '0')}`,
  }
}

const publicPoolClues = computed(() => {
  if (!roomState.value?.publicCluesReleased || !scriptData.value?.publicClues) return []
  return scriptData.value.publicClues.map(mapPublicClue)
})

const sharedPoolClues = computed(() => {
  return (roomState.value?.sharedClues || []).map((c, i) => ({
    id: c.id,
    type: 'shared',
    title: c.title,
    shortTitle: (c.roleName || c.playerName || '玩家').slice(0, 6),
    content: c.content,
    sharedBy: c.roleName || c.playerName,
    cardNo: `S-${String(i + 1).padStart(2, '0')}`,
    icon: '📌',
  }))
})

const centerClues = computed(() => [...publicPoolClues.value, ...sharedPoolClues.value])

const privateClueList = computed(() => {
  const list = []
  const u = unlocked.value
  if (u.includes('clue1') && playerContent.value?.clue1) {
    list.push({
      key: 'clue1',
      title: '私人线索 ①',
      shortTitle: roleReveal.value?.name || '线索',
      content: playerContent.value.clue1,
      cardNo: '#01',
      icon: '📋',
    })
  }
  if (u.includes('clue2') && playerContent.value?.clue2) {
    list.push({
      key: 'clue2',
      title: '私人线索 ②',
      shortTitle: roleReveal.value?.name || '线索',
      content: playerContent.value.clue2,
      cardNo: '#02',
      icon: '🔍',
    })
  }
  return list
})

const sharedClueIdSet = computed(() => new Set((roomState.value?.sharedClues || []).map((s) => s.id)))

const avatarColor = (name = '') => {
  const colors = ['#8B4513', '#6B2737', '#2D5016', '#4A4A6A', '#9B2335', '#3D5C1A']
  let sum = 0
  for (const ch of name) sum += ch.charCodeAt(0)
  return colors[sum % colors.length]
}

onLoad((q) => {
  if (q?.course) courseId.value = q.course
  if (q?.preview === '1' || q?.preview === 'true') isPreview.value = true
  if (q?.role != null) previewRoleIndex.value = Number(q.role) || 0
  if (q?.phase != null) previewPhaseIndex.value = Number(q.phase) || 3
})

function initPreviewMode() {
  const data = scriptData.value
  if (!data?.roles?.length) return

  const roleIdx = Math.min(Math.max(0, previewRoleIndex.value), data.roles.length - 1)
  const role = data.roles[roleIdx]
  const phaseIdx = Math.min(Math.max(0, previewPhaseIndex.value), (data.phases?.length || 1) - 1)

  joined.value = true
  hasRole.value = true
  drawVisible.value = false
  roleReveal.value = {
    id: role.id,
    name: role.name,
    gender: role.gender,
    title: role.title,
    tag: role.tag,
  }
  myPlayerId.value = 'preview-me'
  playerContent.value = buildPlayerContent(role, phaseIdx, data)

  const mockPlayers = data.roles.map((r, i) => ({
    id: i === roleIdx ? 'preview-me' : `preview-p${i}`,
    nickname: r.name,
    roleName: r.name,
    isHost: false,
  }))

  roomState.value = {
    code: '888888',
    phaseIndex: phaseIdx,
    publicCluesReleased: phaseIdx >= 4,
    sharedClues: [],
    players: [{ id: 'preview-host', nickname: '教师', isHost: true }, ...mockPlayers],
  }
  statusLine.value = `[预览] ${role.name} · ${data.phases?.[phaseIdx]?.name || '主界面'}`
}

function resetToJoinScreen(message = '教师已结束本局，请重新加入') {
  joined.value = false
  hasRole.value = false
  drawVisible.value = false
  roleReveal.value = null
  playerContent.value = null
  roomState.value = null
  playerToken.value = ''
  myPlayerId.value = ''
  showCharacter.value = false
  showScript.value = false
  activeSheet.value = ''
  voteTruth.value = ''
  voteCulprit.value = ''
  voteSubmitted.value = false
  pendingRejoin.value = false
  lastSyncedPhase = -1
  clearPlayerSession()
  statusLine.value = message
  ws.disconnect()
  setTimeout(() => ws.connect(), 200)
}

function syncPlayerContent(phaseIndex) {
  if (!hasRole.value || !roleReveal.value?.id || !scriptData.value) return
  const role = scriptData.value.roles.find((r) => r.id === roleReveal.value.id)
  if (!role) return
  playerContent.value = buildPlayerContent(role, phaseIndex, scriptData.value)
  lastSyncedPhase = phaseIndex
}

function votePlaceholder(field) {
  if (field.key === 'culprit') return '填写核心责任人姓名'
  return field.placeholder || ''
}

function onVoteInput(key, e) {
  const val = e?.detail?.value ?? e?.target?.value ?? ''
  if (key === 'truth') voteTruth.value = val
  else voteCulprit.value = val
}

onMounted(async () => {
  try {
    const res = await uni.request({ url: getSharedUrl('script-data.json') })
    scriptData.value = res.data
  } catch {
    statusLine.value = '剧本数据加载失败'
  }

  if (isPreview.value) {
    initPreviewMode()
    return
  }

  ws.clearHandlers()

  const saved = loadPlayerSession()
  if (saved?.roomCode) roomCode.value = saved.roomCode
  if (saved?.nickname) nickname.value = saved.nickname

  ws.on('connected', () => {
    const session = loadPlayerSession()
    if (session?.playerToken && session?.roomCode) {
      pendingRejoin.value = true
      roomCode.value = session.roomCode
      nickname.value = session.nickname || nickname.value
      statusLine.value = '正在恢复身份…'
      ws.send('REJOIN_ROOM', {
        roomCode: session.roomCode,
        playerToken: session.playerToken,
      })
      return
    }
    statusLine.value = '已连接服务器，请输入房间号'
  })
  ws.on('JOINED', (msg) => {
    joined.value = true
    myPlayerId.value = msg.playerId
    playerToken.value = msg.playerToken || playerToken.value
    roomCode.value = msg.roomCode
    savePlayerSession({
      roomCode: msg.roomCode,
      playerToken: msg.playerToken,
      nickname: nickname.value.trim() || '玩家',
    })
    if (msg.isHost) {
      clearPlayerSession()
      joined.value = false
      hasRole.value = false
      drawVisible.value = false
      playerToken.value = ''
      pendingRejoin.value = false
      statusLine.value = '你是教师，请使用教师大屏页面'
      return
    }
    if (msg.rejoined) {
      statusLine.value = `已恢复房间 ${msg.roomCode}`
      if (!hasRole.value) drawVisible.value = true
      return
    }
    pendingRejoin.value = false
    statusLine.value = `已加入房间 ${msg.roomCode}`
    drawVisible.value = true
  })
  ws.on('ROLE_DRAWN', (msg) => {
    const firstDraw = !hasRole.value
    hasRole.value = true
    drawVisible.value = false
    roleReveal.value = msg.role
    if (firstDraw && !pendingRejoin.value) showCharacter.value = true
    statusLine.value = `你是：${msg.role.name}`
    pendingRejoin.value = false
  })
  ws.on('PLAYER_CONTENT', (msg) => {
    playerContent.value = msg.content
    if (typeof msg.phaseIndex === 'number') lastSyncedPhase = msg.phaseIndex
  })
  ws.on('ROOM_STATE', (msg) => {
    roomState.value = msg.room
    const phaseIdx = msg.room?.phaseIndex ?? 0
    if (phaseIdx !== lastSyncedPhase) {
      syncPlayerContent(phaseIdx)
    }
    const me = msg.room?.players?.find((p) => p.id === myPlayerId.value)
    if (me) {
      voteTruth.value = me.voteTruth || ''
      voteCulprit.value = me.voteCulprit || ''
      voteSubmitted.value = !!me.hasVoted
      if (me.roleName && !hasRole.value) {
        hasRole.value = true
        drawVisible.value = false
      }
    }
    if (joined.value && !hasRole.value && msg.room.gameStarted) {
      drawVisible.value = false
      statusLine.value = '游戏已开始，未能抽卡'
    }
    if (
      joined.value &&
      !msg.room.gameStarted &&
      msg.room.hostConnected === false
    ) {
      resetToJoinScreen('教师已离开，房间已关闭')
      return
    }
    if (pendingRejoin.value && !hasRole.value) {
      pendingRejoin.value = false
    }
  })
  ws.on('ROOM_CLOSED', (msg) => {
    const text =
      msg.reason === 'game_ended'
        ? '教师已结束本局，感谢参与'
        : '教师已离开，房间已关闭，请重新加入'
    resetToJoinScreen(text)
  })
  ws.on('disconnected', () => {
    if (!joined.value) return
    const session = loadPlayerSession()
    if (session?.playerToken && session?.roomCode) {
      pendingRejoin.value = true
    }
  })
  ws.on('ERROR', (msg) => {
    if (pendingRejoin.value) {
      pendingRejoin.value = false
      joined.value = false
      hasRole.value = false
      drawVisible.value = false
      showCharacter.value = false
      lastSyncedPhase = -1
      if (isRejoinRecoverableError(msg.message)) clearPlayerSession()
      statusLine.value = `恢复失败：${msg.message}，请重新加入`
      return
    }
    if (joined.value && isRejoinRecoverableError(msg.message)) {
      resetToJoinScreen(
        msg.message.includes('房间') ? msg.message : '房间已关闭，请重新加入',
      )
      return
    }
    statusLine.value = `⚠ ${msg.message}`
  })

  ws.connect()
})

onUnmounted(() => {
  ws.clearHandlers()
  ws.disconnect()
})

function joinRoom() {
  const code = roomCode.value.trim()
  const name = nickname.value.trim() || '玩家'
  if (code.length !== 6) {
    statusLine.value = '请输入 6 位房间号'
    return
  }
  nickname.value = name
  ws.send('JOIN_ROOM', { roomCode: code, nickname: name })
}

function drawRole() {
  ws.send('DRAW_ROLE')
}

function dismissCharacter() {
  showCharacter.value = false
}

function openCharacter() {
  showCharacter.value = true
  showScript.value = false
  clueView.value = 'table'
}

function dismissScript() {
  showScript.value = false
}

function openScript() {
  posterLoadFailed.value = false
  showScript.value = true
  showCharacter.value = false
  clueView.value = 'table'
  activeSheet.value = ''
}

function openPrivateClues() {
  clueView.value = 'private'
  showCharacter.value = false
  showScript.value = false
  activeSheet.value = ''
}

function backToPublicPool() {
  clueView.value = 'table'
}

function openClueFocus(card) {
  focusedClue.value = card
}

function closeClueFocus() {
  focusedClue.value = null
}

function isClueShared(clueKey) {
  return sharedClueIdSet.value.has(`${myPlayerId.value}:${clueKey}`)
}

function shareClue(clueKey) {
  const clue = privateClueList.value.find((c) => c.key === clueKey)
  if (!clue || isClueShared(clueKey)) return

  if (isPreview.value) {
    if (!roomState.value.sharedClues) roomState.value.sharedClues = []
    roomState.value.sharedClues.push({
      id: `${myPlayerId.value}:${clueKey}`,
      playerId: myPlayerId.value,
      playerName: roleReveal.value?.name,
      roleName: roleReveal.value?.name,
      clueKey,
      title: `${roleReveal.value?.name} · ${clue.title}`,
      content: clue.content,
    })
    clueView.value = 'table'
    return
  }

  ws.send('SHARE_CLUE', { clueKey })
  clueView.value = 'table'
}

function openSheet(key) {
  if (key === 'vote' && !unlocked.value.includes('vote')) return
  activeSheet.value = key
}

function closeSheet() {
  activeSheet.value = ''
}

function submitVote() {
  const truth = voteTruth.value.trim()
  const culprit = voteCulprit.value.trim()
  if (!truth) {
    statusLine.value = '请填写事件真相'
    return
  }
  if (!culprit) {
    statusLine.value = '请填写核心元凶'
    return
  }
  ws.send('CAST_VOTE', { truth, culprit })
  voteSubmitted.value = true
  statusLine.value = '答案已提交'
}

function toggleRoleIntro(roleId) {
  expandedRoleId.value = expandedRoleId.value === roleId ? '' : roleId
}

function leaveRoom() {
  resetToJoinScreen('已退出房间，可重新加入')
}

function goBack() {
  uni.navigateBack()
}

function isMe(player) {
  return player.id === myPlayerId.value
}
</script>

<template>
  <view class="role-app">
    <!-- 加入房间 -->
    <view v-if="!joined" class="join-screen">
      <text class="join-back" @click="goBack">← 返回</text>
      <view class="join-hero">
        <text class="join-title">🎭 {{ scriptData?.title || '苏区账目风波' }}</text>
        <text class="join-sub">学生端 · 加入房间抽取角色</text>
      </view>
      <view class="join-form">
        <input v-model="roomCode" class="input" placeholder="输入 6 位房间号" maxlength="6" />
        <input v-model="nickname" class="input" placeholder="你的昵称" maxlength="12" />
        <button type="button" class="btn primary" @click="joinRoom">加入房间</button>
        <text class="join-status">{{ statusLine }}</text>
      </view>
    </view>

    <!-- 抽卡 -->
    <view v-else-if="!hasRole" class="draw-screen">
      <text class="join-back" @click="goBack">← 返回</text>
      <view class="draw-card">
        <text class="draw-title">{{ scriptData?.title || '苏区账目风波' }}</text>
        <text class="draw-room">房间 {{ roomState?.code || roomCode }}</text>
        <text class="draw-phase">当前环节：{{ phaseName }}</text>
        <button v-if="drawVisible" class="btn gold draw-btn" @click="drawRole">🎴 抽取角色卡</button>
        <text class="draw-hint">剩余角色 {{ roomState?.rolesRemaining ?? 12 }} / 12</text>
        <text v-if="identityCode" class="draw-identity">身份码 {{ identityCode }}</text>
        <text class="draw-status">{{ statusLine }}</text>
      </view>
    </view>

    <!-- 主界面 -->
    <view v-else class="main-screen">
      <view v-if="isPreview" class="preview-badge">预览模式 · 无需联机</view>
      <view class="topbar">
        <view class="topbar-left">
          <text class="script-title">{{ scriptData?.title || '苏区账目风波' }}</text>
          <text class="phase-badge">{{ phaseName }}</text>
        </view>
        <view class="topbar-right">
          <text v-if="identityCode" class="identity-tag">身份码 {{ identityCode }}</text>
          <text class="room-tag">房间 {{ roomState?.code }}</text>
        </view>
      </view>

      <view class="table-area">
        <view class="player-col player-col--left">
          <view
            v-for="p in sidePlayers.left"
            :key="p.id"
            class="player-chip"
            :class="{ me: isMe(p) }"
          >
            <view class="avatar" :style="{ background: avatarColor(p.roleName || p.nickname) }">
              <text class="avatar-text">{{ (p.roleName || p.nickname || '?').slice(0, 1) }}</text>
            </view>
            <text class="player-name">{{ p.roleName || p.nickname }}</text>
          </view>
        </view>

        <view class="parchment">
          <view class="parchment-inner">
            <scroll-view scroll-y class="board-scroll">
              <!-- 公开卡池 -->
              <view v-if="clueView === 'table'">
                <text class="board-label">📋 公开卡池</text>

                <view v-if="publicPoolClues.length" class="pool-section">
                  <text class="pool-section-label">公共线索 · 教师公布</text>
                  <view class="clue-grid clue-grid--pool">
                    <view
                      v-for="card in publicPoolClues"
                      :key="card.id"
                      class="pub-clue-card pub-clue-card--compact"
                      :style="{ '--accent': card.accent }"
                      @click="openClueFocus(card)"
                    >
                      <view class="pub-clue-seal">
                        <text class="pub-clue-seal-txt">{{ card.seal }}</text>
                      </view>
                      <text class="pub-clue-cat">{{ card.category }}</text>
                      <view class="pub-clue-title-box">
                        <text class="pub-clue-title">{{ card.shortTitle }}</text>
                      </view>
                      <view class="pub-clue-visual">
                        <text class="pub-clue-icon">{{ card.icon }}</text>
                      </view>
                      <text class="pub-clue-excerpt">{{ card.content }}</text>
                      <view class="pub-clue-foot">
                        <text class="pub-clue-source">{{ card.subtitle }}</text>
                        <text class="pub-clue-no">{{ card.cardNo }}</text>
                      </view>
                    </view>
                  </view>
                </view>

                <view v-if="sharedPoolClues.length" class="pool-section">
                  <text class="pool-section-label">玩家公开</text>
                  <view class="clue-grid clue-grid--pool">
                    <view
                      v-for="card in sharedPoolClues"
                      :key="card.id"
                      class="game-clue-card game-clue-card--compact game-clue-card--shared"
                      @click="openClueFocus(card)"
                    >
                      <view class="game-clue-head">
                        <text class="game-clue-head-txt">{{ card.shortTitle }}</text>
                      </view>
                      <view class="game-clue-pic">
                        <text class="game-clue-pic-icon">{{ card.icon }}</text>
                      </view>
                      <text class="game-clue-desc">{{ card.content }}</text>
                      <view class="game-clue-meta">
                        <text class="game-clue-flower">✿</text>
                        <text class="game-clue-no">{{ card.cardNo }}</text>
                      </view>
                    </view>
                  </view>
                </view>

                <view v-if="!centerClues.length" class="clue-empty">
                  <text class="clue-empty-icon">📜</text>
                  <text class="clue-empty-text">线索将随教师推进环节解锁</text>
                  <text class="clue-empty-hint">点底部「线索」查看私人线索 · 点击卡池卡片可放大</text>
                </view>
              </view>

              <!-- 私人线索卡片 -->
              <view v-else class="clue-board-private">
                <text class="board-label">🔗 私人线索</text>
                <view v-if="privateClueList.length" class="clue-grid">
                  <view
                    v-for="clue in privateClueList"
                    :key="clue.key"
                    class="clue-card-wrap"
                  >
                    <view class="game-clue-card game-clue-card--private">
                      <view class="game-clue-head">
                        <text class="game-clue-head-txt">{{ clue.shortTitle }}</text>
                      </view>
                      <view class="game-clue-pic">
                        <text class="game-clue-pic-icon">{{ clue.icon }}</text>
                      </view>
                      <text class="game-clue-desc">{{ clue.content }}</text>
                      <view class="game-clue-meta">
                        <text class="game-clue-flower">✿</text>
                        <text class="game-clue-no">{{ clue.cardNo }}</text>
                      </view>
                    </view>
                    <button
                      class="clue-push-btn"
                      :class="{ pushed: isClueShared(clue.key) }"
                      :disabled="isClueShared(clue.key)"
                      @click="shareClue(clue.key)"
                    >
                      {{ isClueShared(clue.key) ? '已在公开卡池' : '推送到公开卡池' }}
                    </button>
                  </view>
                </view>
                <view v-else class="clue-empty">
                  <text class="clue-empty-icon">🔒</text>
                  <text class="clue-empty-text">私人线索①将在「一轮线索」环节解锁</text>
                </view>
                <button class="board-back-btn" @click="backToPublicPool">返回公开卡池</button>
              </view>
            </scroll-view>
          </view>
        </view>

        <view class="player-col player-col--right">
          <view
            v-for="p in sidePlayers.right"
            :key="p.id"
            class="player-chip"
            :class="{ me: isMe(p) }"
          >
            <view class="avatar" :style="{ background: avatarColor(p.roleName || p.nickname) }">
              <text class="avatar-text">{{ (p.roleName || p.nickname || '?').slice(0, 1) }}</text>
            </view>
            <text class="player-name">{{ p.roleName || p.nickname }}</text>
          </view>
        </view>
      </view>

      <view class="bottom-nav">
        <view class="nav-item" @click="openCharacter">
          <view class="nav-avatar" :style="{ background: avatarColor(roleReveal?.name) }">
            <text>{{ roleReveal?.name?.slice(0, 1) }}</text>
          </view>
          <text class="nav-label">人物</text>
        </view>
        <view class="nav-item" @click="openScript">
          <text class="nav-icon">📖</text>
          <text class="nav-label">剧本</text>
        </view>
        <view class="nav-item" :class="{ active: clueView === 'private' }" @click="openPrivateClues">
          <text class="nav-icon">🔗</text>
          <text class="nav-label">线索</text>
        </view>
        <view
          class="nav-item"
          :class="{ locked: !unlocked.includes('vote') }"
          @click="openSheet('vote')"
        >
          <text class="nav-icon">🗳️</text>
          <text class="nav-label">投票</text>
        </view>
        <view class="nav-item" @click="openSheet('more')">
          <text class="nav-icon">☰</text>
          <text class="nav-label">更多</text>
        </view>
      </view>
    </view>

    <!-- 公开卡池线索放大浏览 -->
    <view v-if="focusedClue" class="clue-focus-overlay" @click="closeClueFocus">
      <view class="clue-focus-card" @click.stop>
        <button class="clue-focus-close" @click="closeClueFocus">✕</button>

        <view
          v-if="focusedClue.type === 'public'"
          class="pub-clue-card pub-clue-card--focus"
          :style="{ '--accent': focusedClue.accent }"
        >
          <view class="pub-clue-seal pub-clue-seal--lg">
            <text class="pub-clue-seal-txt">{{ focusedClue.seal }}</text>
          </view>
          <text class="pub-clue-cat">{{ focusedClue.category }}</text>
          <view class="pub-clue-title-box pub-clue-title-box--lg">
            <text class="pub-clue-title">{{ focusedClue.title }}</text>
          </view>
          <view class="pub-clue-visual pub-clue-visual--lg">
            <text class="pub-clue-icon">{{ focusedClue.icon }}</text>
          </view>
          <scroll-view scroll-y class="clue-focus-scroll">
            <text class="pub-clue-body">{{ focusedClue.content }}</text>
          </scroll-view>
          <view class="pub-clue-foot">
            <text class="pub-clue-source">{{ focusedClue.subtitle }}</text>
            <text class="pub-clue-no">{{ focusedClue.cardNo }}</text>
          </view>
        </view>

        <view v-else class="game-clue-card game-clue-card--focus" :class="'game-clue-card--' + focusedClue.type">
          <view class="game-clue-head">
            <text class="game-clue-head-txt">{{ focusedClue.shortTitle || focusedClue.title }}</text>
          </view>
          <view class="game-clue-pic">
            <text class="game-clue-pic-icon">{{ focusedClue.icon }}</text>
          </view>
          <scroll-view scroll-y class="clue-focus-scroll">
            <text class="game-clue-desc">{{ focusedClue.content }}</text>
          </scroll-view>
          <view class="game-clue-meta">
            <text class="game-clue-flower">✿</text>
            <text class="game-clue-no">{{ focusedClue.cardNo }}</text>
          </view>
        </view>

        <text class="clue-focus-hint">点击外侧关闭</text>
      </view>
    </view>

    <!-- 人物设定：长方形人物卡 -->
    <view v-if="showCharacter && roleReveal" class="char-overlay" @click="dismissCharacter">
      <view class="char-frame" @click.stop>
        <button class="char-close" @click="dismissCharacter">✕</button>
        <text class="char-label">你的角色</text>
        <view class="char-poster">
          <view class="poster-media">
            <image
              v-if="rolePosterUrl && !posterLoadFailed"
              class="char-poster-img"
              :src="rolePosterUrl"
              mode="aspectFit"
              @error="posterLoadFailed = true"
            />
            <view v-else class="poster-placeholder">
              <text class="poster-icon">🖼️</text>
              <text class="poster-hint">人物海报加载失败</text>
            </view>
          </view>
        </view>
        <view class="poster-info">
          <text class="poster-name">{{ roleReveal.name }}</text>
          <text class="poster-meta">{{ roleReveal.gender }} · {{ roleReveal.title }}</text>
        </view>
        <text class="char-footnote">闽浙赣苏区物资总站 · {{ roleReveal.title }}</text>
        <button class="btn primary char-enter" @click="dismissCharacter">进入主界面</button>
      </view>
    </view>

    <!-- 个人剧本：纵向卷轴 · 海报 → 简介 → 剧本 → 任务 → 全员简介 -->
    <view v-if="showScript && roleReveal" class="book-overlay" @click="dismissScript">
      <view class="script-book" @click.stop>
        <button class="book-close" @click="dismissScript">✕</button>
        <scroll-view scroll-y class="script-book-scroll">
          <!-- 海报 -->
          <view class="script-poster">
            <view class="poster-media">
              <image
                v-if="rolePosterUrl && !posterLoadFailed"
                class="script-poster-img"
                :src="rolePosterUrl"
                mode="aspectFit"
                @error="posterLoadFailed = true"
              />
              <view v-if="!rolePosterUrl || posterLoadFailed" class="script-poster-placeholder">
                <text class="poster-icon">🖼️</text>
                <text class="poster-hint">人物海报加载失败</text>
              </view>
            </view>
            <view class="script-poster-info">
              <text class="poster-name">{{ roleReveal.name }}</text>
              <text class="poster-meta">{{ roleReveal.gender }} · {{ roleReveal.title }}</text>
            </view>
          </view>

          <!-- 个人简介 -->
          <view class="script-block">
            <text class="block-title">人物简介 · 全员可见</text>
            <text class="block-p">{{ playerContent?.public?.publicIntro || roleReveal.publicIntro }}</text>
          </view>

          <!-- 个人剧本 -->
          <view v-if="scriptReadable && playerContent?.personalScript?.length" class="script-block">
            <text class="block-title">个人剧本 · 仅自己可见</text>
            <text
              v-for="(para, idx) in playerContent.personalScript"
              :key="`script-${idx}`"
              class="block-p block-p--para"
            >{{ para }}</text>
          </view>
          <view v-else-if="!scriptReadable" class="script-locked">
            <text>🔒 个人剧本将在「读剧本」环节解锁</text>
          </view>

          <!-- 本场任务 -->
          <view v-if="unlocked.includes('secret') && playerContent?.secretTasks?.length" class="script-block">
            <text class="block-title">本场任务</text>
            <view v-for="(task, idx) in playerContent.secretTasks" :key="`task-${idx}`" class="task-item">
              <text class="task-no">{{ idx + 1 }}</text>
              <text class="task-text">{{ task }}</text>
            </view>
          </view>
          <view v-else-if="!unlocked.includes('secret')" class="script-locked">
            <text>🔒 本场任务将在「读剧本」环节解锁</text>
          </view>

          <!-- 全员简介 -->
          <view v-if="unlocked.includes('allRoles') && allRolesList.length" class="script-block">
            <text class="block-title">全员简介 · 可随时查阅</text>
            <text class="block-hint">按自我介绍顺序排列，点击展开</text>
            <view
              v-for="r in allRolesList"
              :key="r.id"
              class="role-intro-card"
              :class="{ expanded: expandedRoleId === r.id, me: r.id === roleReveal.id }"
            >
              <view class="role-intro-head" @click="toggleRoleIntro(r.id)">
                <text class="role-intro-order">{{ r.introOrder }}</text>
                <view class="role-intro-meta">
                  <text class="role-intro-name">{{ r.name }} · {{ r.title }}</text>
                  <text class="role-intro-toggle">{{ expandedRoleId === r.id ? '收起' : '展开' }}</text>
                </view>
              </view>
              <text v-if="expandedRoleId === r.id" class="role-intro-body">{{ r.publicIntro }}</text>
            </view>
          </view>
        </scroll-view>
        <text class="book-tip">上下滑动阅读 · 点击外侧关闭</text>
      </view>
    </view>

    <!-- 底部弹层：投票 / 更多 -->
    <view v-if="activeSheet" class="sheet-overlay" @click="closeSheet">
      <view class="sheet-panel" @click.stop>
        <view class="sheet-head">
          <text class="sheet-title">
            {{ activeSheet === 'vote' ? '🗳️ 投票' : '更多' }}
          </text>
          <button class="sheet-close" @click="closeSheet">✕</button>
        </view>

        <view v-if="activeSheet === 'vote'" class="sheet-body sheet-body--vote">
          <text class="sheet-block-title">填写你的推理结论</text>
          <text class="sheet-muted">请根据剧本与线索，用简短文字作答；提交后教师端可实时查看。</text>
          <view
            v-for="field in playerContent?.voteForm?.fields || []"
            :key="field.key"
            class="vote-field"
          >
            <text class="vote-label">{{ field.label }}</text>
            <textarea
              v-if="field.key === 'truth'"
              :value="voteTruth"
              class="vote-input vote-textarea"
              :placeholder="votePlaceholder(field)"
              maxlength="200"
              @input="(e) => onVoteInput('truth', e)"
            />
            <textarea
              v-else
              :value="voteCulprit"
              class="vote-input vote-input-single"
              :placeholder="votePlaceholder(field)"
              maxlength="20"
              @input="(e) => onVoteInput('culprit', e)"
            />
          </view>
          <button class="btn primary sheet-btn" @click="submitVote">提交答案</button>
          <text v-if="voteSubmitted" class="sheet-tip">已提交，可修改后再次点击提交更新</text>
        </view>

        <scroll-view v-else scroll-y class="sheet-body">
          <template v-if="activeSheet === 'more'">
            <text class="sheet-p">房间号：{{ roomState?.code }}</text>
            <text class="sheet-p">当前环节：{{ phaseName }}</text>
            <text class="sheet-p">你的角色：{{ roleReveal?.name }}</text>
            <button class="btn ghost sheet-btn" @click="openCharacter">查看人物设定</button>
            <button class="btn ghost sheet-btn" @click="openPrivateClues">查看私人线索</button>
            <button type="button" class="btn ghost sheet-btn" @click="openScript">查看个人剧本</button>
            <button type="button" class="btn ghost sheet-btn" @click="leaveRoom">退出房间</button>
            <button type="button" class="btn ghost sheet-btn" @click="goBack">返回课件</button>
          </template>
        </scroll-view>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
.role-app {
  min-height: 100vh;
  background: #1a1410;
  color: #f5e6d0;
  font-family: 'Noto Sans SC', 'PingFang SC', serif;
}

/* ===== Join / Draw ===== */
.join-screen,
.draw-screen {
  min-height: 100vh;
  padding: 32rpx;
  background: linear-gradient(180deg, #2d1810, #1a1410);
}

.join-back {
  font-size: 28rpx;
  color: rgba(245, 230, 208, 0.8);
}

.join-hero {
  margin: 80rpx 0 48rpx;
  text-align: center;
}

.join-title {
  display: block;
  font-size: 44rpx;
  color: #d4a574;
  font-weight: 700;
}

.join-sub {
  display: block;
  margin-top: 12rpx;
  font-size: 26rpx;
  color: rgba(245, 230, 208, 0.5);
}

.input {
  width: 100%;
  padding: 24rpx;
  margin-bottom: 16rpx;
  border-radius: 12rpx;
  border: 1px solid rgba(212, 165, 116, 0.3);
  background: rgba(0, 0, 0, 0.35);
  color: #f5e6d0;
  font-size: 28rpx;
}

.btn {
  border: none;
  border-radius: 12rpx;
  font-weight: 700;
  font-size: 28rpx;
}

.btn.primary {
  width: 100%;
  padding: 24rpx;
  background: #8b3a3a;
  color: #fff;
}

.btn.gold {
  background: #d4a574;
  color: #2d1810;
}

.btn.ghost {
  width: 100%;
  padding: 20rpx;
  margin-top: 12rpx;
  background: rgba(255, 255, 255, 0.08);
  color: #f5e6d0;
}

.join-status,
.draw-status {
  display: block;
  margin-top: 16rpx;
  text-align: center;
  font-size: 24rpx;
  color: rgba(245, 230, 208, 0.45);
}

.join-identity,
.draw-identity {
  display: block;
  margin-top: 12rpx;
  text-align: center;
  font-size: 22rpx;
  color: rgba(212, 165, 116, 0.75);
  letter-spacing: 2rpx;
}

.join-clear {
  margin-top: 16rpx;
}

.draw-card {
  margin-top: 120rpx;
  padding: 48rpx 32rpx;
  text-align: center;
  border: 2rpx solid rgba(212, 165, 116, 0.35);
  border-radius: 24rpx;
  background: rgba(0, 0, 0, 0.25);
}

.draw-title {
  display: block;
  font-size: 40rpx;
  color: #d4a574;
  font-weight: 700;
}

.draw-room,
.draw-phase {
  display: block;
  margin-top: 12rpx;
  font-size: 26rpx;
  color: rgba(245, 230, 208, 0.55);
}

.draw-btn {
  width: 100%;
  padding: 28rpx;
  margin-top: 40rpx;
  font-size: 32rpx;
}

.draw-hint {
  display: block;
  margin-top: 16rpx;
  font-size: 24rpx;
  color: rgba(245, 230, 208, 0.4);
}

/* ===== Main table ===== */
.main-screen {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #242018;
}

.preview-badge {
  padding: 8rpx 20rpx;
  text-align: center;
  font-size: 20rpx;
  color: #d4a574;
  background: rgba(212, 165, 116, 0.12);
  border-bottom: 1px solid rgba(212, 165, 116, 0.2);
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20rpx 24rpx 12rpx;
  background: rgba(0, 0, 0, 0.45);
  border-bottom: 1px solid rgba(212, 165, 116, 0.15);
}

.script-title {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
  color: #d4a574;
}

.phase-badge {
  display: inline-block;
  margin-top: 6rpx;
  padding: 4rpx 14rpx;
  font-size: 20rpx;
  border-radius: 20rpx;
  background: rgba(139, 58, 58, 0.35);
  color: #e8c9a0;
}

.room-tag {
  font-size: 22rpx;
  color: rgba(245, 230, 208, 0.45);
}

.topbar-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4rpx;
}

.identity-tag {
  font-size: 20rpx;
  color: #d4a574;
  letter-spacing: 1rpx;
}

.table-area {
  flex: 1;
  display: flex;
  min-height: 0;
  padding: 16rpx 8rpx;
  gap: 8rpx;
}

.player-col {
  width: 88rpx;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  padding-top: 8rpx;
}

.player-chip {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;

  &.me .avatar {
    box-shadow: 0 0 0 3rpx #d4a574;
  }
}

.avatar {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2rpx solid rgba(212, 165, 116, 0.4);
}

.avatar-text {
  font-size: 26rpx;
  font-weight: 700;
  color: #fff;
}

.player-name {
  font-size: 18rpx;
  color: rgba(245, 230, 208, 0.65);
  text-align: center;
  line-height: 1.2;
  max-width: 80rpx;
  word-break: break-all;
}

.parchment {
  flex: 1;
  min-width: 0;
  border-radius: 16rpx;
  background:
    radial-gradient(ellipse at 50% 0%, rgba(255, 240, 210, 0.4), transparent 55%),
    linear-gradient(165deg, #c4a574 0%, #a8845a 18%, #8b6b42 55%, #6b4f32 100%);
  box-shadow: inset 0 0 60rpx rgba(40, 25, 10, 0.35), 0 4rpx 20rpx rgba(0, 0, 0, 0.45);
  overflow: hidden;
}

.parchment-inner {
  height: 100%;
  min-height: 520rpx;
  padding: 12rpx 10rpx 0;
  position: relative;
  display: flex;
  flex-direction: column;
}

.board-scroll {
  flex: 1;
  height: 100%;
  min-height: 480rpx;
  padding: 8rpx 6rpx 16rpx;
}

.board-label {
  display: block;
  text-align: center;
  font-size: 22rpx;
  font-weight: 700;
  color: #3d2914;
  margin-bottom: 12rpx;
  letter-spacing: 0.1em;
}

.pool-section {
  margin-bottom: 16rpx;
}

.pool-section-label {
  display: block;
  font-size: 18rpx;
  color: rgba(61, 41, 20, 0.65);
  margin-bottom: 8rpx;
  padding-left: 4rpx;
  letter-spacing: 0.08em;
}

/* ===== 公共线索卡片（苏区文书风） ===== */
.pub-clue-card {
  position: relative;
  background: linear-gradient(180deg, #fffdf8 0%, #f8f2e6 100%);
  border: 1px solid rgba(70, 50, 30, 0.22);
  border-top: 3rpx solid var(--accent, #8b3a3a);
  border-radius: 8rpx;
  box-shadow:
    0 4rpx 14rpx rgba(0, 0, 0, 0.18),
    inset 0 0 0 1rpx rgba(255, 255, 255, 0.85);
  padding: 28rpx 8rpx 8rpx;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
      repeating-linear-gradient(
        0deg,
        transparent,
        transparent 18rpx,
        rgba(139, 90, 43, 0.03) 18rpx,
        rgba(139, 90, 43, 0.03) 19rpx
      );
    pointer-events: none;
  }
}

.pub-clue-seal {
  position: absolute;
  top: 6rpx;
  right: 6rpx;
  width: 36rpx;
  height: 36rpx;
  border-radius: 50%;
  border: 2rpx solid var(--accent, #8b3a3a);
  background: rgba(139, 58, 58, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  transform: rotate(-12deg);
  z-index: 1;
}

.pub-clue-seal--lg {
  width: 64rpx;
  height: 64rpx;
  top: 12rpx;
  right: 12rpx;
}

.pub-clue-seal-txt {
  font-size: 18rpx;
  font-weight: 900;
  color: var(--accent, #8b3a3a);
  font-family: 'Noto Serif SC', 'Songti SC', serif;
}

.pub-clue-seal--lg .pub-clue-seal-txt {
  font-size: 30rpx;
}

.pub-clue-cat {
  position: relative;
  z-index: 1;
  display: inline-block;
  align-self: flex-start;
  font-size: 11rpx;
  font-weight: 700;
  color: var(--accent, #8b3a3a);
  background: color-mix(in srgb, var(--accent, #8b3a3a) 12%, transparent);
  padding: 2rpx 8rpx;
  border-radius: 3rpx;
  margin-bottom: 6rpx;
  letter-spacing: 0.05em;
}

.pub-clue-title-box {
  position: relative;
  z-index: 1;
  border: 1px solid rgba(70, 50, 30, 0.18);
  border-radius: 4rpx;
  padding: 6rpx 4rpx;
  margin-bottom: 6rpx;
  background: rgba(255, 255, 255, 0.55);
  text-align: center;
}

.pub-clue-title-box--lg {
  padding: 12rpx 10rpx;
  margin-bottom: 12rpx;
}

.pub-clue-title {
  font-size: 14rpx;
  font-weight: 800;
  color: #3d2914;
  line-height: 1.35;
}

.pub-clue-title-box--lg .pub-clue-title {
  font-size: 26rpx;
}

.pub-clue-visual {
  position: relative;
  z-index: 1;
  height: 56rpx;
  margin-bottom: 6rpx;
  border-radius: 4rpx;
  background: linear-gradient(
    145deg,
    color-mix(in srgb, var(--accent, #8b4513) 8%, #f5efe0),
    color-mix(in srgb, var(--accent, #8b4513) 18%, #ebe2d0)
  );
  border: 1px solid color-mix(in srgb, var(--accent, #8b4513) 20%, transparent);
  display: flex;
  align-items: center;
  justify-content: center;
}

.pub-clue-visual--lg {
  height: 140rpx;
  margin-bottom: 12rpx;
}

.pub-clue-icon {
  font-size: 30rpx;
  opacity: 0.85;
}

.pub-clue-visual--lg .pub-clue-icon {
  font-size: 72rpx;
}

.pub-clue-excerpt {
  position: relative;
  z-index: 1;
  flex: 1;
  font-size: 12rpx;
  line-height: 1.5;
  color: #4a3728;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.pub-clue-body {
  position: relative;
  z-index: 1;
  font-size: 22rpx;
  line-height: 1.8;
  color: #4a3728;
}

.pub-clue-foot {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-top: 6rpx;
  padding-top: 4rpx;
  border-top: 1px dashed rgba(70, 50, 30, 0.15);
}

.pub-clue-source {
  font-size: 10rpx;
  color: rgba(70, 50, 30, 0.5);
  max-width: 70%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pub-clue-no {
  font-size: 11rpx;
  font-weight: 700;
  color: var(--accent, #8b3a3a);
  opacity: 0.7;
  font-family: 'Courier New', monospace;
}

.pub-clue-card--compact {
  min-height: 178rpx;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;

  &:active {
    transform: scale(0.96);
  }
}

.pub-clue-card--focus {
  min-height: 460rpx;
  padding: 40rpx 20rpx 16rpx;

  .pub-clue-cat {
    font-size: 18rpx;
    padding: 4rpx 12rpx;
    margin-bottom: 10rpx;
  }

  .pub-clue-source {
    font-size: 18rpx;
  }

  .pub-clue-no {
    font-size: 16rpx;
  }
}

.clue-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8rpx;
}

.clue-grid--pool {
  grid-template-columns: repeat(4, 1fr);
  gap: 6rpx;
}

.game-clue-card {
  background: #faf8f4;
  border: 1px solid rgba(70, 50, 30, 0.28);
  border-radius: 6rpx;
  box-shadow:
    0 4rpx 12rpx rgba(0, 0, 0, 0.2),
    inset 0 1rpx 0 rgba(255, 255, 255, 0.9);
  padding: 8rpx 8rpx 10rpx;
  display: flex;
  flex-direction: column;
  min-height: 260rpx;
}

.game-clue-card--compact {
  min-height: 168rpx;
  padding: 6rpx 6rpx 8rpx;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;

  &:active {
    transform: scale(0.96);
  }

  .game-clue-head-txt {
    font-size: 14rpx;
  }

  .game-clue-pic {
    height: 52rpx;
    margin: 2rpx 0 4rpx;
  }

  .game-clue-pic-icon {
    font-size: 28rpx;
  }

  .game-clue-desc {
    font-size: 12rpx;
    line-height: 1.45;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .game-clue-flower,
  .game-clue-no {
    font-size: 11rpx;
  }
}

.game-clue-card--focus {
  min-height: 420rpx;
  padding: 16rpx 14rpx 14rpx;
  box-shadow:
    0 12rpx 40rpx rgba(0, 0, 0, 0.35),
    inset 0 1rpx 0 rgba(255, 255, 255, 0.9);

  .game-clue-head-txt {
    font-size: 24rpx;
  }

  .game-clue-pic {
    height: 140rpx;
    margin: 8rpx 0 12rpx;
  }

  .game-clue-pic-icon {
    font-size: 72rpx;
  }

  .game-clue-desc {
    font-size: 22rpx;
    line-height: 1.75;
  }

  .game-clue-flower {
    font-size: 18rpx;
  }

  .game-clue-no {
    font-size: 16rpx;
  }
}

.clue-focus-overlay {
  position: fixed;
  inset: 0;
  z-index: 320;
  background: rgba(10, 8, 6, 0.78);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40rpx 32rpx;
}

.clue-focus-card {
  width: 100%;
  max-width: 440px;
  position: relative;
  animation: clueZoomIn 0.22s ease-out;
}

@keyframes clueZoomIn {
  from {
    opacity: 0;
    transform: scale(0.82);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.clue-focus-close {
  position: absolute;
  top: -20rpx;
  right: 0;
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.15);
  color: #f5e6d0;
  font-size: 28rpx;
  z-index: 2;
}

.clue-focus-scroll {
  flex: 1;
  max-height: 320rpx;
  margin-bottom: 8rpx;
}

.clue-focus-hint {
  display: block;
  margin-top: 16rpx;
  text-align: center;
  font-size: 20rpx;
  color: rgba(245, 230, 208, 0.45);
}

.game-clue-card--public {
  border-top: 3rpx solid #8b5a2b;
}

.game-clue-card--shared {
  border-top: 3rpx solid #c9a227;
}

.game-clue-card--private {
  border-top: 3rpx solid #8b3a3a;
}

.game-clue-head {
  border-bottom: 1px solid rgba(70, 50, 30, 0.2);
  padding-bottom: 6rpx;
  margin-bottom: 6rpx;
  text-align: center;
}

.game-clue-head-txt {
  font-size: 17rpx;
  font-weight: 700;
  color: #3d2914;
  line-height: 1.35;
  word-break: break-all;
}

.game-clue-pic {
  height: 88rpx;
  margin: 4rpx 0 6rpx;
  background: linear-gradient(180deg, #f2ece0 0%, #e6dcc8 100%);
  border: 1px solid rgba(70, 50, 30, 0.12);
  border-radius: 4rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.game-clue-pic-icon {
  font-size: 44rpx;
  opacity: 0.75;
}

.game-clue-desc {
  flex: 1;
  font-size: 15rpx;
  line-height: 1.55;
  color: #4a3728;
  word-break: break-all;
}

.game-clue-meta {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-top: 6rpx;
}

.game-clue-flower {
  font-size: 14rpx;
  color: #8b3a3a;
  opacity: 0.55;
}

.game-clue-no {
  font-size: 13rpx;
  color: rgba(70, 50, 30, 0.45);
}

.clue-card-wrap {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.clue-push-btn {
  width: 100%;
  padding: 10rpx 6rpx;
  font-size: 16rpx;
  font-weight: 700;
  border: none;
  border-radius: 6rpx;
  background: linear-gradient(180deg, #7a4d9e, #5c3578);
  color: #fff;
  line-height: 1.3;

  &.pushed {
    background: rgba(92, 64, 51, 0.3);
    color: rgba(61, 41, 20, 0.6);
  }
}

.board-back-btn {
  display: block;
  width: 100%;
  margin-top: 16rpx;
  padding: 14rpx;
  font-size: 22rpx;
  border: none;
  border-radius: 8rpx;
  background: rgba(61, 41, 20, 0.15);
  color: #3d2914;
}

.clue-empty {
  padding: 60rpx 24rpx;
  text-align: center;
}

.clue-empty-icon {
  display: block;
  font-size: 64rpx;
  opacity: 0.5;
}

.clue-empty-text {
  display: block;
  margin-top: 16rpx;
  font-size: 26rpx;
  color: #5c4033;
}

.clue-empty-hint {
  display: block;
  margin-top: 8rpx;
  font-size: 20rpx;
  color: rgba(92, 64, 51, 0.6);
}

/* ===== Bottom nav ===== */
.bottom-nav {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  padding: 12rpx 8rpx 24rpx;
  background: rgba(0, 0, 0, 0.55);
  border-top: 1px solid rgba(212, 165, 116, 0.12);
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
  min-width: 80rpx;

  &.locked {
    opacity: 0.35;
  }

  &.active .nav-label,
  &.active .nav-icon {
    color: #d4a574;
  }

  &.active .nav-avatar {
    box-shadow: 0 0 0 3rpx #d4a574;
  }
}

.nav-avatar {
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  font-weight: 700;
  color: #fff;
  border: 2rpx solid #d4a574;
}

.nav-icon {
  font-size: 40rpx;
  line-height: 1;
}

.nav-label {
  font-size: 20rpx;
  color: rgba(245, 230, 208, 0.7);
}

/* ===== 人物设定卡 ===== */
.char-overlay {
  position: fixed;
  inset: 0;
  z-index: 300;
  background: rgba(10, 8, 6, 0.82);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32rpx;
}

.char-frame {
  width: 100%;
  max-width: 420px;
  position: relative;
  padding: 32rpx 28rpx 28rpx;
  border-radius: 12rpx;
  border: 2rpx solid rgba(139, 90, 43, 0.35);
  background:
    linear-gradient(180deg, #faf3e4 0%, #f0e2c8 55%, #e6d4b0 100%);
  box-shadow:
    0 24px 48px rgba(0, 0, 0, 0.5),
    inset 0 0 0 1rpx rgba(255, 255, 255, 0.4);
  color: #3d2914;
}

.char-close {
  position: absolute;
  top: 16rpx;
  right: 16rpx;
  width: 52rpx;
  height: 52rpx;
  border-radius: 50%;
  border: none;
  background: rgba(61, 41, 20, 0.1);
  color: #6b4423;
  font-size: 26rpx;
}

.char-label {
  display: block;
  font-size: 20rpx;
  color: #8b5a2b;
  letter-spacing: 0.25em;
  margin-bottom: 20rpx;
}

.char-footnote {
  display: block;
  margin-top: 20rpx;
  font-size: 18rpx;
  color: rgba(92, 64, 51, 0.45);
  text-align: center;
  font-style: italic;
}

.char-enter {
  width: 100%;
  margin-top: 24rpx;
  padding: 20rpx;
}

/* ===== 剧本书（纵向卷轴） ===== */
.book-overlay {
  position: fixed;
  inset: 0;
  z-index: 300;
  background: rgba(10, 8, 6, 0.82);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24rpx;
}

.script-book {
  width: 100%;
  max-width: 720px;
  max-height: 88vh;
  position: relative;
  border-radius: 20rpx;
  background: linear-gradient(180deg, #faf3e4 0%, #f0e2c8 55%, #e6d4b0 100%);
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.55);
  color: #3d2914;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.script-book-scroll {
  flex: 1;
  max-height: calc(88vh - 80rpx);
  padding: 48rpx 28rpx 24rpx;
  box-sizing: border-box;
}

.script-poster {
  margin-bottom: 28rpx;
  border-radius: 16rpx;
  overflow: hidden;
  background: rgba(61, 41, 20, 0.08);
  border: 2rpx solid rgba(139, 90, 43, 0.25);
}

.poster-media {
  height: 320rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16rpx 24rpx;
  background: #2a2018;
  box-sizing: border-box;
}

.script-poster-img,
.char-poster-img {
  width: 100%;
  height: 100%;
  display: block;
}

.char-poster {
  width: 100%;
  border-radius: 8rpx;
  overflow: hidden;
  border: 2rpx solid rgba(139, 90, 43, 0.25);
  background: #2a2018;
}

.script-poster-placeholder,
.poster-placeholder {
  width: 100%;
  height: 100%;
  min-height: 200rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
}

.script-poster-info {
  padding: 16rpx 24rpx 20rpx;
  text-align: center;
}

.block-p--para {
  display: block;
  margin-bottom: 20rpx;
  line-height: 1.75;
  text-align: justify;
  word-break: break-word;
}

.block-hint {
  display: block;
  margin: 8rpx 0 16rpx;
  font-size: 22rpx;
  color: rgba(92, 64, 51, 0.55);
}

.task-item {
  display: flex;
  gap: 12rpx;
  margin-bottom: 16rpx;
  align-items: flex-start;
}

.task-no {
  flex-shrink: 0;
  width: 36rpx;
  height: 36rpx;
  line-height: 36rpx;
  text-align: center;
  border-radius: 50%;
  background: rgba(139, 58, 58, 0.15);
  color: #8b3a3a;
  font-size: 22rpx;
  font-weight: 700;
}

.task-text {
  flex: 1;
  font-size: 26rpx;
  line-height: 1.65;
}

.role-intro-card {
  margin-bottom: 12rpx;
  border-radius: 12rpx;
  border: 1rpx solid rgba(139, 90, 43, 0.2);
  background: rgba(255, 255, 255, 0.25);
  overflow: hidden;
}

.role-intro-card.me {
  border-color: rgba(139, 58, 58, 0.35);
  background: rgba(139, 58, 58, 0.06);
}

.role-intro-head {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 16rpx 18rpx;
}

.role-intro-order {
  width: 40rpx;
  height: 40rpx;
  line-height: 40rpx;
  text-align: center;
  border-radius: 8rpx;
  background: rgba(61, 41, 20, 0.1);
  font-size: 22rpx;
  font-weight: 700;
  flex-shrink: 0;
}

.role-intro-meta {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12rpx;
}

.role-intro-name {
  font-size: 26rpx;
  font-weight: 600;
}

.role-intro-toggle {
  font-size: 22rpx;
  color: #8b5a2b;
  flex-shrink: 0;
}

.role-intro-body {
  display: block;
  padding: 0 18rpx 18rpx 70rpx;
  font-size: 24rpx;
  line-height: 1.7;
  color: rgba(61, 41, 20, 0.88);
}

.open-book {
  width: 100%;
  max-width: 920px;
  position: relative;
  filter: drop-shadow(0 24px 48px rgba(0, 0, 0, 0.55));
}

.book-close {
  position: absolute;
  top: -16rpx;
  right: 0;
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.12);
  color: #f5e6d0;
  font-size: 28rpx;
  z-index: 10;
}

.book-shell {
  display: flex;
  align-items: stretch;
  min-height: 520rpx;
  perspective: 1200px;
}

.book-edge {
  width: 14rpx;
  flex-shrink: 0;
  background: linear-gradient(180deg, #3d2914, #5c3d1e, #3d2914);
}

.book-edge--left {
  border-radius: 8rpx 0 0 8rpx;
  box-shadow: inset -4rpx 0 8rpx rgba(0, 0, 0, 0.35);
}

.book-edge--right {
  border-radius: 0 8rpx 8rpx 0;
  box-shadow: inset 4rpx 0 8rpx rgba(0, 0, 0, 0.35);
}

.book-page {
  flex: 1;
  min-width: 0;
  padding: 28rpx 24rpx 20rpx;
  position: relative;
  background:
    linear-gradient(90deg, rgba(139, 90, 43, 0.06), transparent 12%),
    linear-gradient(180deg, #faf3e4 0%, #f0e2c8 45%, #e6d4b0 100%);
  color: #3d2914;
}

.book-page--left {
  border-radius: 4rpx 0 0 4rpx;
  box-shadow: inset -12rpx 0 24rpx rgba(61, 41, 20, 0.12);
  display: flex;
  flex-direction: column;
}

.book-page--right {
  border-radius: 0 4rpx 4rpx 0;
  box-shadow: inset 12rpx 0 24rpx rgba(61, 41, 20, 0.1);
  display: flex;
  flex-direction: column;
}

.book-gutter {
  width: 20rpx;
  flex-shrink: 0;
  background: linear-gradient(90deg,
    rgba(61, 41, 20, 0.25) 0%,
    #4a3020 35%,
    #2d1f12 50%,
    #4a3020 65%,
    rgba(61, 41, 20, 0.25) 100%);
  box-shadow: 0 0 20rpx rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
}

.gutter-line {
  width: 2rpx;
  height: 80%;
  background: rgba(0, 0, 0, 0.2);
}

.page-corner {
  position: absolute;
  font-size: 20rpx;
  color: rgba(139, 90, 43, 0.35);
}

.page-corner--tl { top: 12rpx; left: 16rpx; }
.page-corner--tr { top: 12rpx; right: 16rpx; }

.book-label {
  display: block;
  width: 100%;
  text-align: left;
  font-size: 20rpx;
  color: #8b5a2b;
  letter-spacing: 0.25em;
  margin-bottom: 16rpx;
}

.poster-icon {
  font-size: 56rpx;
  opacity: 0.45;
}

.poster-hint {
  margin-top: 10rpx;
  font-size: 22rpx;
  color: rgba(92, 64, 51, 0.55);
}

.poster-info {
  margin-top: 20rpx;
  width: 100%;
}

.poster-name {
  display: block;
  font-size: 40rpx;
  font-weight: 700;
  color: #3d2914;
  line-height: 1.2;
}

.poster-meta {
  display: block;
  margin-top: 8rpx;
  font-size: 24rpx;
  color: #6b4423;
}

.page-footnote {
  margin-top: auto;
  padding-top: 20rpx;
  font-size: 18rpx;
  color: rgba(92, 64, 51, 0.45);
  font-style: italic;
}

.book-scroll {
  flex: 1;
  max-height: 420rpx;
  padding-right: 8rpx;
}

.page-num {
  display: block;
  text-align: center;
  margin-top: 8rpx;
  font-size: 18rpx;
  color: rgba(92, 64, 51, 0.4);
  letter-spacing: 0.3em;
}

.script-section {
  padding-bottom: 16rpx;
}

.section-title {
  display: block;
  font-size: 26rpx;
  font-weight: 700;
  margin-bottom: 12rpx;
  color: #5c4033;
}

.script-placeholder {
  padding: 20rpx;
  margin-bottom: 16rpx;
  border-radius: 8rpx;
  background: rgba(255, 255, 255, 0.4);
  border: 1px solid rgba(139, 90, 43, 0.18);
}

.script-placeholder-title {
  display: block;
  font-size: 24rpx;
  font-weight: 600;
  color: #6b4423;
}

.script-placeholder-desc {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  line-height: 1.7;
  color: rgba(92, 64, 51, 0.75);
}

.script-block {
  margin-bottom: 16rpx;
}

.block-title {
  display: block;
  font-size: 22rpx;
  font-weight: 700;
  color: #8b5a2b;
  margin-bottom: 6rpx;
}

.block-p {
  display: block;
  font-size: 22rpx;
  line-height: 1.75;
  color: #5c4033;
  margin-bottom: 10rpx;
}

.script-locked {
  padding: 16rpx;
  text-align: center;
  font-size: 22rpx;
  color: rgba(92, 64, 51, 0.55);
}

.book-tip {
  display: block;
  margin-top: 16rpx;
  text-align: center;
  font-size: 20rpx;
  color: rgba(245, 230, 208, 0.4);
}

@media (max-width: 640px) {
  .book-shell {
    flex-direction: column;
    min-height: auto;
  }

  .book-edge {
    display: none;
  }

  .book-gutter {
    width: 100%;
    height: 16rpx;
    background: linear-gradient(180deg,
      rgba(61, 41, 20, 0.2) 0%,
      #4a3020 50%,
      rgba(61, 41, 20, 0.2) 100%);
  }

  .gutter-line {
    width: 60%;
    height: 2rpx;
  }

  .book-page--left,
  .book-page--right {
    border-radius: 4rpx;
    box-shadow: none;
  }

  .book-page--left {
    border-bottom: 1px solid rgba(139, 90, 43, 0.15);
  }

  .book-scroll {
    max-height: 320rpx;
  }
}
.sheet-overlay {
  position: fixed;
  inset: 0;
  z-index: 250;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: flex-end;
}

.sheet-panel {
  width: 100%;
  max-height: 75vh;
  background: #2a2218;
  border-radius: 24rpx 24rpx 0 0;
  border-top: 2rpx solid rgba(212, 165, 116, 0.25);
  display: flex;
  flex-direction: column;
}

.sheet-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 28rpx;
  border-bottom: 1px solid rgba(212, 165, 116, 0.12);
}

.sheet-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #d4a574;
}

.sheet-close {
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.08);
  color: #f5e6d0;
  font-size: 28rpx;
}

.sheet-body {
  flex: 1;
  max-height: 60vh;
  padding: 24rpx 28rpx 48rpx;
}

.sheet-block {
  margin-bottom: 28rpx;
  padding: 20rpx;
  border-radius: 12rpx;
  background: rgba(0, 0, 0, 0.25);
  border-left: 4rpx solid #8b5a2b;
}

.sheet-block.clue-private {
  border-left-color: #8b3a3a;
}

.sheet-block-title {
  display: block;
  font-size: 28rpx;
  font-weight: 700;
  color: #d4a574;
  margin-bottom: 10rpx;
}

.sheet-p {
  display: block;
  font-size: 26rpx;
  line-height: 1.75;
  color: rgba(245, 230, 208, 0.75);
  margin-bottom: 12rpx;
}

.sheet-muted,
.sheet-tip {
  display: block;
  font-size: 24rpx;
  color: rgba(245, 230, 208, 0.45);
  line-height: 1.6;
  margin-bottom: 12rpx;
}

.sheet-tip {
  margin-top: 16rpx;
  color: #d4a574;
}

.vote-field {
  margin-bottom: 24rpx;
}

.vote-label {
  display: block;
  font-size: 26rpx;
  color: #d4a574;
  margin-bottom: 12rpx;
}

.vote-input {
  display: block;
  width: 100%;
  box-sizing: border-box;
  padding: 20rpx 24rpx;
  border-radius: 12rpx;
  border: 1px solid rgba(212, 165, 116, 0.25);
  background: rgba(0, 0, 0, 0.35);
  color: #f5e6d0;
  font-size: 26rpx;
  line-height: 1.5;
}

.vote-textarea {
  min-height: 160rpx;
}

.vote-input-single {
  min-height: 88rpx;
  height: 88rpx;
}

.sheet-body--vote {
  padding: 24rpx 28rpx 48rpx;
}

.sheet-btn {
  margin-top: 12rpx;
}

@media (max-width: 640px) {
  .table-area {
    padding: 12rpx 6rpx;
    gap: 4rpx;
  }

  .player-col {
    width: 64rpx;
    gap: 10rpx;
  }

  .avatar {
    width: 52rpx;
    height: 52rpx;
  }

  .avatar-text {
    font-size: 22rpx;
  }

  .player-name {
    font-size: 16rpx;
    max-width: 60rpx;
  }

  .parchment-inner {
    min-height: 420rpx;
  }

  .clue-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 6rpx;
  }

  .clue-grid--pool {
    grid-template-columns: repeat(3, 1fr);
  }

  .pub-clue-card--compact {
    min-height: 160rpx;
  }

  .pub-clue-title {
    font-size: 13rpx;
  }

  .bottom-nav {
    padding-bottom: calc(12rpx + env(safe-area-inset-bottom));
  }
}
</style>
