// @vitest-environment jsdom
// Pulpit analityczny: przepływ przez etapy z jednoznacznym szczytem, koła z liczbą i udziałem w legendzie,
// odprawa ukryta dla ról bez wglądu, tygodnie z wyróżnionym bieżącym; zła odpowiedź = brak sekcji.
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'

const { get } = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('../../api', () => ({ api: { get } }))

import AnalyticsBoard from './AnalyticsBoard'

afterEach(() => { cleanup(); get.mockReset() })

const STATUSES = ['ZAPOWIEDZIANY', 'W_PRODUKCJI', 'TRANSPORT_WSTEPNY', 'W_TRANSPORCIE', 'W_PORCIE', 'ODPRAWA',
  'AWIZOWANY', 'W_DOSTAWIE', 'DOSTARCZONY']
const overview = (over = {}) => ({
  stages: STATUSES.map((status, i) => ({ status, count: status === 'W_PORCIE' ? 12 : i })),
  transport: [{ key: 'morski', count: 6 }, { key: 'kolej', count: 3 }, { key: 'lotniczy', count: 1 }, { key: 'inne', count: 0 }],
  ports: [{ name: 'Gdańsk', count: 7 }, { name: null, count: 3 }],
  customs: { not_started: 5, in_progress: 3, cleared: 2 },
  weeks: [{ week: '2026-10-05', count: 4, current: false }, { week: '2026-10-12', count: 9, current: true },
    { week: '2026-10-19', count: 2, current: false }],
  ...over,
})

describe('pulpit analityczny', () => {
  it('przepływ nazywa najliczniejszy etap, koła podają liczbę i udział', async () => {
    get.mockResolvedValue(overview())
    render(<AnalyticsBoard />)
    expect(await screen.findByText(/Najwięcej teraz: Port docelowy \(12\)/)).toBeTruthy()
    const ports = screen.getByRole('region', { name: 'Porty' })
    const other = within(ports).getByText('Inne / bez portu').closest('li') as HTMLElement
    expect(other.textContent).toContain('30%')
    fireEvent.mouseEnter(within(ports).getByText('Gdańsk').closest('li') as HTMLElement)
    expect(within(ports).getAllByText('70%')).toHaveLength(2)   // legenda + środek koła (wskazany wycinek)
    expect(screen.getByRole('region', { name: 'Stan odprawy celnej' })).toBeTruthy()
    expect(screen.getByText('ten tydzień')).toBeTruthy()
    expect(screen.getByRole('listitem', { name: /Tydzień od 12\.10\.2026: 9/ })).toBeTruthy()
  })

  it('remis na szczycie — bez wskazywania „najwięcej”; odprawa ukryta, gdy rola jej nie widzi', async () => {
    get.mockResolvedValue(overview({ stages: STATUSES.map(status => ({ status, count: 5 })), customs: null }))
    render(<AnalyticsBoard />)
    await screen.findByRole('region', { name: 'Przepływ kontenerów przez proces' })
    expect(screen.queryByText(/Najwięcej teraz/)).toBeNull()
    expect(screen.queryByRole('region', { name: 'Stan odprawy celnej' })).toBeNull()
  })

  it('odpowiedź bez etapów — sekcja się nie pokazuje', async () => {
    get.mockResolvedValue({ detail: 'x' })
    const { container } = render(<AnalyticsBoard />)
    await new Promise(r => setTimeout(r, 0))
    expect(container.innerHTML).toBe('')
  })
})
