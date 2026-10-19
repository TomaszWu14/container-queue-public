// @vitest-environment jsdom
// US-079: karta spedytora — ranking z odsetkami i medianą; brak awizacji → komunikat
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import type { Scorecard } from './ForwarderScorecardPanel'

const { get } = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('../api', () => ({ api: { get } }))

import ForwarderScorecardPanel from './ForwarderScorecardPanel'

afterEach(() => { cleanup(); get.mockReset() })

describe('Karta spedytora', () => {
  it('ranking spedycji', async () => {
    const data: Scorecard = {
      window_days: 90, on_time_hours: 24,
      forwarders: [
        { forwarder: 'Szybka Spedycja', requests: 2, answered: 2, median_hours: 4, on_time_pct: 100,
          date_change_pct: 33.3, problem_pct: 0, rejected: 0 },
        { forwarder: 'Wolna Spedycja', requests: 3, answered: 1, median_hours: null, on_time_pct: 0,
          date_change_pct: null, problem_pct: null, rejected: 1 },
      ],
    }
    get.mockResolvedValue(data)
    render(<ForwarderScorecardPanel />)
    expect(await screen.findByText('Szybka Spedycja')).toBeTruthy()
    expect(screen.getByText('Odpowiedź w 24 h')).toBeTruthy()
    expect(screen.getByText('2 / 2')).toBeTruthy()
    expect(screen.getByText('4 h')).toBeTruthy()
    expect(screen.getAllByText('—').length).toBeGreaterThan(0)
  })

  it('brak awizacji', async () => {
    get.mockResolvedValue({ window_days: 90, on_time_hours: 24, forwarders: [] })
    render(<ForwarderScorecardPanel />)
    expect(await screen.findByText('Brak awizacji w tym okresie.')).toBeTruthy()
  })
})
