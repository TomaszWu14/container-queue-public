import { useEffect, useState } from 'react'
import { BellRing } from 'lucide-react'
import { api, errorMessage } from '../../api'
import { useToast } from '../../feedback'
import { useT } from '../../i18n'
import * as push from './pushClient'

/** Profil: powiadomienia push na tym urządzeniu (US-086) — tylko najpilniejsze alerty. */
export default function PushSection() {
  const t = useT()
  const { showToast } = useToast()
  const [status, setStatus] = useState<push.PushStatus | null>(null)
  const [mine, setMine] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const load = async () => {
    const s = await api.get<push.PushStatus>('/api/notifications/push')
    setStatus(s)
    const endpoint = await push.currentEndpoint()
    setMine(endpoint && s.endpoints.includes(endpoint) ? endpoint : null)
  }
  useEffect(() => { load().catch(() => setStatus(null)) }, [])

  const run = async (fn: () => Promise<void>) => {
    setBusy(true)
    try { await fn(); await load() } catch (e) { showToast(errorMessage(e), 'error') } finally { setBusy(false) }
  }
  const turnOn = () => run(async () => {
    if (!status?.public_key) return
    if (!await push.enable(status.public_key)) showToast(t('pushDenied'), 'error')
  })
  const turnOff = () => run(() => push.disable())
  const test = () => run(async () => {
    const r = await api.post<{ devices: number; sent: number }>('/api/notifications/push/test', {})
    showToast(t('pushTestSent').replace('{sent}', String(r.sent)).replace('{devices}', String(r.devices)), r.sent ? 'success' : 'error')
  })

  if (!status) return null
  return (
    <div className="panel">
      <h2 className="as-h3"><BellRing size={18} aria-hidden="true" /> {t('pushTitle')}</h2>
      <p className="muted">{t('pushIntro')}</p>
      {!status.available ? <p className="muted">{t('pushServerOff')}</p>
        : !push.supported() ? <p className="muted">{t('pushUnsupported')}</p>
        : <div className="row" style={{ gap: 8, flexWrap: 'wrap' }}>
            {mine
              ? <>
                  <span className="badge">{t('pushOnHere')}</span>
                  <button className="btn small secondary" disabled={busy} onClick={test}>{t('pushTest')}</button>
                  <button className="btn small secondary" disabled={busy} onClick={turnOff}>{t('pushTurnOff')}</button>
                </>
              : <button className="btn small" disabled={busy} onClick={turnOn}>{t('pushTurnOn')}</button>}
          </div>}
      {status.endpoints.length > 0 && <p className="muted">{t('pushDevices').replace('{n}', String(status.endpoints.length))}</p>}
    </div>
  )
}
