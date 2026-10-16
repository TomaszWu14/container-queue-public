// @vitest-environment jsdom
// Ryzyko kary za przestój: każda pozycja mówi, dlaczego grozi kara i co zrobić; pusta lista = brak karty.
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

const { get } = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('../../api', () => ({ api: { get } }))

import DemurrageRiskCard, { type DemurrageRisk } from './DemurrageRiskCard'

afterEach(() => { cleanup(); get.mockReset() })

const row = (over: Partial<DemurrageRisk>): DemurrageRisk => ({ container_id: 1, container_no: 'MSKU1234565',
  deadline: '2026-10-21', planned: '2026-10-24', days_left: 5, days_over: 3, reason: 'planned_after_deadline', ...over })

const card = () => render(<MemoryRouter><DemurrageRiskCard /></MemoryRouter>)

describe('pulpit — ryzyko kary za przestój', () => {
  it('wyjaśnia powód i działanie, link do kontenera', async () => {
    get.mockResolvedValue([row({}), row({ container_id: 2, container_no: 'TGHU0000001', planned: null,
      reason: 'unplanned_near_deadline', days_left: 2, days_over: 0 })])
    card()
    expect(await screen.findByText(/Dostawa zaplanowana na 24\.10\.2026.*21\.10\.2026 — 3 dni kary/)).toBeTruthy()
    expect(screen.getByText(/za 2 dni\), a dostawa nie ma terminu/)).toBeTruthy()
    expect(screen.getByRole('link', { name: 'MSKU1234565' }).getAttribute('href')).toBe('/kontenery/1')
  })

  it('kara już biegnie, gdy termin minął bez planu', async () => {
    get.mockResolvedValue([row({ planned: null, reason: 'unplanned_near_deadline', days_left: -2, days_over: 2 })])
    card()
    expect(await screen.findByText(/kara już biegnie \(2 dni\)/)).toBeTruthy()
  })

  it('licznik pokazuje wszystkie ryzyka, lista najpilniejsze 8', async () => {
    get.mockResolvedValue(Array.from({ length: 11 }, (_, i) => row({ container_id: i + 1, container_no: `X${i}` })))
    const { container } = card()
    await screen.findByText('X0')
    expect(container.querySelector('.count-chip')?.textContent).toBe('11')
    expect(container.querySelectorAll('.risk-list li')).toHaveLength(8)
  })

  it('brak ryzyk — karta się nie pokazuje', async () => {
    get.mockResolvedValue([])
    const { container } = card()
    await new Promise(r => setTimeout(r, 0))
    expect(container.querySelector('.risk-card')).toBeNull()
  })
})
