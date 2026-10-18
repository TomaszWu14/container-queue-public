// @vitest-environment jsdom
// US-040: „Symuluj dzień” — po kliknięciu 5 kroków obiegu (mail → numer kontenera, faktura, reguły,
// zdarzenie z podpisem, zaoszczędzone minuty) z linkiem do kontenera; bez kontenerów — komunikat.
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import type { DaySimulation } from './SimulateDayPanel'

const { get } = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('../api', () => ({ api: { get }, errorMessage: (e: unknown) => String(e) }))

import SimulateDayPanel from './SimulateDayPanel'

afterEach(() => { cleanup(); get.mockReset() })

const sim: DaySimulation = {
  available: true, container_id: 7, container_no: 'MSKU1000132',
  mail: { text: 'Dzień dobry, faktura do kontenera MSKU1000132.', found: ['MSKU1000132'] },
  invoice: { invoice_number: 'CI-2026-1001', lines: 8, rules: 4, ml: 2, user: 1, open: 1 },
  rules: [{ name: 'Awizacja jutro, brak kierowcy', count: 3 }],
  event: { id: 'abc', event: 'container_in_port', signature: 'sha256=0123456789abcdef…', bytes: 210 },
  minutes: { mail: 5, invoice: 15, rules: 15 }, total_minutes: 35,
}

const show = () => render(<MemoryRouter><SimulateDayPanel /></MemoryRouter>)

describe('Symuluj dzień', () => {
  it('kroki obiegu po kliknięciu', async () => {
    get.mockResolvedValue(sim)
    show()
    fireEvent.click(screen.getByRole('button', { name: 'Uruchom symulację' }))
    expect(await screen.findByText(/odczytał z treści numer MSKU1000132/)).toBeTruthy()
    expect(get).toHaveBeenCalledWith('/api/automations/simulate-day')
    expect(document.querySelectorAll('.sim-step')).toHaveLength(5)
    expect(screen.getByText(/Faktura CI-2026-1001: 8 pozycji — reguły 4, model ML 2, człowiek 1, do decyzji 1/)).toBeTruthy()
    expect(screen.getByText(/„Awizacja jutro, brak kierowcy” — 3 kontenerów/)).toBeTruthy()
    expect(screen.getByText('sha256=0123456789abcdef…')).toBeTruthy()
    expect(screen.getByText(/Ok. 35 min pracy ręcznej/)).toBeTruthy()
    expect(screen.getByRole('link', { name: 'MSKU1000132' }).getAttribute('href')).toBe('/kontenery/7')
  })

  it('brak kontenerów i błąd serwera', async () => {
    get.mockResolvedValueOnce({ available: false })
    show()
    fireEvent.click(screen.getByRole('button', { name: 'Uruchom symulację' }))
    expect(await screen.findByText('Brak kontenerów do symulacji.')).toBeTruthy()
    get.mockRejectedValueOnce(new Error('boom'))
    fireEvent.click(screen.getByRole('button', { name: 'Uruchom symulację' }))
    expect((await screen.findByRole('alert')).textContent).toContain('boom')
  })
})
