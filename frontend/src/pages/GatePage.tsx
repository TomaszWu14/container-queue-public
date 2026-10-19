import { CircleCheckIcon, ClockIcon } from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { api, errorMessage } from '../api'
import { LoadError, Skeleton, useToast } from '../feedback'
import { useLocale, useT } from '../i18n'
import { useUser } from '../App'
import { Field } from '../Field'
import { useConfirm } from '../ConfirmDialog'
import { PageHeader } from '../PageHeader'
import { useVisibleInterval } from '../useVisibleInterval'
import GateScanner from './gate/GateScanner'
import * as offline from './gate/gateOffline'

// #60: kolejka bramy — dzisiejsze spodziewane auta, duża czcionka (ochrona przy bramie),
// auto-refresh co 60 s, przycisk „Przyjechał" (check-in, idempotentny per dzień).
export interface GateItem {
  id: number
  container_no: string
  truck_no: string
  trailer_no: string
  driver_name: string
  warehouse_id: number | null
  warehouse: string
  notify_date: string | null
  eta: string | null
  status: string
  driver_arrived_at: string | null
  checked_in_at: string | null
  ramp_stage?: string | null
}

// D9: etap rampy — drugi wymiar obok statusu; „Przyjechałem" kierowcy ustawia PODSTAWIONY
const RAMP_STAGES = ['PODSTAWIONY', 'ROZLADOWANY', 'PRZYJETY']

const fmtTime = (iso: string | null, locale: string) =>
  iso ? new Date(`${iso}Z`).toLocaleTimeString(locale, { hour: '2-digit', minute: '2-digit' }) : ''

