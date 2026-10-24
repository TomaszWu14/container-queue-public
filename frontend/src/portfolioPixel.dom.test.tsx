// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { Link, MemoryRouter } from 'react-router-dom'
import PortfolioPixel from './PortfolioPixel'

afterEach(() => { cleanup(); vi.restoreAllMocks(); vi.unstubAllGlobals() })

describe('Piksel portfolio.twapp.pl', () => {
  it('przy każdej zmianie ekranu ładuje piksel kolejka-kontenerow', () => {
    const srcs: string[] = []
    vi.stubGlobal('Image', class { set src(v: string) { srcs.push(v) } })
    render(<MemoryRouter initialEntries={['/']}>
      <PortfolioPixel /><Link to="/kolejka/12">dalej</Link>
    </MemoryRouter>)
    fireEvent.click(screen.getByText('dalej'))
    expect(srcs).toEqual([
      'https://portfolio.twapp.pl/px/kolejka-kontenerow',
      'https://portfolio.twapp.pl/px/kolejka-kontenerow',
    ])
  })
})
