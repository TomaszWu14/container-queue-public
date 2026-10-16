// @vitest-environment jsdom
// Konto demo: profil bez zdjęcia, 2FA i sesji (konto wspólne dla gości) — tylko informacja.
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'

vi.mock('../api', () => ({
  api: { get: () => Promise.resolve([]), post: vi.fn(), del: vi.fn() },
  errorMessage: (e: unknown) => String(e),
}))
vi.mock('../App', () => ({ useUser: () => ({ id: 1, role: 'logistics', is_demo: true }) }))

import ProfilePage from './ProfilePage'

afterEach(cleanup)

describe('profil — konto demo', () => {
  it('zamiast ustawień bezpieczeństwa pokazuje informację', () => {
    render(<ProfilePage />)
    expect(screen.getByText(/konto jest wspólne dla wszystkich odwiedzających/)).toBeTruthy()
    expect(screen.queryByRole('heading', { name: /dwuetapowe|2FA/i })).toBeNull()
    expect(screen.queryByText('ta sesja')).toBeNull()
  })
})
