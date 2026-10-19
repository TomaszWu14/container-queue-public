// @vitest-environment jsdom
// Trzecia lista PO, pkt 4: historia zmian reguł po rozwinięciu, przywrócenie z potwierdzeniem (tylko admin).
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import type { RuleHistoryEntry } from './AutomationRulesHistory'

const { get, post } = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }))
vi.mock('../api', () => ({ api: { get, post }, errorMessage: (e: unknown) => String(e) }))

import AutomationRulesHistory from './AutomationRulesHistory'

afterEach(() => { cleanup(); vi.clearAllMocks() })

const entries: RuleHistoryEntry[] = [
  { id: 9, at: '2026-10-19T08:00:00', action: 'changed', user: 'Anna Admin', name: 'Brak kierowcy', changed: ['days', 'channels'], note: '' },
  { id: 8, at: '2026-10-18T08:00:00', action: 'added', user: 'Anna Admin', name: 'Brak kierowcy', changed: [], note: '' },
]

const open = (canEdit: boolean, onRestored = vi.fn()) => {
  get.mockResolvedValue(entries)
  render(<AutomationRulesHistory canEdit={canEdit} refreshKey={0} onRestored={onRestored} />)
  const details = screen.getByText('Historia zmian reguł').closest('details') as HTMLDetailsElement
  details.open = true
  fireEvent(details, new Event('toggle'))
  return onRestored
}

describe('historia reguł', () => {
  it('pokazuje zmiany i przywraca po potwierdzeniu', async () => {
    const onRestored = open(true)
    expect(await screen.findByText('zmieniono „Brak kierowcy”: dni, kanały')).toBeTruthy()
    expect(screen.getByText('dodano „Brak kierowcy”')).toBeTruthy()
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    post.mockResolvedValue({ rules: [] })
    fireEvent.click(screen.getAllByRole('button', { name: 'Przywróć stan sprzed tej zmiany' })[0])
    await vi.waitFor(() => expect(onRestored).toHaveBeenCalledWith({ rules: [] }))
    expect(post).toHaveBeenCalledWith('/api/automations/rules/history/9/restore', {})
  })

  it('logistyka widzi historię bez przycisku przywracania', async () => {
    open(false)
    expect(await screen.findByText('dodano „Brak kierowcy”')).toBeTruthy()
    expect(screen.queryByRole('button', { name: 'Przywróć stan sprzed tej zmiany' })).toBeNull()
  })
})
