// Powiadomienia push w przeglądarce (US-086): rejestracja service workera i subskrypcja tego urządzenia.
import { api } from '../../api'

export const SW_URL = '/push-sw.js'

export interface PushStatus { available: boolean; public_key: string | null; endpoints: string[]; kinds: string[] }

export function supported(): boolean {
  return typeof window !== 'undefined' && 'serviceWorker' in navigator && 'PushManager' in window
    && 'Notification' in window
}

function keyBytes(base64url: string): Uint8Array<ArrayBuffer> {
  const pad = '='.repeat((4 - base64url.length % 4) % 4)
  const raw = atob((base64url + pad).replace(/-/g, '+').replace(/_/g, '/'))
  const out = new Uint8Array(new ArrayBuffer(raw.length))
  for (let i = 0; i < raw.length; i++) out[i] = raw.charCodeAt(i)
  return out
}

function b64(buf: ArrayBuffer | null): string {
  if (!buf) return ''
  return btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}

export async function currentEndpoint(): Promise<string | null> {
  if (!supported()) return null
  const reg = await navigator.serviceWorker.getRegistration(SW_URL)
  const sub = await reg?.pushManager.getSubscription()
  return sub?.endpoint ?? null
}

/** Pyta o zgodę, rejestruje service worker i zapisuje subskrypcję na serwerze. false = brak zgody. */
export async function enable(publicKey: string): Promise<boolean> {
  if (await Notification.requestPermission() !== 'granted') return false
  const reg = await navigator.serviceWorker.register(SW_URL)
  await navigator.serviceWorker.ready
  const sub = await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: keyBytes(publicKey) })
  await api.post('/api/notifications/push', {
    endpoint: sub.endpoint, p256dh: b64(sub.getKey('p256dh')), auth: b64(sub.getKey('auth')),
  })
  return true
}

export async function disable(): Promise<void> {
  const reg = await navigator.serviceWorker.getRegistration(SW_URL)
  const sub = await reg?.pushManager.getSubscription()
  if (sub) {
    await api.post('/api/notifications/push/remove', { endpoint: sub.endpoint })
    await sub.unsubscribe()
  }
}
