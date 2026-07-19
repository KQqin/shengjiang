const STORAGE_KEY = 'teaching-fullscreen'

export function isTeachingFullscreenActive() {
  if (typeof document === 'undefined') return false
  return !!(document.fullscreenElement || document.webkitFullscreenElement)
}

function getTarget() {
  if (typeof document === 'undefined') return null
  return document.documentElement
}

function syncRootClass(active) {
  if (typeof document === 'undefined') return
  document.documentElement.classList.toggle('teaching-fullscreen', active)
}

export async function enterTeachingFullscreen() {
  const target = getTarget()
  if (!target || isTeachingFullscreenActive()) {
    if (isTeachingFullscreenActive()) {
      sessionStorage.setItem(STORAGE_KEY, '1')
      syncRootClass(true)
    }
    return isTeachingFullscreenActive()
  }
  try {
    if (target.requestFullscreen) {
      await target.requestFullscreen()
    } else if (target.webkitRequestFullscreen) {
      await target.webkitRequestFullscreen()
    } else {
      return false
    }
    sessionStorage.setItem(STORAGE_KEY, '1')
    syncRootClass(true)
    return true
  } catch {
    return false
  }
}

export async function exitTeachingFullscreen() {
  if (typeof document === 'undefined') return
  try {
    if (document.exitFullscreen) {
      await document.exitFullscreen()
    } else if (document.webkitExitFullscreen) {
      await document.webkitExitFullscreen()
    }
  } catch {
    /* ignore */
  }
  sessionStorage.removeItem(STORAGE_KEY)
  syncRootClass(false)
}

export async function toggleTeachingFullscreen() {
  if (isTeachingFullscreenActive()) {
    await exitTeachingFullscreen()
    return false
  }
  return enterTeachingFullscreen()
}

export async function restoreTeachingFullscreen() {
  if (typeof document === 'undefined') return false
  if (sessionStorage.getItem(STORAGE_KEY) !== '1') return false
  if (isTeachingFullscreenActive()) {
    syncRootClass(true)
    return true
  }
  return enterTeachingFullscreen()
}

export function markTeachingFullscreen() {
  if (typeof sessionStorage === 'undefined') return
  sessionStorage.setItem(STORAGE_KEY, '1')
}

export function bindTeachingFullscreenSync(onChange) {
  if (typeof document === 'undefined') return () => {}

  const handler = () => {
    const active = isTeachingFullscreenActive()
    if (active) {
      sessionStorage.setItem(STORAGE_KEY, '1')
      syncRootClass(true)
    } else {
      sessionStorage.removeItem(STORAGE_KEY)
      syncRootClass(false)
    }
    onChange?.(active)
  }

  document.addEventListener('fullscreenchange', handler)
  document.addEventListener('webkitfullscreenchange', handler)
  handler()
  return () => {
    document.removeEventListener('fullscreenchange', handler)
    document.removeEventListener('webkitfullscreenchange', handler)
  }
}
