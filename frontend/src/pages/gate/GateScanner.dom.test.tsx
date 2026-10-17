// @vitest-environment jsdom
// Skaner bramy (pomysł 4 PO): numer wpisany albo kod QR odczytany aparatem → jeden przycisk wpuszcza auto;
// kontener spoza dzisiejszej listy nie jest wpuszczany; bez obsługi kodów w przeglądarce — jasna podpowiedź.
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import type { GateItem } from '../GatePage'
import GateScanner from './GateScanner'

const base: GateItem = { id: 7, container_no: 'MSDU0806613', truck_no: 'WGM 1234A', trailer_no: '',
  driver_name: 'Jan Kierowca', warehouse_id: 1, warehouse: 'MAG-1', notify_date: '2026-10-16', eta: null,
  status: 'AWIZOWANY', driver_arrived_at: null, checked_in_at: null }

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  Object.defineProperty(navigator, 'mediaDevices', { value: undefined, configurable: true })
})

const scanner = (items: GateItem[] = [base], onCheckin = vi.fn()) => {
  render(<GateScanner items={items} busy={0} onCheckin={onCheckin} fmtTime={() => '08:15'} />)
  return onCheckin
}

const typeNo = (no: string) => {
  fireEvent.change(screen.getByLabelText('Numer kontenera'), { target: { value: no } })
  fireEvent.click(screen.getByRole('button', { name: 'Szukaj' }))
}

describe('skaner bramy', () => {
  it('wpisany numer → karta auta i „Przyjechał — wpuść”', () => {
    const onCheckin = scanner()
    typeNo('msdu 0806613')
    expect(screen.getByText('WGM 1234A')).toBeTruthy()
    fireEvent.click(screen.getByRole('button', { name: /Przyjechał — wpuść/ }))
    expect(onCheckin).toHaveBeenCalledWith(7)
  })

  it('kontener spoza dzisiejszej listy — ostrzeżenie, bez przycisku wpuszczenia', () => {
    scanner()
    typeNo('TGHU1234567')
    expect(screen.getByText(/nie ma na dzisiejszej liście bramy/)).toBeTruthy()
    expect(screen.queryByRole('button', { name: /wpuść/ })).toBeNull()
  })

  it('już wpuszczony — godzina zamiast przycisku', () => {
    scanner([{ ...base, checked_in_at: '2026-10-16T06:15:00' }])
    typeNo('MSDU0806613')
    expect(screen.getByText('Już wpuszczony o 08:15.')).toBeTruthy()
    expect(screen.queryByRole('button', { name: /wpuść/ })).toBeNull()
  })

  it('przeglądarka bez odczytu kodów — podpowiedź: zwykły aparat albo numer', () => {
    scanner()
    fireEvent.click(screen.getByRole('button', { name: /Skanuj kod QR/ }))
    expect(screen.getByText(/zwykłym aparatem albo wpisz numer/)).toBeTruthy()
  })

  it('kod QR z aparatu → auto znalezione, aparat wyłączony', async () => {
    const stop = vi.fn()
    Object.defineProperty(navigator, 'mediaDevices', { configurable: true,
      value: { getUserMedia: vi.fn().mockResolvedValue({ getTracks: () => [{ stop }] }) } })
    vi.stubGlobal('BarcodeDetector', class {
      detect = vi.fn().mockResolvedValue([{ rawValue: 'https://kolejka.twapp.pl/kontenery/7' }])
    })
    Object.defineProperty(HTMLMediaElement.prototype, 'readyState', { configurable: true, get: () => 4 })
    HTMLMediaElement.prototype.play = vi.fn().mockResolvedValue(undefined)
    scanner()
    fireEvent.click(screen.getByRole('button', { name: /Skanuj kod QR/ }))
    expect(await screen.findByRole('button', { name: /Przyjechał — wpuść/ }, { timeout: 2000 })).toBeTruthy()
    // aparat gaśnie w sprzątaniu efektu — tuż po pokazaniu wyniku, nie w tym samym kroku
    await vi.waitFor(() => expect(stop).toHaveBeenCalled())
  })

  it('brak zgody na aparat — komunikat', async () => {
    Object.defineProperty(navigator, 'mediaDevices', { configurable: true,
      value: { getUserMedia: vi.fn().mockRejectedValue(new Error('NotAllowedError')) } })
    vi.stubGlobal('BarcodeDetector', class { detect = vi.fn() })
    scanner()
    fireEvent.click(screen.getByRole('button', { name: /Skanuj kod QR/ }))
    expect(await screen.findByText(/Brak zgody na aparat/)).toBeTruthy()
  })
})
