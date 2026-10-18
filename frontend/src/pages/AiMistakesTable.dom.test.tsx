// @vitest-environment jsdom
// Druga lista PO, pkt 8: pomyłki modelu — link do kontenera, podpowiedź vs wybór człowieka, znacznik „automat”
// przy pewności od progu; pusta lista — komunikat.
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import type { AiMistake } from './AiMistakesTable'

const { get } = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('../api', () => ({ api: { get } }))

import AiMistakesTable from './AiMistakesTable'

afterEach(() => { cleanup(); get.mockReset() })

const row = (over: Partial<AiMistake>): AiMistake => ({
  container_id: 7, container_no: 'MSKU1000132', invoice_number: 'CI-1', at: '2026-10-18T08:00:00',
  line_no: 3, raw_ref: 'SUP-0301', descr: 'Artykuł demo', suggestion: 'DEMO-010', chosen: 'DEMO-011',
  confidence: 0.95, auto: true, ...over,
})

describe('pomyłki modelu', () => {
  it('lista z linkiem i znacznikiem automatu', async () => {
    get.mockResolvedValue([row({}), row({ line_no: 4, confidence: 0.55, auto: false })])
    render(<MemoryRouter><AiMistakesTable /></MemoryRouter>)
    expect(await screen.findByText('Pomyłki modelu do przeglądu')).toBeTruthy()
    expect(get).toHaveBeenCalledWith('/api/automations/ai-quality/mistakes')
    const rows = screen.getAllByRole('row').slice(1)
    expect(rows).toHaveLength(2)
    expect(within(rows[0]).getByRole('link', { name: 'MSKU1000132' }).getAttribute('href')).toBe('/kontenery/7')
    expect(within(rows[0]).getByText('automat').getAttribute('title')).toMatch(/ustawiłby/)
    expect(within(rows[1]).queryByText('automat')).toBeNull()
    expect(within(rows[0]).getByText('DEMO-011')).toBeTruthy()
  })

  it('pusta lista', async () => {
    get.mockResolvedValue([])
    render(<MemoryRouter><AiMistakesTable /></MemoryRouter>)
    expect(await screen.findByText('Brak poprawek człowieka w ostatnim czasie.')).toBeTruthy()
  })
})
