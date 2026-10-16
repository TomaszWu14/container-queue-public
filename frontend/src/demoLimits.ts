// Ograniczenia widoków kont demo (instancja portfolio, user.is_demo). Serwer egzekwuje to samo
// (backend/app/demo_limits.py, security._enforce_demo_readonly) — tu tylko chowamy miejsca, które
// i tak dałyby 403, i odcinamy zapis zanim pójdzie do serwera (natychmiastowa informacja).
import type { User } from './types'

// ekrany bez sensu na wspólnym, publicznym koncie: dziennik zmian (ruch innych gości), importy,
// wywołania DLT (linki publiczne dla partnera)
export const DEMO_HIDDEN_PATHS = ['/dziennik-zmian', '/import-sad', '/master-data', '/wywolania-dlt']

export function hiddenInDemo(user: Pick<User, 'is_demo'> | null | undefined, path: string): boolean {
  if (!user?.is_demo) return false
  const bare = path.split('?')[0]
  return DEMO_HIDDEN_PATHS.some(p => bare === p || bare.startsWith(`${p}/`))
}

export const DEMO_READONLY_MESSAGE = 'Konto demo — tylko podgląd, zmiany są wyłączone.'
// jak _DEMO_ALLOWED_WRITES w backend/app/security.py
const ALLOWED_WRITES = new Set(['/api/auth/logout', '/api/auth/refresh', '/api/presence', '/api/presence/leave'])

let demoSession = false

/** App ustawia po zalogowaniu; klasa na <body> wyszarza przyciski zapisu w formularzach. */
export function setDemoSession(on: boolean): void {
  demoSession = on
  document.body.classList.toggle('demo-readonly', on)
}

/** Zapis z konta demo — odcinany w przeglądarce, bez żądania, które i tak skończy się 403. */
export function demoBlocksWrite(path: string, method = 'GET'): boolean {
  return demoSession && !['GET', 'HEAD', 'OPTIONS'].includes(method.toUpperCase())
    && !ALLOWED_WRITES.has(path.split('?')[0])
}
