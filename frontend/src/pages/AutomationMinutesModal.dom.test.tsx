// @vitest-environment jsdom
// US-034: okno „Założenia minut” — pokazuje bieżące minuty każdego automatu, wysyła komplet
// i pokazuje odmowę serwera (np. wartość spoza 0–240) bez zamykania okna.
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import type { AutomationItem } from './AutomationsPage'

const { put } = vi.hoisted(() => ({ put: vi.fn() }))
vi.mock('../api', () => ({ api: { put }, errorMessage: (e: unknown) => (e as Error).message }))

import AutomationMinutesModal from './AutomationMinutesModal'

afterEach(() => { cleanup(); put.mockReset() })

const items = [
  { key: 'demurrage', minutes_per_effect: 5 },
  { key: 'sms_reminders', minutes_per_effect: 3 },
] as AutomationItem[]

describe('założenia minut', () => {
  it('bieżące wartości, odmowa serwera widoczna, okno zostaje', async () => {
    put.mockRejectedValue(new Error('Minuty poza zakresem 0–240: demurrage'))
    const onSaved = vi.fn()
    render(<AutomationMinutesModal items={items} onSaved={onSaved} onClose={vi.fn()} />)
    expect((screen.getByLabelText('SMS do kierowcy') as HTMLInputElement).value).toBe('3')
    fireEvent.change(screen.getByLabelText('Ostrzeżenie o karze za przestój'), { target: { value: '999' } })
    fireEvent.click(screen.getByRole('button', { name: 'Zapisz założenia' }))
    expect(await screen.findByText(/poza zakresem/)).toBeTruthy()
    expect(put).toHaveBeenCalledWith('/api/automations/minutes', { minutes: { demurrage: 999, sms_reminders: 3 } })
    expect(onSaved).not.toHaveBeenCalled()
  })
})
