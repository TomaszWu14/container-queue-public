// Wyciszenie alertów kontenera z dzwonka (trzecia lista PO, pkt 3): „nie przypominaj przez 1 / 3 / 7 dni”.
// Osobiste — inni dalej dostają alert; wzmianki (@) przychodzą zawsze.
import { useState } from 'react'
import { api } from './api'
import { formatDate } from './dates'
import { useT } from './i18n'

export interface AlertMute { container_id: number; container_no: string; until: string }

const DAYS = [1, 3, 7] as const

export default function NotificationMute({ containerId, mute, onChange }: {
  containerId: number; mute?: AlertMute; onChange: (containerId: number, mute: AlertMute | null) => void
}) {
  const t = useT()
  const [picking, setPicking] = useState(false)
  const [busy, setBusy] = useState(false)
  const stop = (e: { stopPropagation: () => void }) => e.stopPropagation()

  const set = async (days: number) => {
    setBusy(true)
    try {
      onChange(containerId, await api.post<AlertMute>('/api/notifications/mutes', { container_id: containerId, days }))
      setPicking(false)
    } catch { /* bez zmiany stanu — przycisk zostaje */ } finally { setBusy(false) }
  }
  const undo = async () => {
    setBusy(true)
    try {
      await api.del(`/api/notifications/mutes/${containerId}`)
      onChange(containerId, null)
    } catch { /* jw. */ } finally { setBusy(false) }
  }

  return (
    <div className="notif-mute" onClick={stop} onKeyDown={stop}>
      {mute ? (
        <>
          <span>{t('muteUntil').replace('{d}', formatDate(mute.until))}</span>
          <button type="button" className="btn small ghost" disabled={busy} onClick={undo}>{t('muteUndo')}</button>
        </>
      ) : picking ? (
        <>
          <span>{t('muteFor')}</span>
          {DAYS.map(d => (
            <button key={d} type="button" className="btn small secondary" disabled={busy} onClick={() => set(d)}>
              {t(`muteDays${d}`)}</button>
          ))}
        </>
      ) : (
        <button type="button" className="btn small ghost" onClick={() => setPicking(true)}
                title={t('muteHint')}>{t('muteAction')}</button>
      )}
    </div>
  )
}
