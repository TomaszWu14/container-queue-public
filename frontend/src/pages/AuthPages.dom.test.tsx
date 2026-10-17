// @vitest-environment jsdom
// US-018 (TEST-007): reset hasła — prośba o link nie zdradza, czy konto istnieje (ten sam komunikat
// przy błędzie API), nowe hasło: min. 8 znaków i zgodne powtórzenie, link bez tokenu = błąd,
// błąd API (np. wygasły link) pokazany wprost.
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

const { post } = vi.hoisted(() => ({ post: vi.fn() }))
vi.mock('../api', () => ({ api: { post }, errorMessage: (e: unknown) => (e as Error).message }))

import { ChangePasswordPage, ForgotPasswordPage, ResetPasswordPage } from './AuthPages'

afterEach(() => { cleanup(); post.mockReset() })

const SENT = /Jeśli konto o tym adresie istnieje/

describe('zapomniane hasło', () => {
  it('wysyła e-mail i pokazuje neutralny komunikat', async () => {
    post.mockResolvedValue({})
    render(<ForgotPasswordPage />)
    fireEvent.change(screen.getByLabelText('Adres e-mail konta'), { target: { value: 'a@example.com' } })
    fireEvent.click(screen.getByRole('button', { name: 'Wyślij link' }))
    expect(await screen.findByText(SENT)).toBeTruthy()
    expect(post).toHaveBeenCalledWith('/api/auth/forgot-password', { email: 'a@example.com' })
  })

  it('błąd API — ten sam komunikat (bez zdradzania, czy konto istnieje)', async () => {
    post.mockRejectedValue(new Error('Nie ma takiego konta'))
    render(<ForgotPasswordPage />)
    fireEvent.change(screen.getByLabelText('Adres e-mail konta'), { target: { value: 'x@example.com' } })
    fireEvent.click(screen.getByRole('button', { name: 'Wyślij link' }))
    expect(await screen.findByText(SENT)).toBeTruthy()
    expect(screen.queryByText('Nie ma takiego konta')).toBeNull()
  })
})

const resetAt = (url: string) => render(<MemoryRouter initialEntries={[url]}><ResetPasswordPage /></MemoryRouter>)

const fill = (pass: string, repeat: string) => {
  fireEvent.change(screen.getByLabelText('Nowe hasło'), { target: { value: pass } })
  fireEvent.change(screen.getByLabelText('Powtórz hasło'), { target: { value: repeat } })
  fireEvent.click(screen.getByRole('button', { name: 'Ustaw hasło' }))
}

describe('ustawienie nowego hasła z linku', () => {
  it('link bez tokenu — komunikat, bez formularza', () => {
    resetAt('/reset-hasla')
    expect(screen.getByText('Nieprawidłowy lub niekompletny link resetu hasła.')).toBeTruthy()
    expect(screen.queryByLabelText('Nowe hasło')).toBeNull()
  })

  it('za krótkie i niezgodne hasło — bez wysyłki', () => {
    resetAt('/reset-hasla?token=abc')
    fill('krótkie', 'krótkie')
    expect(screen.getByText('Hasło musi mieć min. 8 znaków.')).toBeTruthy()
    fill('dlugiehaslo1', 'dlugiehaslo2')
    expect(screen.getByText('Hasła nie są takie same.')).toBeTruthy()
    expect(post).not.toHaveBeenCalled()
  })

  it('poprawne hasło — wysyła token i pokazuje sukces', async () => {
    post.mockResolvedValue({})
    resetAt('/reset-hasla?token=abc')
    fill('dlugiehaslo1', 'dlugiehaslo1')
    expect(await screen.findByText(/Hasło zostało zmienione/)).toBeTruthy()
    expect(post).toHaveBeenCalledWith('/api/auth/reset-password', { token: 'abc', password: 'dlugiehaslo1' })
  })

  it('wygasły link — błąd z API, formularz zostaje', async () => {
    post.mockRejectedValue(new Error('Link wygasł'))
    resetAt('/reset-hasla?token=abc')
    fill('dlugiehaslo1', 'dlugiehaslo1')
    expect(await screen.findByText('Link wygasł')).toBeTruthy()
    expect(screen.getByLabelText('Nowe hasło')).toBeTruthy()
  })
})

describe('wymuszona zmiana hasła', () => {
  it('po zapisie wywołuje onDone; błąd zostaje na ekranie', async () => {
    const onDone = vi.fn()
    post.mockRejectedValueOnce(new Error('Hasło zbyt popularne')).mockResolvedValueOnce({})
    render(<ChangePasswordPage onDone={onDone} />)
    fill('dlugiehaslo1', 'dlugiehaslo1')
    expect(await screen.findByText('Hasło zbyt popularne')).toBeTruthy()
    expect(onDone).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: 'Ustaw hasło' }))
    await vi.waitFor(() => expect(onDone).toHaveBeenCalled())
    expect(post).toHaveBeenLastCalledWith('/api/auth/change-password', { new_password: 'dlugiehaslo1' })
  })
})
