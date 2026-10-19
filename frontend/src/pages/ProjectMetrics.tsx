// Metryki projektu (US-080, czwarta lista PO, pkt 13): liczby policzone z repozytorium skryptem
// `scripts/project_metrics.py` (testy, trasy API, historyjki, ADR, PR-y) — z datą, kiedy je policzono.
import metrics from '../data/projectMetrics.json'
import { formatDate } from '../dates'
import { useT } from '../i18n'

export const METRICS: [keyof typeof metrics, string][] = [
  ['backend_tests', 'pmBackendTests'], ['frontend_tests', 'pmFrontendTests'], ['e2e_tests', 'pmE2eTests'],
  ['api_operations', 'pmApiOps'], ['stories_shipped', 'pmStories'], ['adrs', 'pmAdrs'], ['last_pr', 'pmPrs'],
]

export default function ProjectMetrics() {
  const t = useT()
  return (
    <section className="panel" aria-label={t('pmTitle')}>
      <h2 className="as-h3">{t('pmTitle')}</h2>
      <p className="muted">{t('pmIntro').replace('{date}', formatDate(metrics.generated_at))}</p>
      <div className="ctl-kpis">
        {METRICS.map(([field, key]) => (
          <div key={field} className="ctl-kpi plain">
            <div className="ctl-kpi-value">{String(metrics[field])}</div>
            <div className="ctl-kpi-sub">{t(key)}</div>
          </div>
        ))}
      </div>
    </section>
  )
}
