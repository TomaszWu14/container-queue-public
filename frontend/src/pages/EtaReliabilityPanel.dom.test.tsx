// @vitest-environment jsdom
// Trzecia lista PO, pkt 7: tabela punktualności armatorów i realne ETA kontenerów w drodze.
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import type { EtaReliability } from './EtaReliabilityPanel'

const { get } = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('../api', () => ({ api: { get } }))

import EtaReliabilityPanel from './EtaReliabilityPanel'

afterEach(() => { cleanup(); get.mockReset() })

describe('Punktualność armatorów', () => {
  it('tabela i realne ETA', async () => {
    const data: EtaReliability = {
      window_days: 365, min_arrivals: 3, forecast_total: 1,
      carriers: [{ carrier: 'Demo Line', port: 'GDANSK', arrivals: 12, median_days: 3.5, p90_days: 6, late_pct: 75 }],
      forecasts: [{ container_id: 4, container_no: 'MSKU1000132', carrier: 'Demo Line', port: 'GDANSK', eta: '2026-10-25',
                    realistic_eta: '2026-10-29', shift_days: 4, basis: 'carrier_port', arrivals: 12 }],
    }
    get.mockResolvedValue(data)
    render(<MemoryRouter><EtaReliabilityPanel /></MemoryRouter>)
    expect(await screen.findByText('Demo Line', { selector: 'td' })).toBeTruthy()
    expect(screen.getByText('75%')).toBeTruthy()
    expect(screen.getByText(/ETA 25\.10\.2026, realnie ok\. 29\.10\.2026 \(\+4 dni wg historii Demo Line\)/)).toBeTruthy()
    expect(screen.getByRole('link', { name: 'MSKU1000132' }).getAttribute('href')).toBe('/kontenery/4')
  })

  it('za mało danych', async () => {
    get.mockResolvedValue({ window_days: 365, min_arrivals: 3, carriers: [], forecasts: [], forecast_total: 0 })
    render(<MemoryRouter><EtaReliabilityPanel /></MemoryRouter>)
    expect(await screen.findByText('Za mało przypłynięć w historii, żeby ocenić punktualność.')).toBeTruthy()
  })
})
