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
    const host = window.location.host
    const pagePort = window.location.port || (window.location.protocol === 'https:' ? '443' : '80')
    const devFrontendPorts = new Set(['5173', '5174', '5175', '4173'])
    if (import.meta.env.DEV || devFrontendPorts.has(pagePort)) {
      // 开发态走 Vite 同源代理，避免浏览器直连 3001 失败
      return `${proto}://${host}/ws-backend`
    }
    return `${proto}://${host}`
  }
  // #endif

  return 'ws://localhost:3001'
}

export function getSharedUrl(path) {
  return `${getApiBase()}/shared/${path}`
}

/** 开发时前端 5173、后端 3001 */
export function getHealthUrl() {
  const base = getApiBase()
  if (base) return `${base}/health`

  // #ifdef H5
  if (typeof window !== 'undefined') {
    const host = window.location.host
    const pagePort = window.location.port || (window.location.protocol === 'https:' ? '443' : '80')
    const devFrontendPorts = new Set(['5173', '5174', '5175', '4173'])
    const proto = window.location.protocol === 'https:' ? 'https' : 'http'
    if (import.meta.env.DEV || devFrontendPorts.has(pagePort)) {
      return `${proto}://${host}/health`
    }
    return `${proto}://${host}/health`
  }
  // #endif

  return 'http://localhost:3001/health'
}
