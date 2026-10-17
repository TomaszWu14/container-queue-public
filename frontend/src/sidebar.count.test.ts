// audyt UI C14/A17: licznik „Kolejka” nie dolicza magazynu MAG-1 (podzbiór Acme) drugi raz
import { describe, expect, it } from 'vitest'
import { activeTotal } from './Sidebar'

describe('activeTotal', () => {
  it('sumuje spółki, pomija klucz MAG-1', () => {
    expect(activeTotal({ ACME: 288, 'MAG-1': 96, BETA: 1, DELTA: 1 })).toBe(290)
  })
  it('pusta odpowiedź → 0', () => {
    expect(activeTotal({})).toBe(0)
  })
})
