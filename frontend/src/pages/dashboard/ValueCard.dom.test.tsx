// @vitest-environment jsdom
// Panel „Ile to oszczędza”: liczby z /api/stats/value, założenie minut widoczne, procenty bez dzielenia przez 0.
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'

const { get } = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('../../api', () => ({ api: { get } }))

import ValueCard, { type ValueStats } from './ValueCard'

afterEach(() => { cleanup(); get.mockReset() })

const stats = (over: Partial<ValueStats> = {}): ValueStats => ({ days: 30, changes: 400, minutes_per_change: 3,
  hours_saved: 20, delivered: 10, delivered_on_time: 9, docs_in_flow: 8, docs_complete: 6, demurrage_warned: 4, ...over })

describe('pulpit — Ile to oszczędza', () => {
  it('pokazuje godziny z jawnym założeniem, odsetki i ostrzeżenia', async () => {
    get.mockResolvedValue(stats())
    render(<ValueCard />)
    expect(await screen.findByText('≈ 20 h')).toBeTruthy()
    expect(screen.getByText('400 zmian w aplikacji × 3 min (założenie)')).toBeTruthy()
    expect(screen.getByText('90%')).toBeTruthy()
    expect(screen.getByText('75%')).toBeTruthy()
    expect(screen.getByText('4')).toBeTruthy()
  })

  it('brak dostaw i odpraw — kreska zamiast dzielenia przez zero', async () => {
    get.mockResolvedValue(stats({ delivered: 0, delivered_on_time: 0, docs_in_flow: 0, docs_complete: 0 }))
    render(<ValueCard />)
    expect(await screen.findAllByText('—')).toHaveLength(2)
  })
})
