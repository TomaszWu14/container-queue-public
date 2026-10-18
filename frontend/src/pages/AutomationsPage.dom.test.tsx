// @vitest-environment jsdom
// US-032/US-033: ekran „Automatyzacje” — katalog z wyzwalaczem i akcją z tłumaczeń, stan każdego
// automatu (błąd / spóźnienie / wyłączony) i podsumowanie; filtr kategorii i „tylko wymagające uwagi”.
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import type { AutomationCatalog, AutomationItem } from './AutomationsPage'

const { get, put, post } = vi.hoisted(() => ({ get: vi.fn(), put: vi.fn(), post: vi.fn() }))
vi.mock('../api', () => ({ api: { get, put, post }, errorMessage: (e: unknown) => (e as Error).message }))

import AutomationsPage from './AutomationsPage'
import { UserContext } from '../userContext'
import type { User } from '../types'

afterEach(() => { cleanup(); get.mockReset(); put.mockReset(); post.mockReset() })

const item = (over: Partial<AutomationItem>): AutomationItem => ({
  key: 'demurrage', category: 'alerts', kind: 'schedule', status: 'ok', interval_s: 21600,
  last_run_at: null, last_ok_at: null, runs: 4, errors: 0, effects: 7,
  minutes_per_effect: 5, minutes_saved: 35, ...over,
})

const catalog: AutomationCatalog = {
  window_days: 7,
  items: [
    item({}),
    item({ key: 'customs_delay', status: 'error', errors: 1 }),
    item({ key: 'missing_docs', status: 'late' }),
    item({ key: 'mail_intake', category: 'integrations', kind: 'event', interval_s: null,
           runs: 3, errors: null, effects: null }),
    item({ key: 'congestion', category: 'integrations', status: 'off', interval_s: null, runs: 0 }),
    item({ key: 'invoice_ingest', category: 'documents', interval_s: 30 }),
  ],
  summary: { total: 6, active: 5, attention: 2, runs: 12, effects: 7, minutes_saved: 95, hours_saved: 1.6 },
}

const rows = () => screen.getAllByRole('row').slice(1)
// katalog i lista reguł (panel US-036) to osobne zapytania
const mockGet = (data: AutomationCatalog = catalog) => get.mockImplementation((url: string) => Promise.resolve(
  url.startsWith('/api/automations/rules') ? { rules: [], conditions: [], statuses: [], max_rules: 20 }
    : url.startsWith('/api/automations/ai-quality') ? null : data))
const catalogCalls = () => get.mock.calls.filter(c => c[0] === '/api/automations').length

