import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../../api'
import { formatDate } from '../../dates'
import { useT } from '../../i18n'

// Ryzyko kary za przestój z wyjaśnieniem (pomysł 10 PO): dlaczego grozi kara i co zrobić.
// Reguły i dane: GET /api/stats/demurrage-risk (backend/app/demurrage_risk.py). Bez kwot — stawek
// armatorów aplikacja nie przechowuje.
export type DemurrageRisk = {
  container_id: number; container_no: string; deadline: string; planned: string | null
  days_left: number; days_over: number; reason: 'planned_after_deadline' | 'unplanned_near_deadline'
}

export function riskText(r: DemurrageRisk, t: (k: string) => string): string {
  const vars: Record<string, string> = {
    deadline: formatDate(r.deadline), planned: r.planned ? formatDate(r.planned) : '',
    n: String(r.days_over), left: String(r.days_left),
  }
  const key = r.reason === 'planned_after_deadline' ? 'riskPlannedAfter'
    : r.days_left < 0 ? 'riskUnplannedOver' : 'riskUnplannedNear'
  return Object.entries(vars).reduce((s, [k, v]) => s.split(`{${k}}`).join(v), t(key))
}

export default function DemurrageRiskCard() {
  const t = useT()
  const [rows, setRows] = useState<DemurrageRisk[] | null>(null)
  useEffect(() => {
    api.get<DemurrageRisk[]>('/api/stats/demurrage-risk?limit=8')
      .then(r => setRows(Array.isArray(r) ? r : null)).catch(() => setRows(null))   // nie-lista = brak karty
  }, [])
  if (!rows || rows.length === 0) return null
  return (
    <section className="panel risk-card" aria-label={t('riskTitle')}>
      <div className="dash-card-head">
        <span className="dash-card-title">{t('riskTitle')}</span>
        <span className="count-chip">{rows.length}</span>
      </div>
      <ul className="risk-list">
        {rows.map(r => (
          <li key={r.container_id}>
            <Link to={`/kontenery/${r.container_id}`} className="mono">{r.container_no}</Link>
            <span>{riskText(r, t)}</span>
          </li>
        ))}
      </ul>
    </section>
  )
}
