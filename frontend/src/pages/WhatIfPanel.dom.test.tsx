// @vitest-environment jsdom
// US-062: „co jeśli statek się spóźni” — lista statków, wynik z dniami ponad limit i przesuniętymi kontenerami.
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import type { WhatIfResult } from './WhatIfPanel'

const { get } = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('../api', () => ({ api: { get }, errorMessage: (e: unknown) => String(e) }))

import WhatIfPanel from './WhatIfPanel'

afterEach(() => { cleanup(); get.mockReset() })

const result: WhatIfResult = {
  vessel: 'MSC ALFA', delay: 5,
  containers: [{ id: 3, container_no: 'MSKU1000132', warehouse: 'Magazyn Łódź', from: '2026-10-21', to: '2026-10-26' }],
  days: [
    { warehouse: 'Magazyn Łódź', day: '2026-10-21', before: 8, after: 7, limit: 7, over_before: true, over_after: false },
    { warehouse: 'Magazyn Łódź', day: '2026-10-26', before: 7, after: 8, limit: 7, over_before: false, over_after: true },
  ],
  new_overloads: 1, resolved_overloads: 1, extra_container_days: 2, rate_eur: 150, cost_eur: 300,
}

const show = () => render(<MemoryRouter><WhatIfPanel /></MemoryRouter>)

describe('Co jeśli statek się spóźni', () => {
  it('liczy wpływ opóźnienia', async () => {
    get.mockResolvedValueOnce({ vessels: ['MSC ALFA', 'MSC BETA'] }).mockResolvedValueOnce(result)
    show()
    expect(await screen.findByRole('option', { name: 'MSC BETA' })).toBeTruthy()
    fireEvent.click(screen.getByRole('button', { name: 'Policz' }))
    expect(await screen.findByText(/Statek MSC ALFA spóźniony o 5 dni: przesuniętych kontenerów 1, nowe przekroczenia limitu 1/)).toBeTruthy()
    expect(get).toHaveBeenLastCalledWith('/api/automations/what-if?vessel=MSC+ALFA&delay=5')
    expect(screen.getAllByText('ponad limit')).toHaveLength(2)
    expect(screen.getByText(/Szacowany koszt kar: ok\. 300 EUR \(2 kontenero-dni ponad limit × 150 EUR\/dzień\)/)).toBeTruthy()
    expect(document.querySelectorAll('tr.whatif-new')).toHaveLength(1)
    expect(screen.getByRole('link', { name: 'MSKU1000132' }).getAttribute('href')).toBe('/kontenery/3')
  })

  it('brak statków i błąd', async () => {
    get.mockResolvedValueOnce({ vessels: [] })
    show()
    expect(await screen.findByText('Brak statków z zaplanowanymi awizacjami.')).toBeTruthy()
    cleanup()
    get.mockRejectedValueOnce(new Error('boom'))
    show()
    expect((await screen.findByRole('alert')).textContent).toContain('boom')
  })
})
