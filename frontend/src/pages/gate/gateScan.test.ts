// Skaner bramy: kod QR z karty rozładunku (link do kontenera) albo wpisany numer → auto z dzisiejszej listy.
import { describe, expect, it } from 'vitest'
import type { GateItem } from '../GatePage'
import { findGateItem, parseScan } from './gateScan'

const item = (id: number, no: string) => ({ id, container_no: no } as GateItem)
const items = [item(7, 'MSDU0806613'), item(9, 'TGHU1234567')]

describe('skaner bramy — odczyt', () => {
  it('link z etykiety QR → id kontenera', () => {
    expect(parseScan('https://kolejka.twapp.pl/kontenery/7')).toEqual({ id: 7 })
    expect(parseScan('https://x.pl/kontenery/9?akcja=history')).toEqual({ id: 9 })
  })
  it('wpisany numer: bez spacji i myślników, wielkie litery', () => {
    expect(parseScan(' msdu 080661-3 ')).toEqual({ no: 'MSDU0806613' })
    expect(parseScan('ab')).toBeNull()
  })
  it('szuka tylko na dzisiejszej liście bramy', () => {
    expect(findGateItem(items, { id: 9 })?.container_no).toBe('TGHU1234567')
    expect(findGateItem(items, { no: 'MSDU0806613' })?.id).toBe(7)
    expect(findGateItem(items, { id: 99 })).toBeNull()
    expect(findGateItem(items, parseScan('https://x.pl/kontenery/99/karta'))).toBeNull()
  })
})
