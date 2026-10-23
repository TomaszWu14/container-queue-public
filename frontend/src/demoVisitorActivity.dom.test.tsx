// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { Link, MemoryRouter } from 'react-router-dom'
import DemoVisitTracker from './DemoVisitTracker'
import DemoVisitorsTab from './pages/admin/DemoVisitorsTab'
import DemoVisitorForm from './pages/DemoVisitorForm'
import demoFeature from './i18n/features/demo-wizytowka'

afterEach(() => { cleanup(); vi.restoreAllMocks(); vi.unstubAllGlobals() })

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })

describe('Aktywność gościa demo', () => {
  it('przy każdej zmianie ekranu wysyła sygnał z samą ścieżką', async () => {
    const bodies: string[] = []
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      if (String(input).includes('/api/public/demo-visitor/view')) bodies.push(String(init?.body))
      return new Response(null, { status: 204 })
    }))
    render(<MemoryRouter initialEntries={['/pulpit?x=1']}>
      <DemoVisitTracker /><Link to="/kolejka/12">dalej</Link>
    </MemoryRouter>)
    await waitFor(() => expect(bodies).toHaveLength(1))
    fireEvent.click(screen.getByText('dalej'))
    await waitFor(() => expect(bodies).toHaveLength(2))
    expect(bodies.map(b => JSON.parse(b).path)).toEqual(['/pulpit', '/kolejka/12'])
  })

  it('lista gości pokazuje ekrany, czas i najczęstsze sekcje', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => json([
      { id: 1, first_name: 'Jan', last_name: 'K', company: 'F', created_at: '2026-10-23T10:00:00',
        page_views: 7, duration_min: 12, top_sections: ['kolejka', 'pulpit'] },
      { id: 2, first_name: 'Ewa', last_name: 'N', company: 'G', created_at: '2026-10-23T11:00:00',
        page_views: 0, duration_min: null, top_sections: [] },
    ])))
    render(<DemoVisitorsTab />)
    expect(await screen.findByText('ok. 12 min')).toBeTruthy()
    for (const head of ['Ekrany', 'Czas', 'Najczęściej']) expect(screen.getByText(head)).toBeTruthy()
    expect(screen.getByText('kolejka, pulpit')).toBeTruthy()
    expect(screen.getAllByText('—')).toHaveLength(2)
  })

  it('klauzula RODO mówi o zapisie oglądanych ekranów (PL i EN)', () => {
    const { pl, en } = demoFeature as unknown as Record<'pl' | 'en', Record<string, string>>
    expect(pl.visitorGdpr).toContain('O każdej wizycie (imię, nazwisko, firma) dostaję powiadomienie na telefon '
      + 'przez usługę powiadomień push ntfy. Zapisuję też, ile i jakie ekrany wersji demonstracyjnej obejrzałeś '
      + '(bez adresu IP), żeby wiedzieć, co zainteresowało gości. Poza tym nikomu danych nie przekazuję.')
    expect(en.visitorGdpr).toContain('I also record how many and which screens of the demo you viewed '
      + '(without your IP address) to see what visitors find interesting. Apart from that I do not share')
  })

  it('bramka gościa nie ujawnia adresu jawnym tekstem (anty-boty), tylko „[at]”', () => {
    const { container } = render(<DemoVisitorForm onDone={() => {}} onBack={() => {}} />)
    expect(container.innerHTML).not.toContain('tomasz.wierzbowski@op.pl')
    expect(container.innerHTML).toContain('tomasz.wierzbowski [at] op.pl')
    const { pl, en } = demoFeature as unknown as Record<'pl' | 'en', Record<string, string>>
    expect(pl.visitorGdpr).toContain('tomasz.wierzbowski [at] op.pl')
    expect(en.visitorGdpr).toContain('tomasz.wierzbowski [at] op.pl')
  })
})
