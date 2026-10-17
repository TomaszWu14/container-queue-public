// @vitest-environment jsdom
// US-032/US-033: ekran „Automatyzacje” — katalog z wyzwalaczem i akcją z tłumaczeń, stan każdego
// automatu (błąd / spóźnienie / wyłączony) i podsumowanie; filtr kategorii i „tylko wymagające uwagi”.
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import type { AutomationCatalog, AutomationItem } from './AutomationsPage'

const { get } = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('../api', () => ({ api: { get }, errorMessage: (e: unknown) => (e as Error).message }))

import AutomationsPage from './AutomationsPage'

afterEach(() => { cleanup(); get.mockReset() })

const item = (over: Partial<AutomationItem>): AutomationItem => ({
  key: 'demurrage', category: 'alerts', kind: 'schedule', status: 'ok', interval_s: 21600,
  last_run_at: null, last_ok_at: null, runs: 4, errors: 0, effects: 7, ...over,
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
  summary: { total: 6, active: 5, attention: 2, runs: 12, effects: 7 },
}

const rows = () => screen.getAllByRole('row').slice(1)

describe('ekran Automatyzacje', () => {
  it('katalog: nazwa, wyzwalacz, akcja, stan i podsumowanie', async () => {
    get.mockResolvedValue(catalog)
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
    get.mockResolvedValue(catalog)
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
})