describe('ekran Automatyzacje', () => {
  it('katalog: nazwa, wyzwalacz, akcja, stan i podsumowanie', async () => {
    mockGet()
    render(<AutomationsPage />)
    expect(await screen.findByText('Ostrzeżenie o karze za przestój')).toBeTruthy()
    expect(get).toHaveBeenCalledWith('/api/automations')
    const demurrage = within(rows()[0])
    expect(demurrage.getByText(/zostało ≤ N dni/)).toBeTruthy()
    expect(demurrage.getByText(/co 6 h/)).toBeTruthy()
    expect(demurrage.getByText('Działa')).toBeTruthy()
    expect(within(rows()[1]).getByText('Błąd').getAttribute('title')).toMatch(/Logi → Zadania/)
    expect(within(rows()[2]).getByText('Spóźniony')).toBeTruthy()
    expect(within(rows()[3]).getByText(/po zdarzeniu/)).toBeTruthy()
    expect(within(rows()[4]).getByText('Wyłączony')).toBeTruthy()
    expect(within(rows()[5]).getByText(/co 30 s/)).toBeTruthy()
    expect(screen.getByText('Wymaga uwagi').previousElementSibling?.textContent).toBe('2')
    expect(screen.getByText('Przebiegi · 7 dni')).toBeTruthy()
  })

  it('filtr kategorii i „tylko wymagające uwagi”', async () => {
    mockGet()
    render(<AutomationsPage />)
    await screen.findByText('Ostrzeżenie o karze za przestój')
    fireEvent.click(screen.getByLabelText('Tylko wymagające uwagi'))
    expect(rows().map(r => r.getAttribute('data-status'))).toEqual(['error', 'late'])
    fireEvent.click(screen.getByLabelText('Tylko wymagające uwagi'))
    fireEvent.change(screen.getByLabelText('Automat'), { target: { value: 'integrations' } })
    expect(rows()).toHaveLength(2)
    fireEvent.change(screen.getByLabelText('Automat'), { target: { value: 'communication' } })
    expect(screen.getByText('Brak automatów w tym widoku.')).toBeTruthy()
  })

  it('błąd API pokazany', async () => {
    get.mockRejectedValue(new Error('Brak uprawnień'))
    render(<AutomationsPage />)
    expect(await screen.findByText('Brak uprawnień')).toBeTruthy()
  })

  it('US-034: zaoszczędzony czas z jawnym założeniem i oszczędność w wierszu', async () => {
    mockGet()
    render(<AutomationsPage />)
    await screen.findByText('Ostrzeżenie o karze za przestój')
    expect(screen.getByText('Zaoszczędzony czas · 7 dni').previousElementSibling?.textContent).toBe('1.6 h')
    expect(screen.getByText(/założenie: minuty pracy ręcznej/)).toBeTruthy()
    const cell = within(rows()[0]).getByText('35 min')
    expect(cell.getAttribute('title')).toBe('5 min × 7')
    expect(screen.queryByRole('button', { name: 'Założenia minut' })).toBeNull()   // tylko admin
  })

  it('US-034: admin zmienia minuty — zapis i odświeżenie katalogu', async () => {
    mockGet()
    put.mockResolvedValue({})
    render(
      <UserContext.Provider value={{ user: { role: 'admin' } as User, reload: () => {} }}>
        <AutomationsPage />
      </UserContext.Provider>)
    fireEvent.click(await screen.findByRole('button', { name: 'Założenia minut' }))
    const dialog = screen.getByRole('dialog')
    fireEvent.change(within(dialog).getByLabelText('Ostrzeżenie o karze za przestój'), { target: { value: '12' } })
    fireEvent.click(within(dialog).getByRole('button', { name: 'Zapisz założenia' }))
    await vi.waitFor(() => expect(catalogCalls()).toBe(2))
    const sent = put.mock.calls[0][1].minutes
    expect([put.mock.calls[0][0], sent.demurrage, sent.mail_intake]).toEqual(['/api/automations/minutes', 12, 5])
    expect(screen.queryByRole('dialog')).toBeNull()
  })

  it('US-035: admin wysyła zdarzenie testowe — wynik, ostrzeżenie o braku podpisu, błąd odbiorcy', async () => {
    mockGet()
    post.mockResolvedValueOnce({ ok: true, status_code: 200, error: '', signed: false })
      .mockResolvedValueOnce({ ok: false, status_code: 404, error: 'HTTPStatusError' })
    render(
      <UserContext.Provider value={{ user: { role: 'admin' } as User, reload: () => {} }}>
        <AutomationsPage />
      </UserContext.Provider>)
    fireEvent.click(await screen.findByRole('button', { name: 'Wyślij zdarzenie testowe' }))
    expect((await screen.findByRole('status')).textContent).toMatch(/dotarło \(HTTP 200\).*bez podpisu HMAC/)
    expect(post).toHaveBeenCalledWith('/api/automations/test-event', {})
    await vi.waitFor(() => expect(catalogCalls()).toBe(2))   // licznik zdarzeń odświeżony
    fireEvent.click(screen.getByRole('button', { name: 'Wyślij zdarzenie testowe' }))
    await vi.waitFor(() => expect(screen.getByRole('status').textContent).toMatch(/nie przyjął zdarzenia: HTTP 404/))
  })

  it('admin wyłącza i włącza automat; chronionego nie da się wyłączyć (bez przycisku)', async () => {
    const data: AutomationCatalog = { ...catalog, items: [
      item({ can_disable: true }),
      item({ key: 'congestion', category: 'integrations', status: 'off', switched_off: true, can_disable: true }),
      item({ key: 'retention', category: 'data', can_disable: false }),
    ] }
    mockGet(data)
    put.mockResolvedValue({})
    render(
      <UserContext.Provider value={{ user: { role: 'admin' } as User, reload: () => {} }}>
        <AutomationsPage />
      </UserContext.Provider>)
    await screen.findByText('Ostrzeżenie o karze za przestój')
    fireEvent.click(screen.getByRole('button', { name: 'Wyłącz: Ostrzeżenie o karze za przestój' }))
    expect(put).toHaveBeenCalledWith('/api/automations/demurrage/enabled', { enabled: false })
    fireEvent.click(screen.getByRole('button', { name: /^Włącz: / }))
    expect(put).toHaveBeenCalledWith('/api/automations/congestion/enabled', { enabled: true })
    expect(within(rows()[1]).getByText('Wyłączony').getAttribute('title')).toMatch(/przez administratora/)
    expect(within(rows()[2]).queryByRole('button')).toBeNull()
  })

  it('bez roli admina — bez przełączników', async () => {
    mockGet({ ...catalog, items: [item({ can_disable: true })] })
    render(<AutomationsPage />)
    await screen.findByText('Ostrzeżenie o karze za przestój')
    expect(screen.queryByRole('button', { name: /^Wyłącz: / })).toBeNull()
  })
})
