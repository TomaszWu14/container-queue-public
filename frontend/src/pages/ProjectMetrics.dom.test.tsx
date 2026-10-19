// @vitest-environment jsdom
// US-080: metryki projektu — liczby z wygenerowanego pliku, wszystkie dodatnie, z datą policzenia
import { afterEach, describe, expect, it } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import metrics from '../data/projectMetrics.json'
import ProjectMetrics, { METRICS } from './ProjectMetrics'

afterEach(cleanup)

describe('Metryki projektu', () => {
  it('plik ma wszystkie liczby (> 0) i datę', () => {
    for (const [field] of METRICS) expect(Number(metrics[field]), field).toBeGreaterThan(0)
    expect(metrics.generated_at).toMatch(/^\d{4}-\d{2}-\d{2}$/)
  })

  it('pokazuje kafelki z liczbami i datą', () => {
    render(<ProjectMetrics />)
    expect(screen.getByRole('region', { name: 'Metryki projektu' })).toBeTruthy()
    expect(screen.getByText(String(metrics.backend_tests))).toBeTruthy()
    expect(screen.getByText('testów backendu (pytest)')).toBeTruthy()
    expect(screen.getByText(/stan na/)).toBeTruthy()
  })
})
