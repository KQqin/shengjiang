import { getWsUrl } from './config'

const handlers = {}
let connected = false
let reconnectTimer = null

function emit(type, data) {
  ;(handlers[type] || []).forEach((fn) => fn(data))
}

function bindSocketEvents() {
  uni.onSocketOpen(() => {
    connected = true
    emit('connected')
  })

  uni.onSocketMessage((res) => {
    let msg
    try {
      msg = JSON.parse(res.data)
    } catch {
      return
    }
    emit(msg.type, msg)
    emit('message', msg)
  })

  uni.onSocketClose(() => {
    connected = false
    emit('disconnected')
    clearTimeout(reconnectTimer)
    reconnectTimer = setTimeout(() => connect(), 3000)
  })

  uni.onSocketError(() => {
    emit('error')
  })
}

let eventsBound = false

export function connect() {
  if (!eventsBound) {
    bindSocketEvents()
    eventsBound = true
  }

  const url = getWsUrl()
  try {
    uni.closeSocket()
  } catch {
    /* ignore */
  }

  uni.connectSocket({ url })
}

export function send(type, payload = {}) {
  if (!connected) return
  uni.sendSocketMessage({
    data: JSON.stringify({ type, ...payload }),
  })
}

export function on(type, fn) {
  if (!handlers[type]) handlers[type] = []
  handlers[type].push(fn)
}

export function off(type, fn) {
  if (!handlers[type]) return
  handlers[type] = handlers[type].filter((f) => f !== fn)
}

export function isConnected() {
  return connected
}
