// @vitest-environment jsdom
// US-038: panel przebiegu procesu — czas w etapach (mediana, 90. percentyl), cofnięcia,
// najczęstsze przejścia i kontenery dłużej niż zwykle z linkiem do karty kontenera.
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import type { ProcessFlow } from './ProcessFlowPanel'

const { get } = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('../api', () => ({ api: { get } }))

import ProcessFlowPanel from './ProcessFlowPanel'

afterEach(() => { cleanup(); get.mockReset() })

const stage = (status: string, count: number, median: number | null, p90: number | null) =>
  ({ status, count, median_days: median, p90_days: p90 })

const data: ProcessFlow = {
  days: 90, min_samples: 5, transitions_total: 15, backward: 1, backward_pct: 7,
  stages: [stage('W_TRANSPORCIE', 6, 10, 10), stage('W_PORCIE', 7, 4, 7.6), stage('ODPRAWA', 0, null, null)],
  top_transitions: [{ from: 'W_PORCIE', to: 'ODPRAWA', count: 7 }],
  stuck_total: 1,
  stuck: [{ id: 42, container_no: 'PRMU3000001', status: 'W_PORCIE', days_in_stage: 12, p90_days: 7.6 }],
}

const show = () => render(<MemoryRouter><ProcessFlowPanel /></MemoryRouter>)

describe('przebieg procesu', () => {
  it('etapy z pomiarami, cofnięcia, przejścia i utknięte kontenery', async () => {
    get.mockResolvedValue(data)
    show()
    expect((await screen.findByText('Zmian statusu · 90 dni')).previousElementSibling?.textContent).toBe('15')
    expect(screen.getByText('Cofnięć statusu (1) — poprawki w procesie').previousElementSibling?.textContent).toBe('7%')
    expect(get).toHaveBeenCalledWith('/api/automations/process')
    const rows = document.querySelectorAll('.proc-table')[0].querySelectorAll('tbody tr')
    expect(rows).toHaveLength(2)                          // etap bez pomiarów pominięty
    expect(rows[1].textContent).toContain('4 dni')
    expect(rows[1].textContent).toContain('7.6 dni')
    expect((rows[0].querySelector('.proc-p90') as HTMLElement).style.width).toBe('100%')
    expect(document.querySelector('.proc-transitions li')?.textContent).toBe('4 · Port docelowy → 8 · Odprawa celna: 7')
    const link = screen.getByRole('link', { name: 'PRMU3000001' })
    expect(link.getAttribute('href')).toBe('/kontenery/42')
  })

  it('pusty okres i brak utkniętych', async () => {
    get.mockResolvedValue({ ...data, transitions_total: 0, backward: 0, backward_pct: null,
      stages: [stage('W_PORCIE', 0, null, null)], top_transitions: [], stuck_total: 0, stuck: [] })
    show()
    expect(await screen.findByText('Brak zmian statusu w tym okresie.')).toBeTruthy()
  })

  it('błąd serwera — panel się nie pokazuje', async () => {
    get.mockRejectedValue(new Error('x'))
    const { container } = show()
    await Promise.resolve()
    expect(container.textContent).toBe('')
  })
})
