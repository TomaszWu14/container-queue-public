// Punktualność armatorów i „realne ETA” (trzecia lista PO, pkt 7): mediana spóźnienia armatora i portu
// z historii (pierwsze ETA vs faktyczny wyładunek) i podpowiedź realnej daty dla kontenerów w drodze.
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { formatDate, formatNum } from '../dates'
import { useT } from '../i18n'

interface CarrierRow { carrier: string; port: string; arrivals: number; median_days: number; p90_days: number; late_pct: number }
interface Forecast {
  container_id: number; container_no: string; carrier: string; port: string; eta: string
  realistic_eta: string; shift_days: number; basis: 'carrier_port' | 'carrier'; arrivals: number
}
export interface EtaReliability {
  window_days: number; min_arrivals: number; carriers: CarrierRow[]; forecasts: Forecast[]; forecast_total: number
}

const days = (n: number) => `${n > 0 ? '+' : ''}${formatNum(n)}`

export default function EtaReliabilityPanel() {
  const t = useT()
  const [data, setData] = useState<EtaReliability | null>(null)
  useEffect(() => {
    api.get<EtaReliability>('/api/automations/eta-reliability')
      .then(r => { if (Array.isArray(r?.carriers)) setData(r) }).catch(() => {})
  }, [])
  if (!data) return null

  return (
    <section className="panel" aria-label={t('etaRelTitle')} style={{ marginTop: 18 }}>
      <h2 className="as-h3" style={{ margin: 0 }}>{t('etaRelTitle')}</h2>
      <p className="muted" style={{ maxWidth: 820 }}>
        {t('etaRelIntro').replace('{n}', String(data.min_arrivals)).replace('{d}', String(data.window_days))}</p>
      {data.carriers.length === 0 ? <p className="muted">{t('etaRelEmpty')}</p> : (
        <div className="table-wrap">
          <table className="grid auto-table">
            <thead><tr>
              <th>{t('etaRelCarrier')}</th><th>{t('etaRelPort')}</th><th>{t('etaRelArrivals')}</th>
              <th>{t('etaRelMedian')}</th><th>{t('etaRelP90')}</th><th>{t('etaRelLate')}</th>
            </tr></thead>
            <tbody>
              {data.carriers.map(r => (
                <tr key={`${r.carrier}-${r.port}`}>
                  <td data-label={t('etaRelCarrier')}>{r.carrier}</td>
                  <td data-label={t('etaRelPort')}>{r.port}</td>
                  <td data-label={t('etaRelArrivals')}>{r.arrivals}</td>
                  <td data-label={t('etaRelMedian')}>{days(r.median_days)}</td>
                  <td data-label={t('etaRelP90')}>{days(r.p90_days)}</td>
                  <td data-label={t('etaRelLate')}>{r.late_pct}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {data.forecasts.length > 0 && (
        <>
          <h3 style={{ margin: "12px 0 4px", fontSize: 15 }}>
            {t('etaRelForecastTitle').replace('{n}', String(data.forecast_total))}</h3>
          <ul className="eta-forecasts">
            {data.forecasts.map(f => (
              <li key={f.container_id}>
                <Link className="mono" to={`/kontenery/${f.container_id}`}>{f.container_no}</Link>{' '}
                {t('etaRelForecast').replace('{eta}', formatDate(f.eta)).replace('{real}', formatDate(f.realistic_eta))
                  .replace('{shift}', days(f.shift_days)).replace('{carrier}', f.carrier)}
                <span className="muted"> ({t(`etaRelBasis_${f.basis}`).replace('{n}', String(f.arrivals))})</span>
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  )
}
