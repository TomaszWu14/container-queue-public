// Przebieg kontenera (pomysł 3 „oś czasu kontenera”): z historii zmian (GET …/history) wybieramy
// kamienie milowe procesu — status, odprawa, dokumenty, plan, termin, slot — i opisujemy je ludzkim
// językiem. Reszta zmian zostaje w pełnej tabeli historii. Bez nowego API: te same dane, inna forma.
import type { AuditEntry } from '../../types'
import { formatDate } from '../../dates'

export type StoryKind = 'status' | 'customs' | 'docs' | 'plan' | 'warn'
export type StoryStep = { id: number; at: string; who: string | null; kind: StoryKind; text: string }

type T = (key: string) => string
const tr = (t: T, prefix: string, v: string) => { const k = prefix + v; const s = t(k); return s === k ? v : s }
const fill = (text: string, value: string) => text.replace('{v}', value)

function describe(e: AuditEntry, t: T): [StoryKind, string] | null {
  const v = e.new_value ?? ''
  switch (e.field) {
    case 'status': return v ? ['status', fill(t('storyStatus'), tr(t, 'st_', v))] : null
    case 'customs_status': return v ? ['customs', fill(t('storyCustoms'), tr(t, 'cs_', v))] : null
    case 'customs_agency': return v ? ['customs', fill(t('storyAgency'), v)] : null
    case 'document_status':
      if (v !== 'WYSLANE') return null
      return ['docs', t(e.note.includes('MIMO braków') ? 'storyDocsSentMissing' : 'storyDocsSent')]
    case 'invoice_agency_mail': return ['docs', t('storyAgencyMail')]
    case 'attachment_upload': return v ? ['docs', fill(t('storyDocAdded'), v)] : null
    case 'planning_status':
      if (v === 'WYSLANE') return ['plan', t('storyPlanSent')]
      if (v === 'POTWIERDZONE') return ['plan', t('storyPlanConfirmed')]
      return null
    case 'notify_date': return v ? ['plan', fill(t('storyDelivery'), formatDate(v))] : null
    case 'slot_time': return v ? ['plan', fill(t('storySlot'), v)] : null
    case 'docs_missing_on_status': return v ? ['warn', fill(t('storyDocsMissing'), v)] : null
    default: return null
  }
}

/** Kamienie milowe od najstarszego (historia z API przychodzi od najnowszego). */
export function containerStory(history: AuditEntry[], t: T): StoryStep[] {
  const steps: StoryStep[] = []
  for (const e of history) {
    const d = describe(e, t)
    if (d) steps.push({ id: e.id, at: e.created_at, who: e.user_login, kind: d[0], text: d[1] })
  }
  return steps.sort((a, b) => a.at.localeCompare(b.at) || a.id - b.id)
}
