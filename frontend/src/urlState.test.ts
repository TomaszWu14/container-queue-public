import { describe, expect, it } from 'vitest'

import { resolveModule, SELECTABLE_MODULES } from './urlState'

describe('resolveModule — wybór spółki z URL z egzekwowaniem uprawnień', () => {
  it('seesAll: przyjmuje poprawny moduł z URL', () => {
    for (const m of SELECTABLE_MODULES) {
      expect(resolveModule(m, true, 'acme')).toBe(m)
    }
  })
  it('seesAll: nieznany moduł → domyślny', () => {
    expect(resolveModule('haker', true, 'acme')).toBe('acme')
    expect(resolveModule('', true, 'acme')).toBe('acme')
  })
  it('konto bez wglądu we wszystkie spółki: URL NIE przełącza spółki (zawsze własna)', () => {
    expect(resolveModule('beta', false, 'mag1')).toBe('mag1')
    expect(resolveModule('acme', false, 'mag1')).toBe('mag1')
    expect(resolveModule('', false, 'mag1')).toBe('mag1')
  })
})
