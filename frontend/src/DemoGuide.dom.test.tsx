// @vitest-environment jsdom
// US-081: przewodnik po demo — przejście po krokach, podświetlenie celu, Escape zamyka, role filtrują kroki
import { afterEach, describe, expect, it, vi } from 'vitest'
import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom'
import DemoGuide, { GUIDE_STEPS, stepsFor } from './DemoGuide'

afterEach(() => { cleanup(); vi.useRealTimers() })

function Where() { return <span data-testid="where">{useLocation().pathname}</span> }

function setup(index = 0, onIndex = vi.fn(), onClose = vi.fn()) {
  render(
    <MemoryRouter initialEntries={['/start']}>
      <Routes><Route path="*" element={<><Where /><main><div className="panel"><table className="grid" /></div></main></>} /></Routes>
      <DemoGuide steps={GUIDE_STEPS} index={index} onIndex={onIndex} onClose={onClose} />
    </MemoryRouter>,
  )
  return { onIndex, onClose }
}

describe('Przewodnik po demo', () => {
  it('pierwszy krok: przejście do kolejki i podświetlenie tabeli', () => {
    vi.useFakeTimers()
    setup()
    expect(screen.getByTestId('where').textContent).toBe('/kolejka')
    expect(screen.getByRole('dialog', { name: 'Przewodnik po demo' })).toBeTruthy()
    expect(screen.getByText(`Krok 1 z ${GUIDE_STEPS.length}`)).toBeTruthy()
    act(() => { vi.advanceTimersByTime(150) })
    expect(document.querySelector('table.grid')!.classList.contains('tour-highlight')).toBe(true)
  })

  it('Dalej / Wstecz / Zakończ i Escape', () => {
    const { onIndex, onClose } = setup(1)
    fireEvent.click(screen.getByRole('button', { name: 'Dalej' }))
    expect(onIndex).toHaveBeenCalledWith(2)
    fireEvent.click(screen.getByRole('button', { name: 'Wstecz' }))
    expect(onIndex).toHaveBeenCalledWith(0)
    fireEvent.keyDown(window, { key: 'Escape' })
    expect(onClose).toHaveBeenCalled()
  })

  it('ostatni krok kończy przewodnik', () => {
    const { onClose } = setup(GUIDE_STEPS.length - 1)
    fireEvent.click(screen.getByRole('button', { name: 'Gotowe' }))
    expect(onClose).toHaveBeenCalled()
  })

  it('konta partnerów nie dostają kroków ekranu Automatyzacje', () => {
    expect(stepsFor('forwarder').some(s => s.path === '/automatyzacje')).toBe(false)
    expect(stepsFor('logistics').some(s => s.path === '/automatyzacje')).toBe(true)
  })
})
