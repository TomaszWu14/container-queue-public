// „Jak to zbudowano” (pomysł 6 PO): most między rekruterem a programistą — architektura, liczby
// jakości i kluczowe decyzje z linkami do dokumentów w repozytorium. Treść statyczna (bez API).
import { PageHeader } from '../PageHeader'
import { useT } from '../i18n'
import ProjectMetrics from './ProjectMetrics'

export const REPO = 'https://github.com/TomaszWu14/container-queue-public'
const doc = (path: string) => `${REPO}/blob/main/${path}`

const LAYERS: [string, string][] = [
  ['hbLayerUi', 'React 19 · TypeScript · Vite'],
  ['hbLayerApi', 'FastAPI · SQLAlchemy 2 · Alembic'],
  ['hbLayerDb', 'PostgreSQL 16'],
]
const SIDE = ['hbSideMail', 'hbSideN8n', 'hbSideAis', 'hbSideDeploy']
const FACTS: [string, string][] = [
  ['3000+', 'hbFactTests'], ['≥ 92%', 'hbFactCoverage'], ['5', 'hbFactScans'],
  ['PL · EN · PT', 'hbFactLangs'], ['500', 'hbFactLines'],
]
const DECISIONS: [string, string, string][] = [   // [tytuł, opis, dokument] — klucze w pełnej postaci
  ['hbDecIsolationTitle', 'hbDecIsolationBody', doc('docs/06-decyzje.md')],
  ['hbDecWarnTitle', 'hbDecWarnBody', doc('docs/06-decyzje.md')],
  ['hbDecLostUpdateTitle', 'hbDecLostUpdateBody', doc('docs/architektura/adr/0003-oczekiwany-status-przy-zmianie-statusu.md')],
  ['hbDecLinksTitle', 'hbDecLinksBody', doc('docs/06-decyzje.md')],
  ['hbDecProcessTitle', 'hbDecProcessBody', doc('docs/architektura/adr/0002-proces-zespolowy-ba-dev-sec.md')],
  ['hbDecThreatsTitle', 'hbDecThreatsBody', doc('docs/bezpieczenstwo/THREAT_MODEL.md')],
]

export default function HowBuiltPage() {
  const t = useT()
  return (
    <main className="page how-built">
      <PageHeader title={t('hbTitle')} />
      <p className="muted" style={{ maxWidth: 760 }}>{t('hbIntro')}</p>

      <section className="panel">
        <h2 className="as-h3">{t('hbArchitecture')}</h2>
        <div className="hb-arch">
          <div className="hb-stack">
            {LAYERS.map(([key, tech], i) => (
              <div key={key}>
                <div className="hb-box"><b>{t(key)}</b><span className="muted">{tech}</span></div>
                {i < LAYERS.length - 1 && <div className="hb-arrow" aria-hidden="true">↓</div>}
              </div>
            ))}
          </div>
          <ul className="hb-side">{SIDE.map(k => <li key={k} className="hb-box small">{t(k)}</li>)}</ul>
        </div>
      </section>

      <section className="panel">
        <h2 className="as-h3">{t('hbQuality')}</h2>
        <div className="ctl-kpis">
          {FACTS.map(([value, key]) => (
            <div key={key} className="ctl-kpi plain">
              <div className="ctl-kpi-value">{value}</div>
              <div className="ctl-kpi-sub">{t(key)}</div>
            </div>
          ))}
        </div>
      </section>

      <ProjectMetrics />

      <section className="panel">
        <h2 className="as-h3">{t('hbDecisions')}</h2>
        <ol className="hb-decisions">
          {DECISIONS.map(([title, body, href]) => (
            <li key={title}>
              <b>{t(title)}</b>
              <p>{t(body)} <a href={href} target="_blank" rel="noopener noreferrer">{t('hbMore')} ↗</a></p>
            </li>
          ))}
        </ol>
      </section>
    </main>
  )
}
