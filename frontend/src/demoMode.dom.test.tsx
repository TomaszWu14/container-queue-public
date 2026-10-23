// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import DemoMode from './DemoMode'
import { UserContext } from './userContext'
import type { User } from './types'

afterEach(() => { cleanup(); vi.restoreAllMocks(); localStorage.clear() })

const jsonResponse = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })

// fetch: branding instancji portfolio + zapis treści logowania (form-urlencoded)
function stubFetch(branding: Record<string, string>, logins: string[] = []) {
  vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input)
    if (url.includes('/api/public/branding')) return jsonResponse(branding)
    if (url.includes('/api/auth/login')) { logins.push(String(init?.body)); return jsonResponse({}) }
    return jsonResponse({})
  }))
}

describe('Ekran logowania — instancja portfolio', () => {
  it('karta demo pokazuje login i hasło, „Wejdź jako demo” loguje tym kontem', async () => {
    const logins: string[] = []
    stubFetch({ demo_login: 'demo', demo_password: 'haslo-demo-123' }, logins)
    const onLogin = vi.fn()
    render(<MemoryRouter><LoginPage onLogin={onLogin} /></MemoryRouter>)

    const card = await screen.findByTestId('demo-card')
    expect(card.textContent).toContain('haslo-demo-123')
    fireEvent.click(screen.getByRole('button', { name: 'Wejdź jako demo' }))
    await waitFor(() => expect(onLogin).toHaveBeenCalled())
    expect(logins[0]).toContain('username=demo')
    expect(logins[0]).toContain('password=haslo-demo-123')
  })

  it('adres zgłoszeń zastępuje fikcyjną wizytówkę administratora', async () => {
    stubFetch({ support_email: 'autor@example.org' })
    render(<MemoryRouter><LoginPage onLogin={() => {}} /></MemoryRouter>)
    const box = await screen.findByTestId('support-box')
    expect(box.querySelector('a')).toBeNull()   // bez mailto: — adres nie leży jawnie w HTML
    expect(box.textContent).toContain('autor [at] example.org')
    expect(box.textContent).not.toContain('autor@example.org')
    expect(screen.queryByText('admin@example.com')).toBeNull()
  })

  it('link /demo (autoDemo) loguje kontem demo bez klikania — jeden raz', async () => {
    const logins: string[] = []
    stubFetch({ demo_login: 'demo', demo_password: 'haslo-demo-123' }, logins)
    const onLogin = vi.fn()
    render(<MemoryRouter><LoginPage onLogin={onLogin} autoDemo /></MemoryRouter>)
    await waitFor(() => expect(onLogin).toHaveBeenCalled())
    expect(logins).toHaveLength(1)
    expect(logins[0]).toContain('username=demo')
  })

  it('link /demo na zwykłej instancji: nic nie loguje, zwykły ekran logowania', async () => {
    const logins: string[] = []
    stubFetch({}, logins)
    const onLogin = vi.fn()
    render(<MemoryRouter><LoginPage onLogin={onLogin} autoDemo /></MemoryRouter>)
    await waitFor(() => expect(screen.getByText('admin@example.com')).toBeTruthy())
    expect(logins).toHaveLength(0)
    expect(onLogin).not.toHaveBeenCalled()
  })

  it('zwykła instancja: bez karty demo, wizytówka administratora jak dotąd', async () => {
    stubFetch({})
    render(<MemoryRouter><LoginPage onLogin={() => {}} /></MemoryRouter>)
    await waitFor(() => expect(screen.getByText('admin@example.com')).toBeTruthy())
    expect(screen.queryByTestId('demo-card')).toBeNull()
  })
})

describe('Konto demo po zalogowaniu', () => {
  it('baner + ekran powitalny przy pierwszym wejściu; „Zaczynam” zapamiętuje', async () => {
    stubFetch({ support_email: 'autor@example.org' })
    const { unmount } = render(<MemoryRouter><DemoMode /></MemoryRouter>)
    expect(screen.getByTestId('demo-banner').textContent).toContain('dane fikcyjne')
    expect(screen.getByRole('dialog').textContent).toContain('Kalendarz rozładunków')
    await waitFor(() => expect(screen.getByTestId('demo-banner').textContent).toContain('autor [at] example.org'))
    expect(screen.getByTestId('demo-banner').textContent).not.toContain('autor@example.org')
    fireEvent.click(screen.getByRole('button', { name: 'Zaczynam' }))
    expect(screen.queryByRole('dialog')).toBeNull()
    unmount()

    render(<MemoryRouter><DemoMode /></MemoryRouter>)
    expect(screen.queryByRole('dialog')).toBeNull()
    // z banera można otworzyć ponownie
    fireEvent.click(screen.getByRole('button', { name: 'Co warto zobaczyć' }))
    expect(screen.getByRole('dialog')).toBeTruthy()
  })
})

describe('Ekran powitalny demo — ekran Automatyzacje (US-032)', () => {
  const asRole = (role: string) => (
    <UserContext.Provider value={{ user: { role } as User, reload: () => {} }}>
      <MemoryRouter><DemoMode /></MemoryRouter>
    </UserContext.Provider>
  )

  it('konto demo logistyki widzi punkt „Automatyzacje”, konto spedytora nie', async () => {
    stubFetch({})
    const { unmount } = render(asRole('logistics'))
    expect(await screen.findByText(/każdy automat z wyzwalaczem/)).toBeTruthy()
    unmount()
    render(asRole('forwarder'))
    await screen.findByText('Pulpit')
    expect(screen.queryByText(/każdy automat z wyzwalaczem/)).toBeNull()
  })
})

describe('Ekran logowania — chwilowy brak połączenia', () => {
  it('ponawia branding i pokazuje przycisk demo, gdy serwer wróci', async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true })
    let calls = 0
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
      if (String(input).includes('/api/public/branding')) {
        calls += 1
        return calls < 3 ? jsonResponse({ detail: 'Za dużo żądań.' }, 429)
          : jsonResponse({ demo_login: 'demo', demo_password: 'haslo-demo-123' })
      }
      return jsonResponse({})
    }))
    render(<MemoryRouter><LoginPage onLogin={() => {}} /></MemoryRouter>)
    await vi.advanceTimersByTimeAsync(8_000)
    expect(await screen.findByTestId('demo-card')).toBeTruthy()
    expect(screen.queryByTestId('branding-failed')).toBeNull()
    vi.useRealTimers()
  })

  it('po nieudanych próbach mówi, że serwer nie odpowiada, i pozwala spróbować ponownie', async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true })
    let down = true
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
      if (String(input).includes('/api/public/branding'))
        return down ? jsonResponse({ detail: 'Bad Gateway' }, 502) : jsonResponse({ demo_login: 'demo', demo_password: 'x' })
      return jsonResponse({ status: 'ok' })
    }))
    render(<MemoryRouter><LoginPage onLogin={() => {}} /></MemoryRouter>)
    await vi.advanceTimersByTimeAsync(8_000)
    expect(await screen.findByTestId('branding-failed')).toBeTruthy()
    down = false
    fireEvent.click(screen.getByRole('button', { name: 'Spróbuj ponownie' }))
    expect(await screen.findByTestId('demo-card')).toBeTruthy()
    vi.useRealTimers()
  })
})
