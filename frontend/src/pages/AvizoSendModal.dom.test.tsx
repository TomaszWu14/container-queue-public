// @vitest-environment jsdom
// US-031 (TEST-007): wysyłka do awizacji idzie do firm zewnętrznych — podgląd pogrupowany po spedytorze
// (także „bez spedytora”), wysyłane są dokładnie zaznaczone kontenery z uwagą i opcją magazynu;
// wynik mówi wprost o braku adresu i kontenerach bez spedytora; błąd nie woła onDone.
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import type { Container } from '../types'

const { post } = vi.hoisted(() => ({ post: vi.fn() }))
vi.mock('../api', () => ({ api: { post }, errorMessage: (e: unknown) => (e as Error).message }))

import AvizoSendModal from './AvizoSendModal'

afterEach(() => { cleanup(); post.mockReset() })

const containers = [
  { id: 1, container_no: 'MSCU1234565', forwarder_name: 'Spedex' },
  { id: 2, container_no: 'TGHU7654321', forwarder_name: 'Spedex' },
  { id: 3, container_no: 'CSQU3054383', forwarder_name: null },
] as unknown as Container[]

describe('wysyłka do awizacji', () => {
  it('podgląd po spedytorze, wysyłka zaznaczonych, wynik z brakami', async () => {
    post.mockResolvedValue({
      sent: [{ forwarder: 'Spedex', email: 'awizo@spedex.pl', containers: 2 }],
      warehouse_info: [{ warehouse: 'DLT', email: 'dlt@magazyn.pl', containers: 2 }],
      missing_email: ['Trans-B'],
      no_forwarder: 1,
    })
    const onDone = vi.fn()
    render(<AvizoSendModal containers={containers} onDone={onDone} onClose={vi.fn()} />)
    expect(screen.getByText('Spedex')).toBeTruthy()
    expect(screen.getByText('— bez przypisanego spedytora —')).toBeTruthy()

    fireEvent.change(screen.getByLabelText('Uwagi'), { target: { value: 'pilne' } })
    fireEvent.click(screen.getByLabelText(/Wyślij też informację/))
    fireEvent.click(screen.getByRole('button', { name: 'Wyślij (3)' }))
    expect(await screen.findByText(/awizo@spedex\.pl/)).toBeTruthy()
    expect(post).toHaveBeenCalledWith('/api/avizo/send',
      { container_ids: [1, 2, 3], note: 'pilne', send_warehouse_info: true })
    expect(onDone).toHaveBeenCalledOnce()
    expect(screen.getByText(/dlt@magazyn\.pl/)).toBeTruthy()
    expect(screen.getByText('Brak adresu e-mail: Trans-B')).toBeTruthy()
    expect(screen.getByText('1 kont. bez przypisanego spedytora')).toBeTruthy()
    expect(screen.queryByRole('button', { name: /^Wyślij/ })).toBeNull()
  })

  it('błąd wysyłki — komunikat, bez onDone, można ponowić', async () => {
    post.mockRejectedValue(new Error('Poczta nie działa'))
    const onDone = vi.fn()
    render(<AvizoSendModal containers={containers} onDone={onDone} onClose={vi.fn()} />)
    fireEvent.click(screen.getByRole('button', { name: 'Wyślij (3)' }))
    expect(await screen.findByText('Poczta nie działa')).toBeTruthy()
    expect(post.mock.calls[0][1].send_warehouse_info).toBe(false)
    expect(onDone).not.toHaveBeenCalled()
    expect((screen.getByRole('button', { name: 'Wyślij (3)' }) as HTMLButtonElement).disabled).toBe(false)
  })
})
