// Karta spedytora (US-079, czwarta lista PO, pkt 5): jak szybko i jak dobrze spedycje odpowiadają na awizacje
// w ostatnich 90 dniach — ranking po odsetku odpowiedzi na czas (24 h, Z-042), potem po medianie czasu odpowiedzi.
import { useEffect, useState } from 'react'
import { api } from '../api'
import { formatNum } from '../dates'
import { useT } from '../i18n'

interface Row {
  forwarder: string; requests: number; answered: number; median_hours: number | null; on_time_pct: number | null
  date_change_pct: number | null; problem_pct: number | null; rejected: number
}
export interface Scorecard { window_days: number; on_time_hours: number; forwarders: Row[] }

const pct = (v: number | null) => (v === null ? '—' : `${formatNum(v)}%`)

export default function ForwarderScorecardPanel() {
  const t = useT()
  const [data, setData] = useState<Scorecard | null>(null)
  useEffect(() => {
    api.get<Scorecard>('/api/automations/forwarder-scorecard')
      .then(r => { if (Array.isArray(r?.forwarders)) setData(r) }).catch(() => {})
  }, [])
  if (!data) return null
  return (
    <section className="panel" aria-label={t('fwdScoreTitle')} style={{ marginTop: 18 }}>
      <h2 className="as-h3" style={{ margin: 0 }}>{t('fwdScoreTitle')}</h2>
      <p className="muted" style={{ maxWidth: 820 }}>
        {t('fwdScoreIntro').replace('{days}', String(data.window_days)).replace('{hours}', String(data.on_time_hours))}
      </p>
      {data.forwarders.length === 0 ? <p className="muted">{t('fwdScoreEmpty')}</p> : (
        <div className="table-wrap">
          <table className="grid auto-table">
            <thead><tr>
              <th>#</th><th>{t('fwdScoreColName')}</th><th>{t('fwdScoreColRequests')}</th>
              <th>{t('fwdScoreColOnTime').replace('{hours}', String(data.on_time_hours))}</th>
              <th>{t('fwdScoreColMedian')}</th><th>{t('fwdScoreColDateChange')}</th>
              <th>{t('fwdScoreColProblem')}</th><th>{t('fwdScoreColRejected')}</th>
            </tr></thead>
            <tbody>
              {data.forwarders.map((r, i) => (
                <tr key={r.forwarder}>
                  <td>{i + 1}</td>
                  <td data-label={t('fwdScoreColName')}><b>{r.forwarder}</b></td>
                  <td data-label={t('fwdScoreColRequests')}>{r.answered} / {r.requests}</td>
                  <td data-label={t('fwdScoreColOnTime').replace('{hours}', String(data.on_time_hours))}>{pct(r.on_time_pct)}</td>
                  <td data-label={t('fwdScoreColMedian')}>{r.median_hours === null ? '—' : `${formatNum(r.median_hours)} h`}</td>
                  <td data-label={t('fwdScoreColDateChange')}>{pct(r.date_change_pct)}</td>
                  <td data-label={t('fwdScoreColProblem')}>{pct(r.problem_pct)}</td>
                  <td data-label={t('fwdScoreColRejected')}>{r.rejected}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
