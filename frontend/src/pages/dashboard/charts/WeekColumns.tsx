import { formatDate } from '../../../dates'
import { useT } from '../../../i18n'

// Kolumny: rozładunki (data awizacji) w tygodniach — minione pełnym kolorem, zaplanowane kreskowaniem
// (druga cecha poza kolorem), bieżący tydzień akcentem. Liczby wprost tylko przy bieżącym i szczytowym
// tygodniu; reszta w podpowiedzi po najechaniu / fokusie.
export type Week = { week: string; count: number; current: boolean }

export default function WeekColumns({ weeks }: { weeks: Week[] }) {
  const t = useT()
  const max = Math.max(1, ...weeks.map(w => w.count))
  const peak = weeks.reduce((best, w) => (w.count > best.count ? w : best), weeks[0])
  const currentAt = weeks.findIndex(w => w.current)
  const tip = (w: Week) => t('anaWeekTip').replace('{date}', formatDate(w.week)).replace('{n}', String(w.count))
  return (
    <section className="panel ana-card ana-weeks" aria-label={t('anaWeeksTitle')}>
      <div className="ana-card-head">
        <div className="ana-card-title">{t('anaWeeksTitle')}</div>
        <div className="ana-key">
          <span><i className="ana-swatch tone-done" aria-hidden="true" />{t('anaWeekDone')}</span>
          <span><i className="ana-swatch tone-planned" aria-hidden="true" />{t('anaWeekPlanned')}</span>
        </div>
      </div>
      <div className="ana-cols" role="list">
        {weeks.map((w, i) => {
          const kind = w.current ? 'now' : i < currentAt ? 'done' : 'planned'
          const labelled = w.current || (w === peak && w.count > 0)
          return (
            <div key={w.week} className={`ana-col ${kind}`} role="listitem" tabIndex={0} aria-label={tip(w)}>
              <span className="ana-col-tip" aria-hidden="true">{tip(w)}</span>
              <div className="ana-col-plot">
                {labelled && <span className="ana-col-value">{w.count}</span>}
                <div className="ana-col-bar" style={{ height: `${(w.count / max) * 100}%` }} />
              </div>
              <div className="ana-col-label">{w.current ? t('anaThisWeek') : formatDate(w.week).slice(0, 5)}</div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
