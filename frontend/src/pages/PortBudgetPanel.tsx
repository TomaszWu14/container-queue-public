// Budżet kosztów transportu i portu (US-084, czwarta lista PO, pkt 7): na spółkę i miesiąc — budżet (EUR),
// zużycie z faktur transportowych, prognoza do końca miesiąca i stan z ikoną (nie tylko kolor).
// Budżet zmienia admin; reszta ról z dostępem do faktur widzi podgląd.
import { TriangleAlertIcon, CircleCheckIcon, CircleXIcon, MinusIcon } from 'lucide-react'
import { useEffect, useState } from 'react'
import { api, errorMessage } from '../api'
import { useUser } from '../App'
import { formatNum } from '../dates'
import { useT } from '../i18n'

interface Row {
  company_id: number; company: string; budget_eur: number | null; spent_eur: number; forecast_eur: number
  state: 'none' | 'ok' | 'warn' | 'over'; unconverted: number
}
export interface PortBudget { month: string; day: number; days_in_month: number; warn_ratio: number; companies: Row[] }

const ICON = { none: MinusIcon, ok: CircleCheckIcon, warn: TriangleAlertIcon, over: CircleXIcon } as const
const eur = (v: number) => `${formatNum(Math.round(v))} EUR`

export default function PortBudgetPanel() {
  const t = useT()
  const isAdmin = useUser()?.role === 'admin'
  const [data, setData] = useState<PortBudget | null>(null)
  const [draft, setDraft] = useState<Record<number, string>>({})
  const [error, setError] = useState('')
  const load = () => api.get<PortBudget>('/api/budgets/port')
    .then(r => { if (Array.isArray(r?.companies)) setData(r) }).catch(() => {})
  useEffect(() => { load() }, [])

  const save = async (r: Row) => {
    setError('')
    const raw = (draft[r.company_id] ?? '').replace(',', '.').trim()
    try {
      await api.put(`/api/budgets/port/${r.company_id}`, { amount_eur: raw ? Number(raw) : null })
      setDraft(d => ({ ...d, [r.company_id]: '' }))
      load()
    } catch (err) { setError(errorMessage(err)) }
  }
  if (!data) return null
  return (
    <section className="panel" aria-label={t('budgetTitle')} style={{ marginBottom: 14 }}>
      <h3 style={{ marginTop: 0 }}>{t('budgetTitle')} · {data.month}</h3>
      <p className="muted" style={{ maxWidth: 820 }}>
        {t('budgetIntro').replace('{day}', String(data.day)).replace('{days}', String(data.days_in_month))
          .replace('{pct}', String(Math.round(data.warn_ratio * 100)))}
      </p>
      {error && <p className="error">{error}</p>}
      <div className="table-wrap">
        <table className="grid">
          <thead><tr>
            <th>{t('budgetColCompany')}</th><th>{t('budgetColBudget')}</th><th>{t('budgetColSpent')}</th>
            <th>{t('budgetColForecast')}</th><th>{t('budgetColState')}</th>{isAdmin && <th />}
          </tr></thead>
          <tbody>
            {data.companies.map(r => (
              <tr key={r.company_id} data-state={r.state}>
                <td data-label={t('budgetColCompany')}><b>{r.company}</b></td>
                <td data-label={t('budgetColBudget')}>{r.budget_eur === null ? '—' : eur(r.budget_eur)}</td>
                <td data-label={t('budgetColSpent')}>
                  {eur(r.spent_eur)}
                  {r.unconverted > 0 && <div className="muted">{t('budgetUnconverted').replace('{n}', String(r.unconverted))}</div>}
                </td>
                <td data-label={t('budgetColForecast')}>{eur(r.forecast_eur)}</td>
                <td data-label={t('budgetColState')}>{(() => { const Icon = ICON[r.state]; return <Icon size={14} aria-hidden="true" /> })()} {t(`budgetState_${r.state}`)}</td>
                {isAdmin && (
                  <td>
                    <input aria-label={`${t('budgetColBudget')} — ${r.company}`} inputMode="decimal" style={{ width: 110 }}
                           placeholder={r.budget_eur === null ? 'EUR' : String(r.budget_eur)}
                           value={draft[r.company_id] ?? ''}
                           onChange={e => setDraft(d => ({ ...d, [r.company_id]: e.target.value }))} />
                    {' '}
                    <button type="button" className="btn small" onClick={() => void save(r)}>{t('budgetSave')}</button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
