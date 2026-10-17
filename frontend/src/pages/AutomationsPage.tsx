// Ekran „Automatyzacje” (US-032, US-033): katalog wszystkiego, co aplikacja robi sama — wyzwalacz,
// akcja, stan z dziennika zadań (błąd / spóźnienie / wyłączony) i liczniki z ostatnich dni.
// Opisy automatów w i18n/features/automatyzacje.ts (klucz = `key` z backend/app/automation_catalog.py).
import { useContext, useEffect, useMemo, useState } from 'react'
import { api, errorMessage } from '../api'
import { relTime } from '../dates'
import { LangContext, useT } from '../i18n'
import { PageHeader } from '../PageHeader'

type Status = 'ok' | 'late' | 'error' | 'unknown' | 'off'
type Category = 'alerts' | 'documents' | 'communication' | 'data' | 'integrations'

export interface AutomationItem {
  key: string
  category: Category
  kind: 'schedule' | 'event'
  status: Status
  interval_s: number | null
  last_run_at: string | null
  last_ok_at: string | null
  runs: number | null
  errors: number | null
  effects: number | null
}

export interface AutomationCatalog {
  window_days: number
  items: AutomationItem[]
  summary: { total: number; active: number; attention: number; runs: number; effects: number }
}

const CATEGORIES: Category[] = ['alerts', 'documents', 'communication', 'data', 'integrations']
const STATUS_CLASS: Record<Status, string> = {
  ok: 'cs-ODPRAWIONY', late: 'cs-ZLECONA', error: 'cs-REWIZJA', unknown: 'cs-BRAK', off: 'cs-BRAK',
}
const ATTENTION: Status[] = ['error', 'late']

export default function AutomationsPage() {
  const t = useT()
  const { lang } = useContext(LangContext)
  const [data, setData] = useState<AutomationCatalog | null>(null)
  const [error, setError] = useState('')
  const [category, setCategory] = useState<Category | ''>('')
  const [onlyAttention, setOnlyAttention] = useState(false)

  useEffect(() => {
    api.get<AutomationCatalog>('/api/automations').then(setData).catch(err => setError(errorMessage(err)))
  }, [])

  const fill = (key: string, vars: Record<string, string | number>) =>
    Object.entries(vars).reduce((s, [k, v]) => s.replace(`{${k}}`, String(v)), t(key))

  const items = useMemo(() => (data?.items ?? []).filter(i =>
    (!category || i.category === category) && (!onlyAttention || ATTENTION.includes(i.status))),
  [data, category, onlyAttention])

  const cadence = (i: AutomationItem) => {
    if (i.kind === 'event') return t('autoOnEvent')
    const s = i.interval_s
    if (s == null) return t('autoNever')
    if (s < 60) return fill('autoEverySec', { n: s })
    return s >= 3600 && s % 3600 === 0 ? fill('autoEveryH', { n: s / 3600 }) : fill('autoEvery', { n: Math.round(s / 60) })
  }
  const num = (n: number | null) => (n == null ? t('autoNever') : String(n))

  return (
    <main className="page automations">
      <PageHeader title={t('autoTitle')} />
      <p className="muted" style={{ maxWidth: 820 }}>{t('autoIntro')}</p>
      {error && <p className="error">{error}</p>}
      {data && (
        <>
          <section className="ctl-kpis" aria-label={t('autoTitle')}>
            <div className="ctl-kpi plain"><div className="ctl-kpi-value">{data.summary.total}</div>
              <div className="ctl-kpi-sub">{t('autoKpiTotal')}</div></div>
            <div className="ctl-kpi sky"><div className="ctl-kpi-value">{data.summary.active}</div>
              <div className="ctl-kpi-sub">{t('autoKpiActive')}</div></div>
            <div className={`ctl-kpi ${data.summary.attention ? 'danger' : 'plain'}`}>
              <div className="ctl-kpi-value">{data.summary.attention}</div>
              <div className="ctl-kpi-sub">{t('autoKpiAttention')}</div></div>
            <div className="ctl-kpi plain"><div className="ctl-kpi-value">{data.summary.runs}</div>
              <div className="ctl-kpi-sub">{fill('autoKpiRuns', { days: data.window_days })}</div></div>
            <div className="ctl-kpi plain"><div className="ctl-kpi-value">{data.summary.effects}</div>
              <div className="ctl-kpi-sub">{fill('autoKpiEffects', { days: data.window_days })}</div></div>
          </section>

          <div className="row" style={{ gap: 8, flexWrap: 'wrap', margin: '16px 0 8px' }}>
            <select aria-label={t('autoColName')} value={category}
                    onChange={e => setCategory(e.target.value as Category | '')}>
              <option value="">{t('autoFilterAll')}</option>
              {CATEGORIES.map(c => <option key={c} value={c}>{t(`autoCat_${c}`)}</option>)}
            </select>
            <label className="row" style={{ gap: 6, fontSize: 14 }}>
              <input type="checkbox" checked={onlyAttention} onChange={e => setOnlyAttention(e.target.checked)} />
              {t('autoOnlyAttention')}
            </label>
          </div>

          {items.length === 0 ? <p className="muted">{t('autoEmpty')}</p> : (
            <div style={{ overflowX: 'auto' }}>
              <table className="grid auto-table">
                <thead>
                  <tr>
                    <th>{t('autoColName')}</th><th>{t('autoColTrigger')}</th><th>{t('autoColAction')}</th>
                    <th>{t('autoColStatus')}</th><th>{t('autoColLast')}</th>
                    <th>{t('autoColRuns')}</th><th>{t('autoColErrors')}</th><th>{t('autoColEffects')}</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map(i => (
                    <tr key={i.key} data-status={i.status}>
                      <td><b>{t(`autoName_${i.key}`)}</b>
                        <div className="muted" style={{ fontSize: 12 }}>{t(`autoCat_${i.category}`)} · {cadence(i)}</div></td>
                      <td data-label={t('autoColTrigger')}>{t(`autoTrigger_${i.key}`)}</td>
                      <td data-label={t('autoColAction')}>{t(`autoAction_${i.key}`)}</td>
                      <td data-label={t('autoColStatus')}><span className={`badge ${STATUS_CLASS[i.status]}`}
                                title={i.status === 'ok' ? undefined : t(`autoStatusHint_${i.status}`)}>
                        {t(`autoStatus_${i.status}`)}</span></td>
                      <td data-label={t('autoColLast')}>{i.last_run_at ? relTime(i.last_run_at, lang) : t('autoNever')}</td>
                      <td data-label={t('autoColRuns')}>{num(i.runs)}</td>
                      <td data-label={t('autoColErrors')}>{num(i.errors)}</td>
                      <td data-label={t('autoColEffects')}>{num(i.effects)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </main>
  )
}
