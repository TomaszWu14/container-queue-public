import { useState } from 'react'
import { useT } from '../../../i18n'

// Wykres kołowy (pierścień) pulpitu: wycinki z 2px przerwą w kolorze tła, suma w środku, legenda z liczbą
// i udziałem (legenda = podpisy bezpośrednie i widok tabelaryczny — kolor nigdy nie jest jedyną informacją).
// Najechanie / fokus na wycinku albo wierszu legendy podświetla go i pokazuje wartość w środku.
export type Slice = { key: string; label: string; value: number; tone: string }

const R = 54
const WIDTH = 18
const C = 2 * Math.PI * R
const GAP = 2

export default function Donut({ title, slices }: { title: string; slices: Slice[] }) {
  const t = useT()
  const [active, setActive] = useState<string | null>(null)
  const total = slices.reduce((s, x) => s + x.value, 0)
  const shown = slices.filter(s => s.value > 0)
  const pct = (v: number) => (total ? Math.round((v / total) * 100) : 0)
  const focus = shown.find(s => s.key === active)

  let offset = 0
  const arcs = shown.map(s => {
    const len = (s.value / total) * C
    const dash = shown.length > 1 ? Math.max(len - GAP, 0.5) : len
    const arc = { ...s, dash, offset }
    offset += len
    return arc
  })

  return (
    <section className="panel ana-card" aria-label={title}>
      <div className="ana-card-title">{title}</div>
      {total === 0 ? <p className="muted ana-empty">{t('anaEmpty')}</p> : (
        <div className="ana-donut">
          <svg viewBox="0 0 140 140" role="img" className="ana-donut-svg"
               aria-label={`${title}: ${shown.map(s => `${s.label} ${s.value}`).join(', ')}`}>
            <circle cx="70" cy="70" r={R} className="ana-donut-track" strokeWidth={WIDTH} fill="none" />
            <g transform="rotate(-90 70 70)">
              {arcs.map(a => (
                <circle key={a.key} cx="70" cy="70" r={R} fill="none" strokeWidth={WIDTH}
                        className={`ana-arc tone-${a.tone}${active && active !== a.key ? ' dim' : ''}`}
                        strokeDasharray={`${a.dash} ${C - a.dash}`} strokeDashoffset={-a.offset}
                        onMouseEnter={() => setActive(a.key)} onMouseLeave={() => setActive(null)}>
                  <title>{`${a.label}: ${a.value} (${pct(a.value)}%)`}</title>
                </circle>
              ))}
            </g>
            <text x="70" y="68" textAnchor="middle" className="ana-donut-value">
              {focus ? focus.value : total}
            </text>
            <text x="70" y="86" textAnchor="middle" className="ana-donut-caption">
              {focus ? `${pct(focus.value)}%` : t('anaTotal')}
            </text>
          </svg>
          <ul className="ana-legend">
            {slices.map(s => (
              <li key={s.key} tabIndex={0} className={active === s.key ? 'on' : ''}
                  onMouseEnter={() => setActive(s.key)} onMouseLeave={() => setActive(null)}
                  onFocus={() => setActive(s.key)} onBlur={() => setActive(null)}>
                <span className={`ana-swatch tone-${s.tone}`} aria-hidden="true" />
                <span className="ana-legend-label">{s.label}</span>
                <span className="ana-legend-value">{s.value}</span>
                <span className="ana-legend-pct">{pct(s.value)}%</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  )
}
