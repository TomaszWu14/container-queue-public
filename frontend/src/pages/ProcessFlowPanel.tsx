// Przebieg procesu z historii statusów (US-038, „process mining”): ile dni kontener zwykle stoi
// w każdym etapie (mediana i 90. percentyl), ile było cofnięć statusu i które kontenery stoją
// w obecnym etapie dłużej niż zwykle. Dane z dziennika zmian — nic nie trzeba wpisywać ręcznie.
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { useT } from '../i18n'
import ProcessFlowChart, { type Transition } from './ProcessFlowChart'

interface Stage { status: string; count: number; median_days: number | null; p90_days: number | null }
interface Stuck { id: number; container_no: string; status: string; days_in_stage: number; p90_days: number }
export interface ProcessFlow {
  days: number
  min_samples: number
  transitions_total: number
  backward: number
  backward_pct: number | null
  stages: Stage[]
  top_transitions: Transition[]
  transitions?: Transition[]
  stuck_total: number
  stuck: Stuck[]
}

export default function ProcessFlowPanel() {
  const t = useT()
  const [p, setP] = useState<ProcessFlow | null>(null)
  useEffect(() => {
    api.get<ProcessFlow>('/api/automations/process')
      .then(r => setP(r && Array.isArray(r.stages) ? r : null)).catch(() => setP(null))
  }, [])
  if (!p) return null
  const fill = (key: string, vars: Record<string, string | number>) =>
    Object.entries(vars).reduce((s, [k, v]) => s.replace(`{${k}}`, String(v)), t(key))
  const day = (v: number | null) => (v == null ? '—' : fill('procDays', { n: v }))
  const scale = Math.max(1, ...p.stages.map(s => s.p90_days ?? 0))
  const measured = p.stages.filter(s => s.count > 0)

  return (
    <section className="panel proc" aria-label={t('procTitle')} style={{ marginTop: 18 }}>
      <h2 className="as-h3">{t('procTitle')}</h2>
      <p className="muted" style={{ marginTop: 0, maxWidth: 820 }}>{t('procIntro')}</p>
      <div className="ctl-kpis">
        <div className="ctl-kpi plain"><div className="ctl-kpi-value">{p.transitions_total}</div>
          <div className="ctl-kpi-sub">{fill('procTransitions', { days: p.days })}</div></div>
        <div className={`ctl-kpi ${p.backward ? 'amber' : 'plain'}`}>
          <div className="ctl-kpi-value">{p.backward_pct == null ? '—' : `${p.backward_pct}%`}</div>
          <div className="ctl-kpi-sub">{fill('procBackward', { n: p.backward })}</div></div>
        <div className={`ctl-kpi ${p.stuck_total ? 'danger' : 'plain'}`}>
          <div className="ctl-kpi-value">{p.stuck_total}</div>
          <div className="ctl-kpi-sub">{t('procStuckKpi')}</div></div>
      </div>

      {measured.length === 0 ? <p className="muted">{t('procEmpty')}</p> : (
        <>
          <h3 className="aiq-sub">{t('procStages')}</h3>
          <div style={{ overflowX: 'auto' }}>
            <table className="grid proc-table">
              <thead><tr>
                <th>{t('procColStage')}</th><th>{t('procColCount')}</th><th>{t('procColMedian')}</th>
                <th>{t('procColP90')}</th><th aria-hidden="true" />
              </tr></thead>
              <tbody>
                {measured.map(s => (
                  <tr key={s.status}>
                    <td>{t(`st_${s.status}`)}</td>
                    <td data-label={t('procColCount')}>{s.count}</td>
                    <td data-label={t('procColMedian')}>{day(s.median_days)}</td>
                    <td data-label={t('procColP90')}>{day(s.p90_days)}</td>
                    <td aria-hidden="true" className="proc-bar-cell">
                      <span className="proc-bar">
                        <span className="proc-p90" style={{ width: `${(100 * (s.p90_days ?? 0)) / scale}%` }} />
                        <span className="proc-median" style={{ width: `${(100 * (s.median_days ?? 0)) / scale}%` }} />
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="muted" style={{ fontSize: 12, margin: '6px 0 0' }}>{t('procLegend')}</p>

          {(p.transitions?.length ?? 0) > 0 && (
            <>
              <h3 className="aiq-sub">{t('procFlowTitle')}</h3>
              <ProcessFlowChart transitions={p.transitions ?? []} order={p.stages.map(s => s.status).concat('ZREALIZOWANY')} />
            </>
          )}
          {p.top_transitions.length > 0 && (
            <>
              <h3 className="aiq-sub">{t('procTop')}</h3>
              <ul className="proc-transitions">
                {p.top_transitions.map(x => (
                  <li key={`${x.from}-${x.to}`}>{t(`st_${x.from}`)} → {t(`st_${x.to}`)}: <b>{x.count}</b></li>
                ))}
              </ul>
            </>
          )}

          <h3 className="aiq-sub">{t('procStuckTitle')}</h3>
          {p.stuck.length === 0 ? <p className="muted">{fill('procStuckNone', { n: p.min_samples })}</p> : (
            <div style={{ overflowX: 'auto' }}>
              <table className="grid proc-table">
                <thead><tr>
                  <th>{t('procColContainer')}</th><th>{t('procColStage')}</th>
                  <th>{t('procColInStage')}</th><th>{t('procColP90')}</th>
                </tr></thead>
                <tbody>
                  {p.stuck.map(s => (
                    <tr key={s.id}>
                      <td className="mono"><Link to={`/kontenery/${s.id}`}>{s.container_no || `#${s.id}`}</Link></td>
                      <td data-label={t('procColStage')}>{t(`st_${s.status}`)}</td>
                      <td data-label={t('procColInStage')}><b>{day(s.days_in_stage)}</b></td>
                      <td data-label={t('procColP90')}>{day(s.p90_days)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </section>
  )
}
