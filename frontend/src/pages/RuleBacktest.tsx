// „Ile alertów wysłałaby ta reguła?” (trzecia lista PO, pkt 2): test na ostatnich 30 dniach, zanim reguła
// zacznie wysyłać — chroni przed regułą, która zasypie ludzi powiadomieniami. Tylko odczyt.
import { useState } from 'react'
import { api, errorMessage } from '../api'
import { useT } from '../i18n'

export interface Backtest {
  days: number; alerts: number; containers: number; avg_per_day: number; max_per_day: number
  per_day: { day: string; alerts: number }[]
}

export const NOISY_PER_DAY = 10

export default function RuleBacktest({ condition, days, status }: {
  condition: string; days: number; status: string | null
}) {
  const t = useT()
  const [res, setRes] = useState<Backtest | string | null>(null)
  const [busy, setBusy] = useState(false)
  const fill = (key: string, vars: Record<string, string | number>) =>
    Object.entries(vars).reduce((s, [k, v]) => s.replace(`{${k}}`, String(v)), t(key))

  const run = async () => {
    setBusy(true)
    const q = new URLSearchParams({ condition, days: String(days) })
    if (status) q.set('status', status)
    try {
      setRes(await api.get<Backtest>(`/api/automations/rules/backtest?${q}`))
    } catch (err) {
      setRes(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <>
      <button type="button" className="btn secondary small" onClick={run} disabled={busy}>
        {busy ? t('loading') : t('ruleBacktest')}</button>
      {typeof res === 'string' && <span className="error">{res}</span>}
      {res && typeof res !== 'string' && (
        <span role="status" className={res.avg_per_day >= NOISY_PER_DAY ? 'whatif-cost' : undefined}>
          {res.alerts
            ? fill('ruleBacktestResult', { d: res.days, n: res.alerts, c: res.containers, avg: res.avg_per_day, max: res.max_per_day })
            : fill('ruleBacktestNone', { d: res.days })}
          {res.avg_per_day >= NOISY_PER_DAY && ` ${t('ruleBacktestNoisy')}`}
        </span>
      )}
    </>
  )
}
