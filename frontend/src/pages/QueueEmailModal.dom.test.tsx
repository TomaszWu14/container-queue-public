// @vitest-environment jsdom
// US-031 (TEST-007): kolejka dnia mailem do spedytorów — lista magazynów tylko tej spółki, wysyłka
// dopiero po potwierdzeniu w oknie (anulowanie nic nie wysyła), wysłane: spółka, dzień, magazyn;
// wynik mówi o braku adresu; błąd poczty widoczny.
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'

const { get, post } = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }))
vi.mock('../api', () => ({ api: { get, post }, errorMessage: (e: unknown) => (e as Error).message }))

import QueueEmailModal from './QueueEmailModal'

afterEach(() => { cleanup(); get.mockReset(); post.mockReset() })

const sendButtons = () => screen.getAllByRole('button', { name: 'Wyślij' })

describe('kolejka dnia do spedycji', () => {
  it('magazyny spółki, potwierdzenie, wysyłka z filtrami i wynik', async () => {
    get.mockResolvedValue([{ id: 5, name: 'MAG-1' }])
    post.mockResolvedValue({
      sent: [{ forwarder: 'Spedex', email: 'awizo@spedex.pl', containers: 4 }],
      missing_email: ['Trans-B'], no_forwarder: 0,
    })
    render(<QueueEmailModal companyCode="A&B" onClose={vi.fn()} />)
    expect(get).toHaveBeenCalledWith('/api/warehouses?company_code=A%26B')
    fireEvent.change(await screen.findByLabelText('Magazyn'), { target: { value: '5' } })
    expect(screen.getByRole('option', { name: 'MAG-1' })).toBeTruthy()
    const day = screen.getByLabelText(/Awizacja/)
    fireEvent.change(day, { target: { value: '2026-10-20' } })

    fireEvent.click(sendButtons()[0])
    expect(post).not.toHaveBeenCalled()
    fireEvent.click(sendButtons()[1])
    expect(await screen.findByText(/awizo@spedex\.pl/)).toBeTruthy()
    expect(post).toHaveBeenCalledWith('/api/forwarding/queue-email',
      { company_code: 'A&B', day: '2026-10-20', warehouse_id: 5 })
    expect(screen.getByText('Brak adresu e-mail: Trans-B')).toBeTruthy()
  })

  it('anulowanie potwierdzenia nic nie wysyła; wszystkie magazyny = null', async () => {
    get.mockResolvedValue([])
    post.mockRejectedValue(new Error('Poczta nie działa'))
    render(<QueueEmailModal companyCode="ACME" onClose={vi.fn()} />)
    fireEvent.click(sendButtons()[0])
    const cancels = screen.getAllByRole('button', { name: 'Anuluj' })
    fireEvent.click(cancels[cancels.length - 1])
    expect(screen.getAllByRole('button', { name: 'Wyślij' })).toHaveLength(1)
    expect(post).not.toHaveBeenCalled()

    fireEvent.click(sendButtons()[0])
    fireEvent.click(sendButtons()[1])
    expect(await screen.findByText('Poczta nie działa')).toBeTruthy()
    expect(post.mock.calls[0][1].warehouse_id).toBeNull()
  })
})
