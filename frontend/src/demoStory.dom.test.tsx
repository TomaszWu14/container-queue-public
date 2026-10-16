// @vitest-environment jsdom
// Pomysł 1 PO: ekran powitalny demo zaczyna od „historii jednego kontenera” — gdy serwer podaje kontener
// pokazowy, pierwszy krok prowadzi na jego kartę od razu na zakładkę Przebieg (?akcja=history).
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom'
import DemoMode from './DemoMode'

afterEach(() => { cleanup(); vi.unstubAllGlobals(); localStorage.clear() })

function stub(branding: Record<string, unknown>) {
  vi.stubGlobal('fetch', vi.fn(async () => new Response(JSON.stringify(branding),
    { status: 200, headers: { 'Content-Type': 'application/json' } })))
}

function Where() { const l = useLocation(); return <span data-testid="where">{l.pathname + l.search}</span> }

const app = () => render(<MemoryRouter initialEntries={['/pulpit']}>
  <DemoMode /><Routes><Route path="*" element={<Where />} /></Routes></MemoryRouter>)

describe('demo — historia jednego kontenera', () => {
  it('pierwszy krok prowadzi na przebieg kontenera pokazowego', async () => {
    stub({ demo_story_container_id: 42 })
    app()
    const title = await screen.findByText('Historia jednego kontenera (1 min)')
    fireEvent.click(title.closest('li')!.querySelector('button')!)
    expect(screen.getByTestId('where').textContent).toBe('/kontenery/42?akcja=history')
  })

  it('bez kontenera pokazowego — dotychczasowe cztery kroki', async () => {
    stub({})
    app()
    await screen.findByText('Pulpit')
    expect(screen.queryByText('Historia jednego kontenera (1 min)')).toBeNull()
  })
})
