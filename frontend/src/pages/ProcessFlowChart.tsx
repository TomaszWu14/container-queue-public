// Wykres przepływu procesu (druga lista PO, pkt 4): etapy w kolejności procesu, przejścia jako pasma
// o grubości proporcjonalnej do liczby kontenerów. Przejścia w przód nad osią (--viz-1), cofnięcia
// statusu pod osią (--viz-2) — poprawki w procesie widać od razu. Liczby: etykiety i podpowiedź <title>;
// tabelaryczny odpowiednik to lista „Najczęstsze przejścia” obok.
import { useT } from '../i18n'

export interface Transition { from: string; to: string; count: number }

const BOX_W = 124
const GAP = 34
const BOX_H = 40
const ARC_SPACE = 70    // miejsce na łuki (pominięcie etapu nad osią, cofnięcie pod osią)
const MAX_W = 16        // najgrubsze pasmo (px)

export default function ProcessFlowChart({ transitions, order }: { transitions: Transition[]; order: string[] }) {
  const t = useT()
  const used = new Set(transitions.flatMap(x => [x.from, x.to]))
  const stages = order.filter(s => used.has(s))
  if (stages.length < 2) return null
  const idx = new Map(stages.map((s, i) => [s, i]))
  const max = Math.max(...transitions.map(x => x.count))
  const width = (n: number) => 2 + (MAX_W - 2) * (n / max)
  const x0 = (i: number) => i * (BOX_W + GAP)
  const cx = (i: number) => x0(i) + BOX_W / 2
  const W = x0(stages.length - 1) + BOX_W
  const backward = transitions.filter(x => (idx.get(x.to) ?? 0) < (idx.get(x.from) ?? 0))
  const skips = transitions.some(x => (idx.get(x.to) ?? 0) > (idx.get(x.from) ?? 0) + 1)
  const TOP = skips ? ARC_SPACE : 22
  const H = TOP + BOX_H + (backward.length ? ARC_SPACE : 8)
  const yMid = TOP + BOX_H / 2
  const label = (x: Transition) => `${t(`st_${x.from}`)} → ${t(`st_${x.to}`)}: ${x.count}`

  return (
    <div className="proc-flow" style={{ overflowX: 'auto' }}>
      <svg viewBox={`0 0 ${W} ${H}`} role="img" style={{ width: '100%', minWidth: Math.min(W, 760), height: 'auto' }}
           aria-label={`${t('procFlowTitle')}: ${transitions.map(label).join('; ')}`}>
        {transitions.map(x => {
          const a = idx.get(x.from), b = idx.get(x.to)
          if (a === undefined || b === undefined || a === b) return null
          const back = b < a
          const w = width(x.count)
          if (!back && b === a + 1) {        // sąsiednie etapy: prosty pas między pudełkami
            return (
              <g key={`${x.from}-${x.to}`} className="proc-flow-fwd">
                <line x1={x0(a) + BOX_W} x2={x0(b)} y1={yMid} y2={yMid} strokeWidth={w} />
                <text x={(x0(a) + BOX_W + x0(b)) / 2} y={yMid - w / 2 - 4} textAnchor="middle">{x.count}</text>
                <title>{label(x)}</title>
              </g>
            )
          }
          const lift = 18 + Math.abs(b - a) * 10
          const y = back ? TOP + BOX_H : TOP
          const ctrl = back ? y + lift : y - lift
          return (
            <g key={`${x.from}-${x.to}`} className={back ? 'proc-flow-back' : 'proc-flow-fwd'}>
              <path d={`M ${cx(a)} ${y} C ${cx(a)} ${ctrl}, ${cx(b)} ${ctrl}, ${cx(b)} ${y}`}
                    strokeWidth={w} fill="none" />
              <text x={(cx(a) + cx(b)) / 2} y={back ? ctrl - 2 : ctrl + 10} textAnchor="middle">{x.count}</text>
              <title>{label(x)}</title>
            </g>
          )
        })}
        {stages.map((s, i) => {
          const [num, ...rest] = t(`st_${s}`).split(' · ')
          return (
            <g key={s} className="proc-flow-node">
              <rect x={x0(i)} y={TOP} width={BOX_W} height={BOX_H} rx={6} />
              <text x={cx(i)} y={TOP + 16} textAnchor="middle" className="proc-flow-num">{num}</text>
              <text x={cx(i)} y={TOP + 31} textAnchor="middle">{rest.join(' · ') || num}</text>
            </g>
          )
        })}
      </svg>
      <ul className="aiq-legend" aria-hidden="true">
        <li><span className="aiq-swatch proc-flow-sw-fwd" />{t('procFlowForward')}</li>
        {backward.length > 0 && <li><span className="aiq-swatch proc-flow-sw-back" />{t('procFlowBack')}</li>}
      </ul>
    </div>
  )
}
