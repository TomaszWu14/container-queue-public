// @vitest-environment jsdom
// US-018 (TEST-007): czyszczenie kolejki to operacja masowa — najpierw podgląd (dry_run), przycisk
// pokazuje liczbę i jest wyłączony przy 0; filtry (data, zachowane statusy) trafiają do podglądu
// i do usunięcia; usunięcie wymaga confirm=true; błąd API pokazany, bez onDone.
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'

const { del } = vi.hoisted(() => ({ del: vi.fn() }))
vi.mock('../api', () => ({ api: { del }, errorMessage: (e: unknown) => (e as Error).message }))

import ClearQueueModal from './ClearQueueModal'

afterEach(() => { cleanup(); del.mockReset() })

const query = (call: number) => new URLSearchParams(del.mock.calls[call][0].split('?')[1])

describe('czyszczenie kolejki', () => {
  it('podgląd bez usuwania, potem usunięcie z confirm i tymi samymi filtrami', async () => {
    del.mockResolvedValue({ deleted: 7 })
    const onDone = vi.fn()
    render(<ClearQueueModal moduleCode="ACME" onDone={onDone} onClose={vi.fn()} />)
    expect(await screen.findByText('Do usunięcia: 7 kontenerów')).toBeTruthy()
    expect(query(0).get('dry_run')).toBe('true')
    expect(query(0).get('confirm')).toBeNull()

    fireEvent.change(screen.getByLabelText(/Usuń dostawy przed datą/), { target: { value: '2026-09-30' } })
    fireEvent.click(screen.getByLabelText('10 · Przyjęcie na magazyn'))
    await vi.waitFor(() => expect(query(del.mock.calls.length - 1).getAll('keep_statuses')).toEqual(['DOSTARCZONY']))
    del.mockResolvedValue({ deleted: 5 })
    fireEvent.change(screen.getByLabelText(/Usuń dostawy przed datą/), { target: { value: '2026-09-29' } })
    const btn = await screen.findByRole('button', { name: 'Usuń 5 kontenerów' })
    fireEvent.click(btn)
    await vi.waitFor(() => expect(onDone).toHaveBeenCalledWith(5))
    const last = query(del.mock.calls.length - 1)
    expect([last.get('confirm'), last.get('dry_run'), last.get('company_code'), last.get('before')])
      .toEqual(['true', null, 'ACME', '2026-09-29'])
    expect(last.getAll('keep_statuses')).toEqual(['DOSTARCZONY'])
  })

  it('nic do usunięcia — przycisk wyłączony', async () => {
    del.mockResolvedValue({ deleted: 0 })
    render(<ClearQueueModal moduleCode="ACME" onDone={vi.fn()} onClose={vi.fn()} />)
    expect(await screen.findByText('Do usunięcia: 0 kontenerów')).toBeTruthy()
    expect((screen.getByRole('button', { name: 'Usuń 0 kontenerów' }) as HTMLButtonElement).disabled).toBe(true)
  })

  it('błąd przy usuwaniu — komunikat, bez onDone', async () => {
    del.mockResolvedValueOnce({ deleted: 3 }).mockRejectedValueOnce(new Error('Brak uprawnień'))
    const onDone = vi.fn()
    render(<ClearQueueModal moduleCode="ACME" onDone={onDone} onClose={vi.fn()} />)
    fireEvent.click(await screen.findByRole('button', { name: 'Usuń 3 kontenerów' }))
    expect(await screen.findByText('Brak uprawnień')).toBeTruthy()
    expect(onDone).not.toHaveBeenCalled()
  })
})
