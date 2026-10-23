// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import LoginPage from './pages/LoginPage'

afterEach(() => { cleanup(); vi.restoreAllMocks() })

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })

describe('Bramka demo — „przedstaw się”', () => {
  it('428 z logowania pokazuje formularz; po wysłaniu demo loguje ponownie', async () => {
    let registered = false
    const posted: string[] = []
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.includes('/api/public/branding')) return json({ demo_login: 'demo', demo_password: 'haslo-demo-123' })
      if (url.includes('/api/public/demo-visitor')) { registered = true; posted.push(String(init?.body)); return new Response(null, { status: 204 }) }
      if (url.includes('/api/auth/login')) return registered ? json({}) : json({ detail: 'Zanim wejdziesz…' }, 428)
      return json({})
    }))
    const onLogin = vi.fn()
    render(<MemoryRouter><LoginPage onLogin={onLogin} /></MemoryRouter>)

    fireEvent.click(await screen.findByRole('button', { name: 'Wejdź jako demo' }))
    const form = await screen.findByTestId('visitor-form')
    expect(form.textContent).toContain('Prezesa UODO')
    const submit = screen.getByRole('button', { name: 'Wejdź do demo' }) as HTMLButtonElement
    expect(submit.disabled).toBe(true)

    fireEvent.change(screen.getByLabelText('Imię'), { target: { value: 'Jan' } })
    fireEvent.change(screen.getByLabelText('Nazwisko'), { target: { value: 'Kowalski' } })
    fireEvent.change(screen.getByLabelText('Firma'), { target: { value: 'ACME' } })
    fireEvent.click(screen.getByRole('checkbox'))
    expect(submit.disabled).toBe(false)
    fireEvent.click(submit)

    await waitFor(() => expect(onLogin).toHaveBeenCalled())
    expect(JSON.parse(posted[0])).toMatchObject({ first_name: 'Jan', company: 'ACME', consent: true, website: '' })
  })
})
