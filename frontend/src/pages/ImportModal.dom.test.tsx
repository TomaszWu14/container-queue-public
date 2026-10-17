// @vitest-environment jsdom
// US-018 (TEST-007): import Excela — najpierw podgląd (dry_run=true, nic nie zapisuje), liczby
// nowych / już w systemie / błędnych i lista błędnych numerów; „Importuj (n)” wyłączony przy 0 nowych;
// zapis z dry_run=false wywołuje onDone i pokazuje wynik z pominiętymi; błąd API pokazany wprost.
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'

const { upload } = vi.hoisted(() => ({ upload: vi.fn() }))
vi.mock('../api', () => ({ api: { upload }, errorMessage: (e: unknown) => (e as Error).message }))

import ImportModal from './ImportModal'

afterEach(() => { cleanup(); upload.mockReset() })

const row = (container_no: string, status: string) => ({ container_no, status, note: '', supplier: 'Dostawca',
  eta: '2026-10-20', notify_date: '', warehouse: 'DLT', forwarder: '', transport: '' })
const PREVIEW = { dry_run: true, counts: { total: 3, new: 1, exists: 1, invalid: 1 },
  rows: [row('MSKU1234565', 'new'), row('TGHU0000001', 'exists'), row('ZLY123', 'invalid')],
  invalid_numbers: ['ZLY123'] }

const open = (onDone = vi.fn()) => {
  render(<ImportModal companyCode="ACME" onDone={onDone} onClose={vi.fn()} />)
  const file = new File(['x'], 'kolejka.xlsx')
  fireEvent.change(screen.getByLabelText(/Plik Excel/), { target: { files: [file] } })
  return { onDone, file }
}

describe('import Excela', () => {
  it('podgląd bez zapisu, potem import z onDone i podsumowaniem', async () => {
    upload.mockResolvedValueOnce(PREVIEW).mockResolvedValueOnce(
      { dry_run: false, counts: { total: 3, exists: 1, invalid: 1 }, imported: 1, failed: 0 })
    const { onDone, file } = open()
    fireEvent.click(screen.getByRole('button', { name: 'Podgląd' }))
    expect(await screen.findByText('MSKU1234565')).toBeTruthy()
    expect(upload).toHaveBeenLastCalledWith('/api/import/containers?company_code=ACME&dry_run=true', file)
    expect(screen.getByText(/1 nowe/)).toBeTruthy()
    expect(screen.getByText(/Błędne numery \(do poprawy\) \(1\)/)).toBeTruthy()
    expect(onDone).not.toHaveBeenCalled()

    fireEvent.click(screen.getByRole('button', { name: 'Importuj (1)' }))
    expect(await screen.findByText(/Zaimportowano/)).toBeTruthy()
    expect(upload).toHaveBeenLastCalledWith('/api/import/containers?company_code=ACME&dry_run=false', file)
    expect(onDone).toHaveBeenCalledTimes(1)
  })

  it('nic nowego — przycisk importu wyłączony', async () => {
    upload.mockResolvedValue({ ...PREVIEW, counts: { total: 1, new: 0, exists: 1 }, rows: [row('TGHU0000001', 'exists')],
      invalid_numbers: [] })
    open()
    fireEvent.click(screen.getByRole('button', { name: 'Podgląd' }))
    const btn = await screen.findByRole('button', { name: 'Importuj (0)' })
    expect((btn as HTMLButtonElement).disabled).toBe(true)
  })

  it('pominięte przy zapisie widoczne w wyniku', async () => {
    upload.mockResolvedValueOnce(PREVIEW).mockResolvedValueOnce(
      { dry_run: false, counts: { total: 3, exists: 1 }, imported: 0, failed: 1 })
    open()
    fireEvent.click(screen.getByRole('button', { name: 'Podgląd' }))
    fireEvent.click(await screen.findByRole('button', { name: 'Importuj (1)' }))
    expect(await screen.findByText('1 pominięto (błąd zapisu)')).toBeTruthy()
  })

  it('błąd odczytu pliku — komunikat, bez podglądu', async () => {
    upload.mockRejectedValue(new Error('Nie udało się odczytać pliku — wymagany format .xlsx/.xlsm.'))
    const { onDone } = open()
    fireEvent.click(screen.getByRole('button', { name: 'Podgląd' }))
    expect(await screen.findByText(/wymagany format \.xlsx/)).toBeTruthy()
    expect(screen.queryByRole('button', { name: /Importuj/ })).toBeNull()
    expect(onDone).not.toHaveBeenCalled()
  })
})
