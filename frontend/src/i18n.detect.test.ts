// Język na start (druga lista PO, pkt 2): zapamiętany wybór wygrywa; bez niego pierwszy obsługiwany
// język przeglądarki (pl / en / pt, także z regionem), a gdy żaden — angielski (gość z zagranicy).
import { describe, expect, it } from 'vitest'
import { detectLang } from './i18n'

describe('detectLang', () => {
  it('zapamiętany wybór ma pierwszeństwo', () => {
    expect(detectLang('pt', ['pl-PL'])).toBe('pt')
  })
  it('język przeglądarki z regionem', () => {
    expect(detectLang(null, ['pl-PL', 'en'])).toBe('pl')
    expect(detectLang(null, ['de-DE', 'pt-BR'])).toBe('pt')
  })
  it('nieobsługiwany język i śmieć w pamięci → angielski', () => {
    expect(detectLang('xx', ['de-DE', 'fr'])).toBe('en')
    expect(detectLang(null, [])).toBe('en')
  })
})
