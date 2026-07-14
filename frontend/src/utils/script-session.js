const HOST_KEY = 'szht_host_session'
const PLAYER_KEY = 'szht_player_session'

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

/** 供学生截图保存的短身份码（token 前 8 位） */
export function formatIdentityCode(token = '') {
  if (!token) return ''
  return token.replace(/[^a-zA-Z0-9]/g, '').slice(0, 8).toUpperCase()
}

export function isRejoinRecoverableError(message = '') {
  return /身份凭证无效|房间不存在|席位已失效|房间号与身份不匹配/.test(message)
}
