// @vitest-environment jsdom
// US-037: panel jakości odczytu faktur — odsetek automatycznych dopasowań, trafność modelu,
// słupki tygodniowe z opisem dostępnym bez koloru i tabela trafności wg pewności (próg z serwera).
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import type { AiQuality } from './AiQualityPanel'

const { get } = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('../api', () => ({ api: { get } }))

import AiQualityPanel from './AiQualityPanel'

afterEach(() => { cleanup(); get.mockReset() })

const data: AiQuality = {
  weeks: [
    { week: '2026-10-05', rules: 0, ml: 0, user: 0, open: 0 },
    { week: '2026-10-12', rules: 6, ml: 3, user: 2, open: 1 },
  ],
  totals: { rules: 6, ml: 3, user: 2, open: 1, items: 12 },
  automated_pct: 75, ml_hit_pct: 80, threshold: 0.9,
  buckets: [
    { bucket: 'low', suggested: 2, decided: 1, hits: 0, hit_pct: 0 },
    { bucket: 'high', suggested: 3, decided: 3, hits: 2, hit_pct: 67 },
    { bucket: 'auto', suggested: 4, decided: 4, hits: 4, hit_pct: 100 },
  ],
}

describe('jakość odczytu faktur', () => {
  it('liczby, słupki tygodniowe z opisem i kalibracja z progiem', async () => {
    get.mockResolvedValue(data)
    render(<AiQualityPanel />)
    expect((await screen.findByText('Pozycji dopasowanych automatycznie')).previousElementSibling?.textContent).toBe('75%')
    expect(screen.getByText('Trafność podpowiedzi modelu').previousElementSibling?.textContent).toBe('80%')
    expect(get).toHaveBeenCalledWith('/api/automations/ai-quality')
    const bars = [...document.querySelectorAll('.aiq-bar-col')]
    expect(bars).toHaveLength(2)
    expect(bars[1].getAttribute('aria-label')).toBe('tydzień od 12.10.2026: Reguły 6, Model ML 3, Człowiek 2, Do decyzji 1')
    expect(bars[1].querySelectorAll('.aiq-seg')).toHaveLength(4)
    expect(bars[0].querySelectorAll('.aiq-seg')).toHaveLength(0)
    expect(screen.getByText('od 90% — automat ustawia sam')).toBeTruthy()
    expect(screen.getByText('67%')).toBeTruthy()
  })

  it('brak faktur — komunikat zamiast wykresu; „—” zamiast procentu bez danych', async () => {
    get.mockResolvedValue({ ...data, weeks: [], totals: { rules: 0, ml: 0, user: 0, open: 0, items: 0 },
                            automated_pct: null, ml_hit_pct: null })
    render(<AiQualityPanel />)
    expect(await screen.findByText('Brak faktur w tym okresie.')).toBeTruthy()
    expect(screen.getByText('Pozycji dopasowanych automatycznie').previousElementSibling?.textContent).toBe('—')
    expect(screen.queryByRole('table')).toBeNull()
  })
})
