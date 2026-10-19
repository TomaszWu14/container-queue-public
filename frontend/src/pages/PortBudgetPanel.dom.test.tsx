// @vitest-environment jsdom
// US-084: budżet kosztów — stan z ikoną i tekstem, prognoza, edycja tylko dla admina
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import type { PortBudget } from './PortBudgetPanel'

const { get, put, role } = vi.hoisted(() => ({ get: vi.fn(), put: vi.fn(), role: { value: 'admin' } }))
vi.mock('../api', () => ({ api: { get, put }, errorMessage: (e: unknown) => String(e) }))
vi.mock('../App', () => ({ useUser: () => ({ role: role.value }) }))

import PortBudgetPanel from './PortBudgetPanel'

afterEach(() => { cleanup(); get.mockReset(); put.mockReset() })

const data: PortBudget = {
  month: '2026-10', day: 10, days_in_month: 31, warn_ratio: 0.9,
  companies: [
    { company_id: 1, company: 'Acme', budget_eur: 10000, spent_eur: 4000, forecast_eur: 12400, state: 'warn', unconverted: 1 },
    { company_id: 2, company: 'Beta', budget_eur: null, spent_eur: 0, forecast_eur: 0, state: 'none', unconverted: 0 },
  ],
}

describe('Budżet kosztów transportu', () => {
  it('pokazuje stan, prognozę i zapisuje budżet (admin)', async () => {
    role.value = 'admin'
    get.mockResolvedValue(data)
    put.mockResolvedValue({})
    render(<PortBudgetPanel />)
    expect(await screen.findByText('Acme')).toBeTruthy()
    expect(screen.getByText(/uwaga — prognoza blisko budżetu/)).toBeTruthy()
    expect(screen.getByText(/1 faktur\(y\) bez kursu NBP/)).toBeTruthy()
    fireEvent.change(screen.getByLabelText('Budżet / mies. — Beta'), { target: { value: '5000,50' } })
    fireEvent.click(screen.getAllByRole('button', { name: 'Zapisz' })[1])
    await waitFor(() => expect(put).toHaveBeenCalledWith('/api/budgets/port/2', { amount_eur: 5000.5 }))
  })

  it('logistyka widzi podgląd bez edycji', async () => {
    role.value = 'logistics'
    get.mockResolvedValue(data)
    render(<PortBudgetPanel />)
    expect(await screen.findByText('Beta')).toBeTruthy()
    expect(screen.queryByRole('button', { name: 'Zapisz' })).toBeNull()
  })
})
