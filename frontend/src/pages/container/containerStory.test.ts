// Przebieg kontenera: z historii zmian zostają kamienie milowe procesu, od najstarszego,
// opisane ludzkim językiem; zmiany techniczne (np. notatka) nie trafiają na oś.
import { describe, expect, it } from 'vitest'
import type { AuditEntry } from '../../types'
import { containerStory } from './containerStory'

const t = (k: string) => ({
  storyStatus: 'Status: {v}', st_W_PORCIE: 'W porcie', storyCustoms: 'Odprawa: {v}', cs_ZLECONA: 'Zlecona',
  storyDocsSent: 'Dokumenty przekazane', storyDocsSentMissing: 'Dokumenty przekazane mimo braków',
  storyDocAdded: 'Dodano: {v}', storyPlanSent: 'Plan wysłany', storyDocsMissing: 'Braki: {v}',
} as Record<string, string>)[k] ?? k

let n = 0
const e = (field: string, new_value: string | null, at: string, note = ''): AuditEntry =>
  ({ id: ++n, field, old_value: null, new_value, note, user_login: 'log.tim', created_at: at })

describe('przebieg kontenera', () => {
  it('kamienie milowe od najstarszego, bez zmian technicznych', () => {
    const history = [   // API: od najnowszego
      e('document_status', 'WYSLANE', '2026-10-05T10:00:00', 'wysyłka MIMO braków: Faktura'),
      e('customer_note', 'cokolwiek', '2026-10-04T10:00:00'),
      e('customs_status', 'ZLECONA', '2026-10-03T10:00:00'),
      e('attachment_upload', 'bl.pdf', '2026-10-02T10:00:00'),
      e('status', 'W_PORCIE', '2026-10-01T10:00:00'),
    ]
    expect(containerStory(history, t).map(s => [s.kind, s.text])).toEqual([
      ['status', 'Status: W porcie'],
      ['docs', 'Dodano: bl.pdf'],
      ['customs', 'Odprawa: Zlecona'],
      ['docs', 'Dokumenty przekazane mimo braków'],
    ])
  })

  it('plan i braki dokumentów; nieznany status bez tłumaczenia zostaje surowy', () => {
    const steps = containerStory([
      e('docs_missing_on_status', 'Faktura, PL', '2026-10-02T10:00:00'),
      e('planning_status', 'WYSLANE', '2026-10-01T09:00:00'),
      e('status', 'NOWY_STATUS', '2026-10-01T08:00:00'),
      e('planning_status', 'PROPOZYCJA', '2026-10-01T07:00:00'),
    ], t)
    expect(steps.map(s => s.text)).toEqual(['Status: NOWY_STATUS', 'Plan wysłany', 'Braki: Faktura, PL'])
    expect(steps[2].kind).toBe('warn')
  })
})
