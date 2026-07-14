/** 云部署时可在 .env.production 配置 VITE_API_BASE / VITE_WS_URL */

export function getApiBase() {
  return import.meta.env.VITE_API_BASE || ''
}

export function getWsUrl() {
  const envUrl = import.meta.env.VITE_WS_URL
  if (envUrl) return envUrl

  // #ifdef H5
  if (typeof window !== 'undefined') {
    const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const host = window.location.hostname
    // 开发模式：前端 5173、后端 3001，局域网访问时用同一 hostname 连后端
    const port = import.meta.env.DEV ? '3001' : (window.location.port || '80')
    return `${proto}://${host}:${port}`
  }
  // #endif

  return 'ws://localhost:3001'
}

export function getSharedUrl(path) {
  return `${getApiBase()}/shared/${path}`
}
