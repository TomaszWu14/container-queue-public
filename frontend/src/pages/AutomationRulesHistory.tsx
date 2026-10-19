// Historia zmian reguł z kreatora (trzecia lista PO, pkt 4): kto, kiedy, co — i „przywróć stan sprzed tej
// zmiany” dla jednej reguły (tylko admin; przywrócenie też trafia do historii).
import { useEffect, useState } from 'react'
import { api, errorMessage } from '../api'
import { formatDateTime } from '../dates'
import { useT } from '../i18n'

export interface RuleHistoryEntry {
  id: number; at: string; action: 'added' | 'changed' | 'removed'; user: string; name: string
  changed: string[]; note: string
}

export default function AutomationRulesHistory({ canEdit, refreshKey, onRestored }: {
  canEdit: boolean; refreshKey: number; onRestored: (rules: unknown) => void
}) {
  const t = useT()
  const [open, setOpen] = useState(false)
  const [items, setItems] = useState<RuleHistoryEntry[] | null>(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState<number | null>(null)

  useEffect(() => {
    if (!open) return
    api.get<RuleHistoryEntry[]>('/api/automations/rules/history')
      .then(r => setItems(Array.isArray(r) ? r : [])).catch(err => setError(errorMessage(err)))
  }, [open, refreshKey])

  const restore = async (entry: RuleHistoryEntry) => {
    if (!window.confirm(t('ruleHistRestoreConfirm').replace('{name}', entry.name))) return
    setBusy(entry.id); setError('')
    try {
      onRestored(await api.post(`/api/automations/rules/history/${entry.id}/restore`, {}))
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy(null)
    }
  }

  const what = (e: RuleHistoryEntry) => e.action === 'changed'
    ? t('ruleHist_changed').replace('{name}', e.name).replace('{fields}', e.changed.map(f => t(`ruleHistField_${f}`)).join(', '))
    : t(`ruleHist_${e.action}`).replace('{name}', e.name)

  return (
    <details className="auto-rule-history" onToggle={e => setOpen((e.target as HTMLDetailsElement).open)}>
      <summary>{t('ruleHistTitle')}</summary>
      {error && <p className="error" role="alert">{error}</p>}
      {items && items.length === 0 && <p className="muted">{t('ruleHistEmpty')}</p>}
      {items && items.length > 0 && (
        <ul>
          {items.map(e => (
            <li key={e.id}>
              <span className="muted">{formatDateTime(e.at)} · {e.user || '—'}</span>{' '}
              <span>{what(e)}</span>
              {e.note && <span className="muted"> ({e.note})</span>}
              {canEdit && (
                <button type="button" className="btn small ghost" disabled={busy !== null}
                        onClick={() => restore(e)}>{t('ruleHistRestore')}</button>
              )}
            </li>
          ))}
        </ul>
      )}
    </details>
  )
}
