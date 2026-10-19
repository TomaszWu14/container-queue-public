// @vitest-environment jsdom
// Trzecia lista PO, pkt 2: test reguły na 30 dniach — wynik, ostrzeżenie przy dużej liczbie alertów, brak alertów.
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'

const { get } = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('../api', () => ({ api: { get }, errorMessage: (e: unknown) => String(e) }))

import RuleBacktest from './RuleBacktest'

afterEach(() => { cleanup(); get.mockReset() })

describe('test reguły na 30 dniach', () => {
  it('wynik z ostrzeżeniem o hałasie', async () => {
    get.mockResolvedValue({ days: 30, alerts: 420, containers: 51, avg_per_day: 14, max_per_day: 30, per_day: [] })
    render(<RuleBacktest condition="notify_soon_status" days={2} status="ODPRAWA" />)
    fireEvent.click(screen.getByRole('button', { name: 'Sprawdź na 30 dniach' }))
    const out = await screen.findByRole('status')
    expect(out.textContent).toContain('W ostatnich 30 dniach: 420 alertów o 51 kontenerach (średnio 14 dziennie, najwięcej 30).')
    expect(out.textContent).toContain('Dużo alertów')
    expect(get).toHaveBeenCalledWith('/api/automations/rules/backtest?condition=notify_soon_status&days=2&status=ODPRAWA')
  })

  it('brak alertów', async () => {
    get.mockResolvedValue({ days: 30, alerts: 0, containers: 0, avg_per_day: 0, max_per_day: 0, per_day: [] })
    render(<RuleBacktest condition="no_driver" days={1} status={null} />)
    fireEvent.click(screen.getByRole('button', { name: 'Sprawdź na 30 dniach' }))
    expect((await screen.findByRole('status')).textContent).toBe('W ostatnich 30 dniach reguła nie wysłałaby żadnego alertu.')
  })
})
