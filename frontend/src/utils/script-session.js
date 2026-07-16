const HOST_KEY = 'szht_host_session'
const HOST_LOBBY_KEY = 'szht_host_lobby_session'
const PLAYER_KEY = 'szht_player_session'
const SERVER_BOOT_KEY = 'szht_server_boot'

function read(key) {
  try {
    const raw = uni.getStorageSync(key)
    if (!raw) return null
    return typeof raw === 'string' ? JSON.parse(raw) : raw
  } catch {
    return null
  }
}

function write(key, data) {
  try {
    uni.setStorageSync(key, JSON.stringify(data))
  } catch {
    /* ignore */
  }
}

function remove(key) {
  try {
    uni.removeStorageSync(key)
  } catch {
    /* ignore */
  }
}

function readSession(key) {
  try {
    if (typeof window === 'undefined' || !window.sessionStorage) return null
    const raw = window.sessionStorage.getItem(key)
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

function writeSession(key, data) {
  try {
    if (typeof window === 'undefined' || !window.sessionStorage) return
    window.sessionStorage.setItem(key, JSON.stringify(data))
  } catch {
    /* ignore */
  }
}

function removeSession(key) {
  try {
    if (typeof window === 'undefined' || !window.sessionStorage) return
    window.sessionStorage.removeItem(key)
  } catch {
    /* ignore */
  }
}

/** 开课后持久化（localStorage，刷新可恢复） */
export function loadHostSession() {
  return read(HOST_KEY)
}

export function saveHostSession({ roomCode, playerToken }) {
  if (!roomCode || !playerToken) return
  write(HOST_KEY, { roomCode, playerToken })
}

export function clearHostSession() {
  remove(HOST_KEY)
}

/** 入场阶段临时会话（sessionStorage，仅用于刷新/短断线重连） */
export function loadHostLobbySession() {
  return readSession(HOST_LOBBY_KEY)
}

export function saveHostLobbySession({ roomCode, playerToken }) {
  if (!roomCode || !playerToken) return
  writeSession(HOST_LOBBY_KEY, { roomCode, playerToken })
}

export function clearHostLobbySession() {
  removeSession(HOST_LOBBY_KEY)
}

export function clearAllHostSessions() {
  clearHostSession()
  clearHostLobbySession()
}

export function loadPlayerSession() {
  return read(PLAYER_KEY)
}

export function savePlayerSession({ roomCode, playerToken, nickname }) {
  if (!roomCode || !playerToken) return
  write(PLAYER_KEY, {
    roomCode,
    playerToken,
    nickname: nickname || '玩家',
  })
}

export function clearPlayerSession() {
  remove(PLAYER_KEY)
}

/** 后端重启后 bootId 变化，清除本机过期会话 */
export async function syncServerBootSession(getHealthUrl) {
  try {
    const res = await uni.request({ url: getHealthUrl() })
    const bootId = res.data?.bootId
    if (!bootId) return false
    const prev = uni.getStorageSync(SERVER_BOOT_KEY)
    const restarted = !!(prev && prev !== bootId)
    if (restarted) {
      clearPlayerSession()
      clearAllHostSessions()
    }
    uni.setStorageSync(SERVER_BOOT_KEY, bootId)
    return restarted
  } catch {
    return false
  }
}

/** 供学生截图保存的短身份码（token 前 8 位） */
export function formatIdentityCode(token = '') {
  if (!token) return ''
  return token.replace(/[^a-zA-Z0-9]/g, '').slice(0, 8).toUpperCase()
}

export function isRejoinRecoverableError(message = '') {
  return /身份凭证无效|房间不存在|席位已失效|房间号与身份不匹配|房间已关闭|游戏已开始/.test(message)
}
