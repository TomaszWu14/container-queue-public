// @vitest-environment jsdom
// Druga lista PO, pkt 4: wykres przepływu — etapy w kolejności procesu, pasmo na każde przejście (grubość wg
// liczby), cofnięcia pod osią z legendą; opis dostępny bez wykresu (aria-label z liczbami).
import { afterEach, describe, expect, it } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import ProcessFlowChart from './ProcessFlowChart'

afterEach(cleanup)

const ORDER = ['W_TRANSPORCIE', 'W_PORCIE', 'ODPRAWA', 'AWIZOWANY']

describe('wykres przepływu procesu', () => {
  it('przejścia w przód i cofnięcie, grubość wg liczby', () => {
    render(<ProcessFlowChart order={ORDER} transitions={[
      { from: 'W_TRANSPORCIE', to: 'W_PORCIE', count: 10 },
      { from: 'W_PORCIE', to: 'ODPRAWA', count: 5 },
      { from: 'ODPRAWA', to: 'W_PORCIE', count: 1 },
    ]} />)
    const img = screen.getByRole('img')
    expect(img.getAttribute('aria-label')).toContain('8 · Odprawa celna → 4 · Port docelowy: 1')
    expect(document.querySelectorAll('.proc-flow-node')).toHaveLength(3)     // AWIZOWANY bez przejść — pominięty
    const lines = [...document.querySelectorAll('.proc-flow-fwd line')]
    expect(Number(lines[0].getAttribute('stroke-width'))).toBeGreaterThan(Number(lines[1].getAttribute('stroke-width')))
    expect(document.querySelectorAll('.proc-flow-back path')).toHaveLength(1)
    expect(screen.getByText('Cofnięcie statusu')).toBeTruthy()
  })

  it('mniej niż dwa etapy — nic', () => {
    const { container } = render(<ProcessFlowChart order={ORDER} transitions={[]} />)
    expect(container.textContent).toBe('')
  })
})
