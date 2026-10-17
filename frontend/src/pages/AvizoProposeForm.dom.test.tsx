// @vitest-environment jsdom
// US-031 (TEST-007): spedytor proponuje inny termin z awizacji — bez daty nie wyśle; wybrany kontener,
// data, godzina i uwaga trafiają do POST …/{id}/propose; błąd serwera (np. termin poza oknem) widoczny.
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'

const { post } = vi.hoisted(() => ({ post: vi.fn() }))
vi.mock('../api', () => ({ api: { post }, errorMessage: (e: unknown) => (e as Error).message }))

import { AvizoProposeForm } from './AvizoProposeForm'

afterEach(() => { cleanup(); post.mockReset() })

const items = [{ container_id: 11, container_no: 'MSCU1234565' }, { container_id: 12, container_no: 'TGHU7654321' }]

describe('propozycja innego terminu', () => {
  it('wysyła wybrany kontener z datą, godziną i uwagą', async () => {
    post.mockResolvedValue({})
    const onDone = vi.fn()
    render(<AvizoProposeForm requestId={42} items={items} onDone={onDone} />)
    const send = screen.getByRole('button', { name: 'Wyślij propozycję' }) as HTMLButtonElement
    expect(send.disabled).toBe(true)

    fireEvent.change(screen.getByLabelText('Kontenery'), { target: { value: '12' } })
    fireEvent.change(screen.getByLabelText('Nowa data'), { target: { value: '2026-10-20' } })
    fireEvent.change(screen.getByLabelText('Godzina'), { target: { value: '09:30' } })
    fireEvent.change(screen.getByLabelText('Uwagi'), { target: { value: 'rano' } })
    fireEvent.click(send)
    await vi.waitFor(() => expect(onDone).toHaveBeenCalledOnce())
    expect(post).toHaveBeenCalledWith('/api/avizo-forwarder/42/propose',
      { container_id: 12, date: '2026-10-20', time: '09:30', note: 'rano' })
  })

  it('odmowa serwera — komunikat, bez onDone', async () => {
    post.mockRejectedValue(new Error('Godzina poza oknem magazynu'))
    const onDone = vi.fn()
    render(<AvizoProposeForm requestId={42} items={items} onDone={onDone} />)
    fireEvent.change(screen.getByLabelText('Nowa data'), { target: { value: '2026-10-20' } })
    fireEvent.click(screen.getByRole('button', { name: 'Wyślij propozycję' }))
    expect(await screen.findByText('Godzina poza oknem magazynu')).toBeTruthy()
    expect(post.mock.calls[0][1].container_id).toBe(11)
    expect(onDone).not.toHaveBeenCalled()
  })
})
