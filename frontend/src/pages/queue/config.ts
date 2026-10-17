// Stałe i typy kolejki wyniesione z QueuePage.tsx (moduły/spółki, tryby zakresu, sort).
import type { Container } from '../../types'
import type { Country } from '../../holidays'

export const ACME = 'ACME'

// osobne kolejki per spółka + MAG-1 (magazyn) + wspólny fallback „main" i analiza
export type Module = 'acme' | 'mag1' | 'beta' | 'gamma' | 'delta' | 'tranzyt' | 'main' | 'analysis'

// klucz modułu → kod spółki (filtr backendu). MAG-1 to spółka Acme + filtr magazynu.
export const MODULE_CODE: Partial<Record<Module, string>> = {
  acme: 'ACME', mag1: 'ACME', beta: 'BETA', gamma: 'GAMMA', delta: 'DELTA',
}

// moduł MAG-1 = kontenery spółki Acme kierowane do magazynu MAG-1 (Acme agreguje ACME + MAG-1)
// kraj kalendarza świąt w kolejce (backend: warehouse.country, domyślnie PL)
export const moduleCountry = (m: Module): Country => m === 'delta' ? 'PT' : 'PL'

export const MODULE_WAREHOUSE: Partial<Record<Module, string>> = { mag1: 'MAG-1' }

// tranzyt nie jest spółką ani magazynem — to flaga na kontenerze. Pozostałe zakładki
// wysyłają jawne transit=false, żeby tranzyty nie wpadały do zwykłych kolejek.
export const MODULE_TRANSIT: Partial<Record<Module, boolean>> = { tranzyt: true }

// magazyny rozładunku dostępne z menu kontekstowego per zakładka (Delta — nie zmieniamy)
export const WAREHOUSE_OPTIONS: Partial<Record<Module, string[]>> = {
  acme: ['MAG-1', 'ACME'],
  mag1: ['MAG-1', 'ACME'],
  beta: ['ACME', 'BETA'],
  gamma: ['ACME', 'GAMMA'],
}

export type RangeMode = 'all' | 'fromToday' | 'month' | 'week' | 'custom'

// stała mapa trybu zakresu → klucz tłumaczenia (wyczerpująca po RangeMode)
export const RANGE_LABEL: Record<RangeMode, string> = {
  all: 'rangeAll', fromToday: 'rangeFromToday',
  month: 'rangeMonth', week: 'rangeWeek', custom: 'rangeCustom',
}

// multi-sort w dniu — akcesory kolumn sortowalnych
export const SORT_ACCESSOR: Record<string, (c: Container) => string | number> = {
  supplier: c => c.supplier_name ?? '',
  vessel: c => c.vessel ?? '',
  eta: c => c.eta ?? '9999',
  containerNo: c => c.container_no,
  forwarder: c => c.forwarder_name ?? '',
  status: c => c.status,
  orderNumbers: c => c.order_numbers || c.order_number || '',
  warehouse: c => c.warehouse_name ?? '',
  notifyDate: c => c.notify_date ?? '9999',
  customs: c => c.customs_status,
  demurrage: c => c.demurrage_deadline ?? '9999',
}

export type SortKey = { key: string; dir: 1 | -1 }

export type GroupBy = 'weekday' | 'warehouse' | 'status'

// menu kontekstowe kafelka (magazyn / data / kebab) — kontener + pozycja kursora
export type TileMenuPos = { c: Container; x: number; y: number }

// note = wpis do historii; fromDate = zmiana z kalendarza (nie kasuj zaznaczenia)
export type PendingMove = { ids: number[]; day: string; note?: string; fromDate?: boolean }
