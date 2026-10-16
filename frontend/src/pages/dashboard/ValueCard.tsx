import { useEffect, useState } from 'react'
import { api } from '../../api'
import { useT } from '../../i18n'

// Panel „Ile to oszczędza” (pomysł 2 PO): wartość aplikacji z jej własnych danych za 30 dni.
// Jedyne założenie (minuty na zmianę) pokazujemy wprost pod liczbą — bez „magicznych” wyliczeń.
export type ValueStats = {
  days: number; changes: number; minutes_per_change: number; hours_saved: number
  delivered: number; delivered_on_time: number; docs_in_flow: number; docs_complete: number
  demurrage_warned: number
}

const pct = (part: number, whole: number) => (whole ? Math.round((part / whole) * 100) : null)

export default function ValueCard() {
  const t = useT()
  const [v, setV] = useState<ValueStats | null>(null)
  useEffect(() => {
    api.get<ValueStats>('/api/stats/value')
      .then(r => setV(r && typeof r.changes === 'number' ? r : null)).catch(() => setV(null))
  }, [])
  if (!v) return null
  const onTime = pct(v.delivered_on_time, v.delivered)
  const docs = pct(v.docs_complete, v.docs_in_flow)
  const fill = (key: string, vars: Record<string, string | number>) =>
    Object.entries(vars).reduce((s, [k, val]) => s.replace(`{${k}}`, String(val)), t(key))
  return (
    <section className="panel value-card" aria-label={t('valueTitle')}>
      <div className="dash-card-head">
        <span className="dash-card-title">{t('valueTitle')}</span>
        <span className="muted" style={{ fontSize: 12 }}>{fill('valuePeriod', { days: v.days })}</span>
      </div>
      <div className="ctl-kpis">
        <div className="ctl-kpi plain">
          <div className="ctl-kpi-label">{t('valueHours')}</div>
          <div className="ctl-kpi-value">≈ {v.hours_saved} h</div>
          <div className="ctl-kpi-sub">{fill('valueHoursSub', { n: v.changes, m: v.minutes_per_change })}</div>
        </div>
        <div className="ctl-kpi sky">
          <div className="ctl-kpi-label">{t('valueOnTime')}</div>
          <div className="ctl-kpi-value">{onTime === null ? '—' : `${onTime}%`}</div>
          <div className="ctl-kpi-sub">{fill('valueOfDelivered', { a: v.delivered_on_time, b: v.delivered })}</div>
        </div>
        <div className="ctl-kpi sky">
          <div className="ctl-kpi-label">{t('valueDocs')}</div>
          <div className="ctl-kpi-value">{docs === null ? '—' : `${docs}%`}</div>
          <div className="ctl-kpi-sub">{fill('valueOfContainers', { a: v.docs_complete, b: v.docs_in_flow })}</div>
        </div>
        <div className="ctl-kpi amber">
          <div className="ctl-kpi-label">{t('valueDemurrage')}</div>
          <div className="ctl-kpi-value">{v.demurrage_warned}</div>
          <div className="ctl-kpi-sub">{t('valueDemurrageSub')}</div>
        </div>
      </div>
    </section>
  )
}
