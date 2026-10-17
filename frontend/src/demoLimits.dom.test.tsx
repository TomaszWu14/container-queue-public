// @vitest-environment jsdom
// Ograniczenia widoków konta demo (demoLimits.ts): ukryte ekrany, zapis odcięty w przeglądarce
// bez żądania do serwera, klasa wyszarzająca formularze; zwykłe konto bez zmian.
import { afterEach, describe, expect, it, vi } from 'vitest'
import { api } from './api'
import { DEMO_HIDDEN_PATHS, demoBlocksWrite, hiddenInDemo, setDemoSession } from './demoLimits'

afterEach(() => { setDemoSession(false); vi.unstubAllGlobals() })

const demo = { is_demo: true }

describe('konto demo — ograniczenia widoków', () => {
  it('chowa dziennik zmian, importy, master data i wywołania MAG-1 tylko dla demo', () => {
    for (const p of DEMO_HIDDEN_PATHS) {
      expect(hiddenInDemo(demo, p)).toBe(true)
      expect(hiddenInDemo({ is_demo: false }, p)).toBe(false)
    }
    expect(hiddenInDemo(demo, '/master-data/materialy?x=1')).toBe(true)
    expect(hiddenInDemo(demo, '/kolejka')).toBe(false)
    expect(hiddenInDemo(null, '/dziennik-zmian')).toBe(false)
  })

  it('zapis z demo odcięty bez wysyłki; odczyt, wylogowanie i obecność przechodzą', async () => {
    const fetchMock = vi.fn(async () => new Response('{}', { status: 200, headers: { 'Content-Type': 'application/json' } }))
    vi.stubGlobal('fetch', fetchMock)
    setDemoSession(true)
    expect(document.body.classList.contains('demo-readonly')).toBe(true)
    await expect(api.post('/api/containers', {})).rejects.toMatchObject({ status: 403 })
    expect(fetchMock).not.toHaveBeenCalled()
    expect(demoBlocksWrite('/api/auth/logout', 'POST')).toBe(false)
    expect(demoBlocksWrite('/api/presence', 'POST')).toBe(false)
    await api.get('/api/containers')
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })

  it('zwykłe konto zapisuje normalnie', async () => {
    const fetchMock = vi.fn(async () => new Response('{}', { status: 200, headers: { 'Content-Type': 'application/json' } }))
    vi.stubGlobal('fetch', fetchMock)
    setDemoSession(false)
    expect(document.body.classList.contains('demo-readonly')).toBe(false)
    await api.post('/api/containers', {})
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })
})
