import { useT } from '../../i18n'

// Przepływ kontenerów przez 9 etapów procesu (strzałki), pogrupowanych w 4 fazy. Pod liczbą pasek
// udziału względem najliczniejszego etapu (jedna barwa = wielkość); najliczniejszy etap wyróżniony
// i nazwany w podpisie — tam zwykle jest wąskie gardło.
export type Stage = { status: string; count: number }

const PHASES: { key: string; span: number }[] = [
  { key: 'anaPhaseBuy', span: 3 }, { key: 'anaPhaseSea', span: 1 },
  { key: 'anaPhasePort', span: 2 }, { key: 'anaPhaseDelivery', span: 3 },
]

const bare = (label: string) => label.replace(/^\d+\s*·\s*/, '')

export default function ProcessFlow({ stages }: { stages: Stage[] }) {
  const t = useT()
  const max = Math.max(1, ...stages.map(s => s.count))
  // wyróżniamy tylko jednoznaczny szczyt — przy remisie „najwięcej” nic nie mówi
  const peak = stages.reduce((best, s) => (s.count > best.count ? s : best), stages[0])
  const top = peak && peak.count > 0 && stages.filter(s => s.count === peak.count).length === 1 ? peak : null
  const phaseLabel: Record<string, string> = {
    anaPhaseBuy: t('anaPhaseBuy'), anaPhaseSea: t('anaPhaseSea'),
    anaPhasePort: t('anaPhasePort'), anaPhaseDelivery: t('anaPhaseDelivery'),
  }
  return (
    <section className="panel ana-card ana-flow-card" aria-label={t('anaFlowTitle')}>
      <div className="ana-card-title">{t('anaFlowTitle')}</div>
      {top && (
        <div className="ana-sub">
          {t('anaFlowHint').replace('{stage}', bare(t(`st_${top.status}`))).replace('{n}', String(top.count))}
        </div>
      )}
      <div className="ana-flow">
        {PHASES.map(p => (
          <div key={p.key} className="ana-phase" style={{ gridColumn: `span ${p.span}` }}>{phaseLabel[p.key]}</div>
        ))}
        {stages.map((s, i) => (
          <div key={s.status} className={`ana-step${s === top ? ' top' : ''}${s.count ? '' : ' zero'}`}
               title={`${t(`st_${s.status}`)}: ${s.count}`}>
            <div className="ana-step-head">
              <span className="ana-step-no">{i + 1}</span>
              <span className="ana-step-name">{bare(t(`st_${s.status}`))}</span>
            </div>
            <div className="ana-step-count">{s.count}</div>
            <div className="ana-step-track" aria-hidden="true">
              <div className="ana-step-bar" style={{ width: `${(s.count / max) * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
