// Brama bez zasięgu (US-085, czwarta lista PO, pkt 3): ostatnia lista dnia zapamiętana w przeglądarce
// i kolejka „Przyjechał” wysyłana sama po powrocie sieci. Działa, dopóki aplikacja jest otwarta.
// [SEC] W pamięci przeglądarki tylko pola potrzebne przy bramie (bez nazwiska kierowcy), osobno na
// użytkownika, ważne MAX_AGE_MS; check-in po stronie serwera jest idempotentny w ciągu dnia.
import { ApiError } from '../../api'
import type { GateItem } from '../GatePage'

export const MAX_AGE_MS = 12 * 60 * 60 * 1000
const LIST = 'gate-offline-list'
const QUEUE = 'gate-offline-queue'

export interface Pending { id: number; at: string; user: number }
interface Saved { user: number; key: string; savedAt: number; items: GateItem[] }

function read<T>(name: string, fallback: T): T {
  try { const raw = localStorage.getItem(name); return raw ? JSON.parse(raw) as T : fallback } catch { return fallback }
}
function write(name: string, value: unknown) {
  try { localStorage.setItem(name, JSON.stringify(value)) } catch { /* tryb prywatny / pełna pamięć */ }
}

export function saveList(user: number, key: string, items: GateItem[], now = Date.now()) {
  const slim = items.map(i => ({ ...i, driver_name: '' }))   // nazwisko kierowcy nie trafia na urządzenie
  write(LIST, { user, key, savedAt: now, items: slim } satisfies Saved)
}

export function loadList(user: number, key: string, now = Date.now()): { items: GateItem[]; savedAt: number } | null {
  const saved = read<Saved | null>(LIST, null)
  if (!saved || saved.user !== user || saved.key !== key || now - saved.savedAt > MAX_AGE_MS) return null
  return { items: saved.items, savedAt: saved.savedAt }
}

export function pending(user: number): Pending[] {
  return read<Pending[]>(QUEUE, []).filter(p => p.user === user)
}

export function queueCheckin(user: number, id: number, at = new Date().toISOString().slice(0, 19)) {
  const all = read<Pending[]>(QUEUE, []).filter(p => !(p.user === user && p.id === id))
  write(QUEUE, [...all, { id, at, user }])
}

/** Wysyła zaległe check-iny. Brak sieci (status 0) — zostają w kolejce; błąd serwera — wypadają i wracają jako `failed`. */
export async function flush(user: number, post: (id: number) => Promise<unknown>): Promise<{ sent: number[]; failed: number[] }> {
  const sent: number[] = []
  const failed: number[] = []
  for (const p of pending(user)) {
    try {
      await post(p.id)
      sent.push(p.id)
    } catch (err) {
      if (err instanceof ApiError && err.status === 0) break
      failed.push(p.id)
    }
  }
  const done = new Set([...sent, ...failed])
  write(QUEUE, read<Pending[]>(QUEUE, []).filter(p => !(p.user === user && done.has(p.id))))
  return { sent, failed }
}

export function isNetworkError(err: unknown): boolean {
  return err instanceof ApiError && err.status === 0
}
