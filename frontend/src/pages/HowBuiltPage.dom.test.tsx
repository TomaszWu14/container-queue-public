// @vitest-environment jsdom
// „Jak to zbudowano”: architektura, liczby jakości, decyzje z linkami do repozytorium (nowa karta, noopener).
import { afterEach, describe, expect, it } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import HowBuiltPage, { REPO } from './HowBuiltPage'

afterEach(cleanup)

describe('Jak to zbudowano', () => {
  it('pokazuje architekturę, jakość i decyzje z linkami do dokumentów', () => {
    render(<MemoryRouter><HowBuiltPage /></MemoryRouter>)
    expect(screen.getByRole('heading', { name: 'Architektura' })).toBeTruthy()
    expect(screen.getByText('PostgreSQL 16')).toBeTruthy()
    expect(screen.getByText('≥ 92%')).toBeTruthy()
    expect(screen.getByText('Izolacja danych w jednym miejscu')).toBeTruthy()
    const links = screen.getAllByRole('link')
    expect(links.length).toBeGreaterThanOrEqual(10)
    for (const a of links) {
      expect(a.getAttribute('href')!.startsWith(REPO)).toBe(true)
      expect(a.getAttribute('rel')).toContain('noopener')
    }
  })
})
