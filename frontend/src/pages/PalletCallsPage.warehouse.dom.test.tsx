// @vitest-environment jsdom
// Magazyn MAG-1 z kontem (rola warehouse) potwierdza wywołanie w aplikacji — bez linku z maila (2026-10-07)
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'

const { apiGet, apiPost } = vi.hoisted(() => ({ apiGet: vi.fn(), apiPost: vi.fn() }))
vi.mock('../api', () => ({
  api: { get: apiGet, post: apiPost, upload: vi.fn() },
  downloadFile: vi.fn(), errorMessage: (e: unknown) => String(e),
}))
vi.mock('../App', () => ({ useUser: () => ({ role: 'warehouse' }) }))
vi.mock('../feedback', async (orig) => ({
  ...(await orig() as object), useToast: () => ({ showToast: vi.fn() }),
}))

afterEach(() => { cleanup(); apiGet.mockReset(); apiPost.mockReset() })

const call = (status: string) => ({
  id: 5, number: 'W-5', status, needed_by: null, notes: '', created_at: '', sent_at: null, lines: [],
})

function mockCalls(status: string) {
  apiGet.mockImplementation((path: string) => {
    if (path.startsWith('/api/pallet-calls/analysis'))
      return Promise.resolve({ items: [], total: 0, fetched_at: null, discrepancies: [] })
    if (path === '/api/pallet-calls') return Promise.resolve([call(status)])
    return Promise.reject(new Error('x'))
  })
}

describe('Wywołania MAG-1 — magazyn', () => {
  it('wysłane: tylko „Przygotowane”, bez akcji logistyki', async () => {
    mockCalls('sent')
    apiPost.mockResolvedValue({})
    const { default: PalletCallsPage } = await import('./PalletCallsPage')
    render(<PalletCallsPage />)
    fireEvent.click(await screen.findByRole('button', { name: 'Przygotowane' }))
    await waitFor(() => expect(apiPost).toHaveBeenCalledWith('/api/pallet-calls/5/prepared', {}))
    expect(screen.queryByRole('button', { name: 'Przywieziono' })).toBeNull()
    expect(screen.queryByRole('button', { name: 'Potwierdź' })).toBeNull()
  })

  it('przygotowane: „Wysłane z MAG-1”', async () => {
    mockCalls('przygotowane')
    apiPost.mockResolvedValue({})
    const { default: PalletCallsPage } = await import('./PalletCallsPage')
    render(<PalletCallsPage />)
    expect(await screen.findAllByText('Przygotowane w MAG-1')).toBeTruthy()
    fireEvent.click(screen.getByRole('button', { name: 'Wysłane z MAG-1' }))
    await waitFor(() => expect(apiPost).toHaveBeenCalledWith('/api/pallet-calls/5/shipped', {}))
  })
})
