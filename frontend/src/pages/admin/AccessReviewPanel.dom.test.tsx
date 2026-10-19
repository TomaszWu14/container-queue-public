// @vitest-environment jsdom
// US-076: przegląd dostępów — lista kont do decyzji, blokada po potwierdzeniu, pusto → komunikat
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import type { AccessReview } from './AccessReviewPanel'

const { get, patch } = vi.hoisted(() => ({ get: vi.fn(), patch: vi.fn() }))
vi.mock('../../api', () => ({ api: { get, patch }, errorMessage: (e: unknown) => String(e) }))
vi.mock('../../ConfirmDialog', () => ({ useConfirm: () => ({ confirm: async () => true }) }))

import AccessReviewPanel from './AccessReviewPanel'

afterEach(() => { cleanup(); get.mockReset(); patch.mockReset() })

const row = (id: number, login: string, reason: string, last_seen: string | null = null) =>
  ({ id, login, full_name: '', role: 'logistics', last_seen, reason })

describe('Przegląd dostępów', () => {
  it('pokazuje powody i blokuje nieużywane konto', async () => {
    const data: AccessReview = {
      stale_days: 90, active: 7,
      stale: [row(3, 'jan.stary', 'stale', '2026-05-01T08:00:00'), row(4, 'ewa.nowa', 'never')],
      admins_without_2fa: [row(1, 'admin', 'admin_no_2fa', '2026-10-19T08:00:00')],
      all_companies: [],
    }
    get.mockResolvedValue(data)
    patch.mockResolvedValue({})
    const changed = vi.fn()
    render(<AccessReviewPanel onChanged={changed} />)
    expect(await screen.findByText('jan.stary')).toBeTruthy()
    expect(screen.getByText('Nigdy się nie zalogował')).toBeTruthy()
    expect(screen.getByText('Administrator bez 2FA')).toBeTruthy()
    expect(screen.getAllByRole('button', { name: 'Zablokuj' })).toHaveLength(2)   // admin bez 2FA — bez blokady
    fireEvent.click(screen.getAllByRole('button', { name: 'Zablokuj' })[0])
    await waitFor(() => expect(patch).toHaveBeenCalledWith('/api/users/3', { is_active: false }))
    await waitFor(() => expect(changed).toHaveBeenCalled())
  })

  it('nic do sprawdzenia', async () => {
    get.mockResolvedValue({ stale_days: 90, active: 3, stale: [], admins_without_2fa: [], all_companies: [] })
    render(<AccessReviewPanel />)
    expect(await screen.findByText(/Nic do sprawdzenia/)).toBeTruthy()
  })
})
