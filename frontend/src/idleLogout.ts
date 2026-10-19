// Wylogowanie po bezczynności (ASVS 3.3.2, decyzja PO 2026-10-19; backend: session_limits.py).
// Aktywność (ruch, klawisz, dotyk, przewijanie) zapisujemy we wspólnym localStorage, żeby
// otwarte karty liczyły jeden czas. Przy aktywności co KEEPALIVE_MS odświeżamy sesję —
// serwer wygasza refresh token po oknie bezczynności, więc bez aktywności sesja i tak umiera.
import { useEffect, useRef } from 'react'
import { refreshSession } from './api'

const ACTIVITY_KEY = 'timporye_last_activity'
export const IDLE_FLAG = 'timporye_idle_logout'
const KEEPALIVE_MS = 5 * 60_000
const CHECK_MS = 30_000
const EVENTS = ['pointerdown', 'keydown', 'wheel', 'touchstart', 'scroll'] as const

function readActivity(fallback: number): number {
  try {
    const v = Number(localStorage.getItem(ACTIVITY_KEY))
    return Number.isFinite(v) && v > 0 ? Math.max(v, fallback) : fallback
  } catch { return fallback }
}

function writeActivity(at: number) {
  try { localStorage.setItem(ACTIVITY_KEY, String(at)) } catch { /* tryb prywatny */ }
}

export function markIdleLogout() {
  try { sessionStorage.setItem(IDLE_FLAG, '1') } catch { /* tryb prywatny */ }
}

/** Czy ostatnie wylogowanie było z powodu bezczynności (komunikat na logowaniu). */
export function wasIdleLogout(): boolean {
  try { return sessionStorage.getItem(IDLE_FLAG) === '1' } catch { return false }
}

export function clearIdleLogout() {
  try { sessionStorage.removeItem(IDLE_FLAG) } catch { /* tryb prywatny */ }
}

export function useIdleLogout(enabled: boolean, idleMinutes: number, onIdle: () => void) {
  const onIdleRef = useRef(onIdle)
  onIdleRef.current = onIdle
  useEffect(() => {
    if (!enabled || !(idleMinutes > 0)) return
    const idleMs = idleMinutes * 60_000
    let local = Date.now()
    let lastRefresh = Date.now()
    let lastWrite = 0
    writeActivity(local)
    const active = () => {
      const now = Date.now()
      local = now
      if (now - lastWrite > 1000) { writeActivity(now); lastWrite = now }
      if (now - lastRefresh > KEEPALIVE_MS) { lastRefresh = now; void refreshSession() }
    }
    const check = () => {
      if (Date.now() - readActivity(local) >= idleMs) {
        markIdleLogout()
        onIdleRef.current()
      }
    }
    EVENTS.forEach(e => window.addEventListener(e, active, { passive: true }))
    document.addEventListener('visibilitychange', check)
    const timer = window.setInterval(check, CHECK_MS)
    return () => {
      EVENTS.forEach(e => window.removeEventListener(e, active))
      document.removeEventListener('visibilitychange', check)
      window.clearInterval(timer)
    }
  }, [enabled, idleMinutes])
}
