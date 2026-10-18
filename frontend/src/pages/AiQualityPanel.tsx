// Jakość odczytu faktur (US-037): ile pozycji dopasowały reguły, model ML i człowiek (tydzień po
// tygodniu, słupki 100%) oraz trafność podpowiedzi modelu wg jego pewności (tabela kalibracji).
// Kolory serii z palety pulpitu analitycznego (--viz-*, sprawdzona pod daltonizm, wariant ciemny).
import { useEffect, useState } from 'react'
import { api } from '../api'
import { formatDate } from '../dates'
import { useT } from '../i18n'
import AiMistakesTable from './AiMistakesTable'

type Source = 'rules' | 'ml' | 'user' | 'open'
const SOURCES: Source[] = ['rules', 'ml', 'user', 'open']
interface Week { week: string; rules: number; ml: number; user: number; open: number }
interface Bucket { bucket: 'low' | 'high' | 'auto'; suggested: number; decided: number; hits: number; hit_pct: number | null }
export interface AiQuality {
  weeks: Week[]
  totals: Record<Source, number> & { items: number }
  automated_pct: number | null
  ml_hit_pct: number | null
  threshold: number
  buckets: Bucket[]
}

export default function AiQualityPanel() {
  const t = useT()
  const [q, setQ] = useState<AiQuality | null>(null)
  useEffect(() => {
    api.get<AiQuality>('/api/automations/ai-quality')
      .then(r => setQ(r && Array.isArray(r.weeks) ? r : null)).catch(() => setQ(null))
  }, [])
  if (!q) return null
  const fill = (key: string, vars: Record<string, string | number>) =>
    Object.entries(vars).reduce((s, [k, v]) => s.replace(`{${k}}`, String(v)), t(key))
  const pct = (v: number | null) => (v == null ? t('aiqNone') : `${v}%`)

  return (
    <section className="panel aiq" aria-label={t('aiqTitle')} style={{ marginTop: 18 }}>
      <h2 className="as-h3">{t('aiqTitle')}</h2>
      <p className="muted" style={{ marginTop: 0, maxWidth: 820 }}>{t('aiqIntro')}</p>
      <div className="ctl-kpis">
        <div className="ctl-kpi sky"><div className="ctl-kpi-value">{pct(q.automated_pct)}</div>
          <div className="ctl-kpi-sub">{t('aiqAutomated')}</div></div>
        <div className="ctl-kpi plain"><div className="ctl-kpi-value">{pct(q.ml_hit_pct)}</div>
          <div className="ctl-kpi-sub">{t('aiqHit')}</div></div>
        <div className="ctl-kpi plain"><div className="ctl-kpi-value">{q.totals.items}</div>
          <div className="ctl-kpi-sub">{fill('aiqItems', { weeks: q.weeks.length })}</div></div>
      </div>

      {q.totals.items === 0 ? <p className="muted">{t('aiqEmpty')}</p> : (
        <>
          <h3 className="aiq-sub">{t('aiqWeekly')}</h3>
          <ul className="aiq-legend" aria-hidden="true">
            {SOURCES.map(s => <li key={s}><span className={`aiq-swatch src-${s}`} />{t(`aiqSrc_${s}`)}</li>)}
          </ul>
          <div className="aiq-bars" role="list">
            {q.weeks.map(w => {
              const total = SOURCES.reduce((n, s) => n + w[s], 0)
              const label = `${fill('aiqWeekOf', { d: formatDate(w.week) })}: `
                + SOURCES.map(s => `${t(`aiqSrc_${s}`)} ${w[s]}`).join(', ')
              return (
                <div key={w.week} className="aiq-bar-col" role="listitem" title={label} aria-label={label}>
                  <div className="aiq-bar">
                    {total > 0 && SOURCES.filter(s => w[s] > 0).map(s => (
                      <span key={s} className={`aiq-seg src-${s}`} style={{ flexGrow: w[s] }} />
                    ))}
                  </div>
                  <span className="aiq-bar-label">{formatDate(w.week).slice(0, 5)}</span>
                </div>
              )
            })}
          </div>

          <h3 className="aiq-sub">{t('aiqCalibration')}</h3>
          <div style={{ overflowX: 'auto' }}>
            <table className="grid">
              <thead><tr>
                <th>{t('aiqColBucket')}</th><th>{t('aiqColSuggested')}</th><th>{t('aiqColDecided')}</th>
                <th>{t('aiqColHits')}</th><th>{t('aiqColHitPct')}</th>
              </tr></thead>
              <tbody>
                {q.buckets.map(b => (
                  <tr key={b.bucket}>
                    <td>{fill(`aiqBucket_${b.bucket}`, { t: Math.round(q.threshold * 100) })}</td>
                    <td>{b.suggested}</td><td>{b.decided}</td><td>{b.hits}</td><td>{pct(b.hit_pct)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <AiMistakesTable />
        </>
      )}
    </section>
  )
}
