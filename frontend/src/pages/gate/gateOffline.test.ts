// @vitest-environment jsdom
// US-085: pamięć listy bramy (bez nazwiska kierowcy, na użytkownika, 12 h) i kolejka „Przyjechał”
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ApiError } from '../../api'
import type { GateItem } from '../GatePage'
import * as offline from './gateOffline'

const item = (id: number): GateItem => ({
  id, container_no: `MSKU${id}`, truck_no: 'WX 123', trailer_no: '', driver_name: 'Jan Kowalski',
  warehouse_id: 1, warehouse: 'MAG-1', notify_date: '2026-10-19', eta: null, status: 'AWIZOWANY',
  driver_arrived_at: null, checked_in_at: null,
})

beforeEach(() => localStorage.clear())

describe('Brama offline', () => {
  it('lista: bez nazwiska kierowcy, tylko ten sam użytkownik i magazyn, wygasa po 12 h', () => {
    offline.saveList(7, '', [item(1)], 1_000)
    expect(offline.loadList(7, '', 2_000)!.items[0].driver_name).toBe('')
    expect(offline.loadList(8, '', 2_000)).toBeNull()
    expect(offline.loadList(7, '3', 2_000)).toBeNull()
    expect(offline.loadList(7, '', 1_000 + offline.MAX_AGE_MS + 1)).toBeNull()
  })

  it('kolejka: wysyła po powrocie sieci, przy braku sieci zostaje, przy błędzie serwera wypada', async () => {
    offline.queueCheckin(7, 1)
    offline.queueCheckin(7, 2)
    offline.queueCheckin(9, 3)                                   // inny użytkownik — nie jego kolejka
    const down = vi.fn().mockRejectedValue(new ApiError(0, 'offline'))
    expect(await offline.flush(7, down)).toEqual({ sent: [], failed: [] })
    expect(offline.pending(7).map(p => p.id)).toEqual([1, 2])
    const post = vi.fn().mockResolvedValueOnce({}).mockRejectedValueOnce(new ApiError(404, 'nie ma'))
    expect(await offline.flush(7, post)).toEqual({ sent: [1], failed: [2] })
    expect(offline.pending(7)).toEqual([])
    expect(offline.pending(9).map(p => p.id)).toEqual([3])
  })
})
