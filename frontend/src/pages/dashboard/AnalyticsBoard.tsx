import { useEffect, useState } from 'react'
import { api } from '../../api'
import { todayISO } from '../../dates'
import { useT } from '../../i18n'
import Donut from './charts/Donut'
import WeekColumns, { type Week } from './charts/WeekColumns'
import ProcessFlow, { type Stage } from './ProcessFlow'

// Pulpit analityczny (widok w stylu Power BI): przepływ przez proces, trzy koła podziału i rozładunki
// w tygodniach. Dane: GET /api/stats/overview (backend/app/routers/stats_overview.py), zakres jak pulpit.
type Overview = {
  stages: Stage[]
  transport: { key: 'morski' | 'kolej' | 'lotniczy' | 'inne'; count: number }[]
  ports: { name: string | null; count: number }[]
  customs: { not_started: number; in_progress: number; cleared: number } | null
  weeks: Week[]
}

export default function AnalyticsBoard() {
  const t = useT()
  const [data, setData] = useState<Overview | null>(null)
  useEffect(() => {
    api.get<Overview>(`/api/stats/overview?today=${todayISO()}`)
      .then(d => setData(d && Array.isArray(d.stages) ? d : null)).catch(() => setData(null))
  }, [])
  if (!data) return null

  const modeLabel = { morski: t('anaSea'), kolej: t('anaRail'), lotniczy: t('anaAir'), inne: t('anaOther') }
  const modeTone = { morski: '1', kolej: '2', lotniczy: '3', inne: 'rest' }
  return (
    <div className="ana-board">
      <ProcessFlow stages={data.stages} />
      <div className="ana-grid">
        <Donut title={t('anaTransportTitle')} slices={data.transport.map(m => (
          { key: m.key, label: modeLabel[m.key] ?? m.key, value: m.count, tone: modeTone[m.key] ?? 'rest' }))} />
        <Donut title={t('anaPortsTitle')} slices={data.ports.map((p, i) => (
          { key: p.name ?? '_other', label: p.name ?? t('anaPortOther'), value: p.count,
            tone: p.name ? String(i + 1) : 'rest' }))} />
        {data.customs && (
          <Donut title={t('anaCustomsTitle')} slices={[
            { key: 'none', label: t('anaCustomsNone'), value: data.customs.not_started, tone: 'rest' },
            { key: 'progress', label: t('anaCustomsProgress'), value: data.customs.in_progress, tone: 'warn' },
            { key: 'cleared', label: t('anaCustomsCleared'), value: data.customs.cleared, tone: 'good' },
          ]} />
        )}
      </div>
      <WeekColumns weeks={data.weeks} />
    </div>
  )
}
