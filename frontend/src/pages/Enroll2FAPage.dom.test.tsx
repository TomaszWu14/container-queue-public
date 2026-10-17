// @vitest-environment jsdom
// US-031 (TEST-007): administrator bez 2FA — ekran włączania 2FA: sekret z serwera, kod przycięty
// trafia razem z sekretem do /enable, kody zapasowe pokazane przed przejściem do panelu;
// błąd serwera widoczny i nie przepuszcza dalej; wylogowanie zawsze dostępne.
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'

const { post } = vi.hoisted(() => ({ post: vi.fn() }))
vi.mock('../api', () => ({ api: { post }, errorMessage: (e: unknown) => (e as Error).message }))
vi.mock('qrcode', () => ({ default: { toDataURL: vi.fn().mockResolvedValue('data:image/png;base64,AA') } }))

import Enroll2FAPage from './Enroll2FAPage'

afterEach(() => { cleanup(); post.mockReset() })

describe('wymuszone włączenie 2FA', () => {
  it('sekret → kod → kody zapasowe → przejście do panelu', async () => {
    post.mockResolvedValueOnce({ secret: 'SEKRET123', otpauth_url: 'otpauth://totp/x?secret=SEKRET123' })
      .mockResolvedValueOnce({ backup_codes: ['aaaa-1111', 'bbbb-2222'] })
    const onDone = vi.fn()
    render(<Enroll2FAPage onDone={onDone} onLogout={vi.fn()} />)
    fireEvent.click(screen.getByRole('button', { name: 'Włącz 2FA' }))
    expect(await screen.findByLabelText(/Kod z aplikacji/)).toBeTruthy()
    expect(screen.getAllByText(/SEKRET123/).length).toBeGreaterThan(0)
    expect(post).toHaveBeenNthCalledWith(1, '/api/auth/2fa/setup', {})

    const submit = screen.getByRole('button', { name: 'Włącz 2FA' }) as HTMLButtonElement
    expect(submit.disabled).toBe(true)
    fireEvent.change(screen.getByLabelText(/Kod z aplikacji/), { target: { value: ' 123456 ' } })
    fireEvent.click(submit)
    expect(await screen.findByText(/aaaa-1111/)).toBeTruthy()
    expect(post).toHaveBeenNthCalledWith(2, '/api/auth/2fa/enable', { secret: 'SEKRET123', code: '123456' })
    expect(onDone).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: /przejdź do panelu/ }))
    expect(onDone).toHaveBeenCalledOnce()
  })

  it('błędny kod — komunikat, bez kodów zapasowych i bez przejścia', async () => {
    post.mockResolvedValueOnce({ secret: 'S', otpauth_url: 'otpauth://totp/x' })
      .mockRejectedValueOnce(new Error('Nieprawidłowy kod'))
    const onDone = vi.fn()
    render(<Enroll2FAPage onDone={onDone} onLogout={vi.fn()} />)
    fireEvent.click(screen.getByRole('button', { name: 'Włącz 2FA' }))
    fireEvent.change(await screen.findByLabelText(/Kod z aplikacji/), { target: { value: '000000' } })
    fireEvent.click(screen.getByRole('button', { name: 'Włącz 2FA' }))
    expect(await screen.findByText('Nieprawidłowy kod')).toBeTruthy()
    expect(screen.queryByRole('button', { name: /przejdź do panelu/ })).toBeNull()
    expect(onDone).not.toHaveBeenCalled()
  })

  it('wylogowanie bez włączania 2FA', () => {
    const onLogout = vi.fn()
    render(<Enroll2FAPage onDone={vi.fn()} onLogout={onLogout} />)
    fireEvent.click(screen.getByRole('button', { name: 'Wyloguj' }))
    expect(onLogout).toHaveBeenCalledOnce()
    expect(post).not.toHaveBeenCalled()
  })
})
