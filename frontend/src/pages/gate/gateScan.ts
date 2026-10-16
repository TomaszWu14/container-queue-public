// Skaner bramy: co odczytano z kodu QR albo wpisano ręcznie → który kontener z dzisiejszej listy bramy.
// Etykieta QR z karty rozładunku koduje link `<origin>/kontenery/<id>`; ochrona może też wpisać numer.
// Szukamy WYŁĄCZNIE na liście bramy (dzisiejsze auta w zakresie użytkownika) — nic spoza niej nie wpuszczamy.
import type { GateItem } from '../GatePage'

export type Scan = { id: number } | { no: string } | null

export function parseScan(raw: string): Scan {
  const text = raw.trim()
  const link = text.match(/\/kontenery\/(\d+)(?:[/?#]|$)/)
  if (link) return { id: Number(link[1]) }
  const no = text.toUpperCase().replace(/[\s-]/g, '')
  return no.length >= 4 ? { no } : null
}

export function findGateItem(items: GateItem[], scan: Scan): GateItem | null {
  if (!scan) return null
  if ('id' in scan) return items.find(i => i.id === scan.id) ?? null
  return items.find(i => i.container_no.toUpperCase().replace(/[\s-]/g, '') === scan.no) ?? null
}