export default function GatePage() {
  const t = useT()
  const locale = useLocale()
  const user = useUser()
  const { showToast } = useToast()
  const { prompt } = useConfirm()
  const [params] = useSearchParams()
  const magazyn = params.get('magazyn') || ''
  const [items, setItems] = useState<GateItem[] | null>(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(0)
  const [offlineSince, setOfflineSince] = useState<number | null>(null)   // US-085: lista z pamięci
  const [queued, setQueued] = useState<number[]>([])                       // check-iny czekające na sieć
  const uid = user?.id ?? 0

  const canCheckin = user?.role === 'admin' || user?.role === 'logistics' || user?.role === 'warehouse'

  const load = useCallback(() => {
    // ?magazyn=<id> — tylko liczbowe id trafia do API (inaczej pełny zakres użytkownika)
    const q = /^\d+$/.test(magazyn) ? `?warehouse_id=${magazyn}` : ''
    api.get<{ items: GateItem[] }>(`/api/gate${q}`)
      .then(r => {
        setItems(r.items); setError(''); setOfflineSince(null)
        offline.saveList(uid, magazyn, r.items)
      })
      .catch(err => {
        const cached = offline.isNetworkError(err) ? offline.loadList(uid, magazyn) : null
        if (!cached) { setError(errorMessage(err)); return }
        const waiting = new Map(offline.pending(uid).map(p => [p.id, p.at]))
        setItems(cached.items.map(i => (waiting.has(i.id) && !i.checked_in_at ? { ...i, checked_in_at: waiting.get(i.id)! } : i)))
        setOfflineSince(cached.savedAt); setError('')
      })
  }, [magazyn, uid])

  // po powrocie sieci: najpierw zaległe „Przyjechał”, potem świeża lista
  const flushQueue = useCallback(async () => {
    const { sent, failed } = await offline.flush(uid, id => api.post(`/api/gate/${id}/checkin`, {}))
    setQueued(offline.pending(uid).map(p => p.id))
    if (sent.length) showToast(t('gateOfflineSent').replace('{n}', String(sent.length)))
    if (failed.length) setError(t('gateOfflineFailed').replace('{n}', String(failed.length)))
    if (sent.length || failed.length) load()
  }, [uid, load, showToast, t])

  useEffect(() => {
    setQueued(offline.pending(uid).map(p => p.id))
    void flushQueue()
    const onOnline = () => { void flushQueue() }
    window.addEventListener('online', onOnline)
    return () => window.removeEventListener('online', onOnline)
  }, [flushQueue, uid])

  const queueCheckin = (id: number) => {
    const at = new Date().toISOString().slice(0, 19)
    offline.queueCheckin(uid, id, at)
    setQueued(offline.pending(uid).map(p => p.id))
    setItems(list => list && list.map(i => (i.id === id ? { ...i, checked_in_at: at } : i)))
    showToast(t('gateOfflineQueued'))
  }

  useEffect(() => { load() }, [load])
  useVisibleInterval(load, 60_000)   // auto-refresh 60 s (tylko widoczna karta)

  const checkin = async (id: number) => {
    if (typeof navigator !== 'undefined' && navigator.onLine === false) { queueCheckin(id); return }
    setBusy(id)
    try {
      await api.post(`/api/gate/${id}/checkin`, {})
      showToast(t('toastSaved'))
      load()
    } catch (err) {
      if (offline.isNetworkError(err)) queueCheckin(id)
      else setError(errorMessage(err))
    } finally { setBusy(0) }
  }

  // kierowca zadzwonił, że się spóźni — ta sama ścieżka co dawna strona kierowcy (dzwonek, okno 30 min)
  const delay = async (id: number) => {
    const etaTime = await prompt(t('gateDelayPrompt'))
    if (!etaTime) return
    setBusy(id)
    try {
      await api.post(`/api/gate/${id}/delay`, { eta_time: etaTime })
      showToast(t('toastSaved'))
      load()
    } catch (err) { setError(errorMessage(err)) } finally { setBusy(0) }
  }

  const setRamp = async (id: number, stage: string) => {
    setBusy(id)
    try {
      await api.post(`/api/containers/${id}/ramp-stage`, { stage: stage || null })
      load()
    } catch (err) { setError(errorMessage(err)) } finally { setBusy(0) }
  }

  return (
    <main className="page gate-page">
      <PageHeader title={t('gateTitle')} subtitle={t('gateRefreshInfo')} />
      {error && !items && <LoadError message={error} onRetry={load} />}
      {error && items && <p className="error">{error}</p>}
      {!items && !error && <Skeleton rows={4} />}
      {offlineSince !== null && (
        <p className="gate-offline" role="status">
          {t('gateOfflineBanner').replace('{time}', new Date(offlineSince).toLocaleTimeString(locale, { hour: '2-digit', minute: '2-digit' }))}
        </p>
      )}
      {queued.length > 0 && <p className="muted" role="status">{t('gateOfflineWaiting').replace('{n}', String(queued.length))}</p>}
      {items && canCheckin && (
        <GateScanner items={items} busy={busy} onCheckin={checkin} fmtTime={iso => fmtTime(iso, locale)} />)}
      {items && items.length === 0 && <p className="muted gate-big">{t('gateNoTrucks')}</p>}
      {items && items.map(item => (
        <div key={item.id} id={`gate-row-${item.id}`} className={`panel gate-row${item.checked_in_at ? ' gate-done' : ''}`}>
          <div className="gate-main">
            <b className="mono gate-no">{item.container_no}</b>
            {/* C29: bez numeru auta nie pokazujemy samotnego „—” */}
            {(item.truck_no || item.trailer_no) && (
              <span className="gate-truck mono">
                {item.truck_no}{item.trailer_no ? ` / ${item.trailer_no}` : ''}
              </span>
            )}
            {item.driver_name && <span className="gate-driver">{item.driver_name}</span>}
            <span className="muted">{item.warehouse}</span>
          </div>
          <div className="gate-side">
            {canCheckin
              ? <Field label={t('gateRamp')}>
                  <select value={item.ramp_stage || ''} disabled={busy === item.id || offlineSince !== null}
                          onChange={e => setRamp(item.id, e.target.value)}>
                    <option value="">{t('gateRamp_none')}</option>
                    {RAMP_STAGES.map(s => <option key={s} value={s}>{t(`gateRamp_${s}`)}</option>)}
                  </select>
                </Field>
              : item.ramp_stage && <span className="muted">{t('gateRamp')}: {t(`gateRamp_${item.ramp_stage}`)}</span>}
            {item.driver_arrived_at && (
              <span className="badge st-W_DOSTAWIE">
                {t('gateDriverArrived')} {fmtTime(item.driver_arrived_at, locale)}
              </span>
            )}
            {canCheckin && !item.checked_in_at && (
              <button className="btn secondary gate-btn" disabled={busy === item.id || offlineSince !== null}
                      onClick={() => delay(item.id)}>
                <ClockIcon size={14} /> {t('gateDelayBtn')}
              </button>
            )}
            {item.checked_in_at
              ? <span className="badge st-DOSTARCZONY">✓ {t('gateCheckedIn')} {fmtTime(item.checked_in_at, locale)}
                  {queued.includes(item.id) && <> · {t('gateOfflinePendingBadge')}</>}</span>
              : canCheckin && (
                <button className="btn gate-btn" disabled={busy === item.id}
                        onClick={() => checkin(item.id)}>
                  <CircleCheckIcon size={14} /> {t('gateArrivedBtn')}
                </button>
              )}
          </div>
        </div>
      ))}
    </main>
  )
}
