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
    const pagePort = window.location.port || (window.location.protocol === 'https:' ? '443' : '80')
    // Vite/uni 开发时前端常在 5173，后端固定 3001（import.meta.env.DEV 在 uni 下可能为 false）
    const devFrontendPorts = new Set(['5173', '5174', '5175', '4173'])
    const port = import.meta.env.DEV || devFrontendPorts.has(pagePort) ? '3001' : pagePort
    return `${proto}://${host}:${port}`
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
    const host = window.location.hostname
    const pagePort = window.location.port || (window.location.protocol === 'https:' ? '443' : '80')
    const devFrontendPorts = new Set(['5173', '5174', '5175', '4173'])
    const port = import.meta.env.DEV || devFrontendPorts.has(pagePort) ? '3001' : pagePort
    const proto = window.location.protocol === 'https:' ? 'https' : 'http'
    return `${proto}://${host}:${port}/health`
  }
  // #endif

  return 'http://localhost:3001/health'
}
