// @vitest-environment jsdom
// Strażnik tła wiersza kolejki wg magazynu: MAG-1 → kq-wh-mag1, ACME → kq-wh-acme (ten sam klucz co
// kolumna Magazyn, więc „ACME MAG-1" to MAG-1), bez magazynu / inny magazyn → brak klasy (białe tło).
import { createContext } from 'react'
import { describe, expect, it, vi } from 'vitest'
import { render } from '@testing-library/react'

vi.mock('../../i18n', () => ({
  useT: () => (key: string) => key,
  LangContext: createContext({ lang: 'pl' }),
  localeFor: () => 'pl-PL',
}))
vi.mock('../ContainerDetailPanel', () => ({ default: () => null }))

import GroupBody from './EnterpriseGroup'
import type { TableCtx } from './EnterpriseTable'
import type { Container } from '../../types'

const row = (id: number, warehouse_name: string | null) =>
  ({ id, container_no: `C${id}`, status: 'W_PORCIE', warehouse_name }) as unknown as Container

const items = [row(1, 'MAG-1'), row(2, 'ACME'), row(3, null), row(4, 'ACME MAG-1'), row(5, 'BETA')]
const x = {
  groupBy: 'warehouse', collapsed: new Set(), collapsedPlanning: [], selectable: false,
  mv: { selected: new Set(), moveActive: false, dragId: null },
  watched: new Set(), sortItems: (i: Container[]) => i, expandedId: null, drawerId: null,
  warehouseKeys: [], cumByDay: new Map(), limitFor: () => null,
} as unknown as TableCtx

describe('wiersz kolejki — tło wg magazynu', () => {
  it('klasa kq-wh-* tylko dla MAG-1 i ACME', () => {
    const { container } = render(<table><GroupBody g={{ key: 'X', items }} x={x} cols={[]} span={2} /></table>)
    const cls = (id: number) => container.querySelector(`tr[data-cid="${id}"]`)!.className
    expect(cls(1)).toContain('kq-wh-mag1')
    expect(cls(2)).toContain('kq-wh-acme')
    expect(cls(4)).toContain('kq-wh-mag1')
    for (const id of [3, 5]) expect(cls(id)).not.toMatch(/kq-wh-/)
  })
})
