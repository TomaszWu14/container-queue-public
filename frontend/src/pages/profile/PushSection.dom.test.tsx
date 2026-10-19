// @vitest-environment jsdom
// US-086: przełącznik push w profilu — stan serwera, wsparcie przeglądarki, włączenie i próba
import { afterEach, describe, expect, it, vi } from 'vitest'
import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'

vi.mock('../../i18n', () => ({ useT: () => (key: string) => key }))
const { showToast, apiGet, apiPost, client } = vi.hoisted(() => ({
  showToast: vi.fn(),
  apiGet: vi.fn(),
  apiPost: vi.fn(() => Promise.resolve({ devices: 1, sent: 1 })),
  client: { supported: vi.fn(() => true), currentEndpoint: vi.fn(() => Promise.resolve(null as string | null)),
            enable: vi.fn(() => Promise.resolve(true)), disable: vi.fn(() => Promise.resolve()) },
}))
vi.mock('../../feedback', () => ({ useToast: () => ({ showToast }) }))
vi.mock('../../api', () => ({ api: { get: apiGet, post: apiPost }, errorMessage: String }))
vi.mock('./pushClient', () => client)

import PushSection from './PushSection'

afterEach(() => { cleanup(); vi.clearAllMocks() })
const status = (over = {}) => ({ available: true, public_key: 'KEY', endpoints: [], kinds: ['demurrage'], ...over })

describe('PushSection', () => {
  it('mówi wprost, gdy serwer nie ma kluczy push', async () => {
    apiGet.mockResolvedValue(status({ available: false, public_key: null }))
    await act(async () => { render(<PushSection />) })
    expect(screen.getByText('pushServerOff')).toBeTruthy()
    expect(screen.queryByText('pushTurnOn')).toBeNull()
  })

  it('włącza push na tym urządzeniu kluczem z serwera', async () => {
    apiGet.mockResolvedValue(status())
    await act(async () => { render(<PushSection />) })
    await act(async () => fireEvent.click(screen.getByText('pushTurnOn')))
    expect(client.enable).toHaveBeenCalledWith('KEY')
  })

  it('urządzenie zapisane: próba i wyłączenie', async () => {
    apiGet.mockResolvedValue(status({ endpoints: ['https://fcm.googleapis.com/x'] }))
    client.currentEndpoint.mockResolvedValue('https://fcm.googleapis.com/x')
    await act(async () => { render(<PushSection />) })
    expect(screen.getByText('pushOnHere')).toBeTruthy()
    await act(async () => fireEvent.click(screen.getByText('pushTest')))
    expect(apiPost).toHaveBeenCalledWith('/api/notifications/push/test', {})
    expect(showToast).toHaveBeenCalledWith('pushTestSent', 'success')
    await act(async () => fireEvent.click(screen.getByText('pushTurnOff')))
    expect(client.disable).toHaveBeenCalled()
  })
})
