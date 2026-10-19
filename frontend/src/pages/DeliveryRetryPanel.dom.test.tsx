// @vitest-environment jsdom
// US-022: panel ponowień — co czeka na ponowienie i co nie doszło; pusto → „Wszystkie wysyłki doszły.”
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import type { Deliveries } from './DeliveryRetryPanel'

const { get } = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('../api', () => ({ api: { get } }))

import DeliveryRetryPanel from './DeliveryRetryPanel'

afterEach(() => { cleanup(); get.mockReset() })

describe('Wysyłki do ponowienia', () => {
  it('lista oczekujących i nieudanych', async () => {
    const data: Deliveries = {
      pending: [{ channel: 'teams', label: 'Kontener MSKU1 w porcie', attempts: 1, error: 'HTTP 503', next_at: '2026-10-19T10:01:00' }],
      failed: [{ channel: 'email', label: 'Raport tygodniowy', attempts: 4, error: 'ConnectionRefusedError', at: '2026-10-19T09:00:00' }],
      delays_s: [60, 300, 1800],
    }
    get.mockResolvedValue(data)
    render(<DeliveryRetryPanel />)
    expect(await screen.findByText('Kontener MSKU1 w porcie')).toBeTruthy()
    expect(screen.getByText('czeka na ponowienie')).toBeTruthy()
    expect(screen.getByText('nie doszło')).toBeTruthy()
    expect(screen.getByText('HTTP 503')).toBeTruthy()
  })

  it('wszystko doszło', async () => {
    get.mockResolvedValue({ pending: [], failed: [], delays_s: [60] })
    render(<DeliveryRetryPanel />)
    expect(await screen.findByText('Wszystkie wysyłki doszły.')).toBeTruthy()
  })
})
