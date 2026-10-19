// Ponawianie wysyłek (US-022, trzecia lista PO, pkt 1): e-mail, Teams i n8n, które się nie udały, wracają
// do kolejki (po 1, 5 i 30 min); tu admin widzi, co czeka na ponowienie i co ostatecznie nie doszło.
import { useEffect, useState } from 'react'
import { api } from '../api'
import { formatDateTime } from '../dates'
import { useT } from '../i18n'

interface Pending { channel: string; label: string; attempts: number; error: string; next_at: string }
interface Failed { channel: string; label: string; attempts: number; error: string; at: string }
export interface Deliveries { pending: Pending[]; failed: Failed[]; delays_s: number[] }

export default function DeliveryRetryPanel() {
  const t = useT()
  const [data, setData] = useState<Deliveries | null>(null)

  useEffect(() => {
    api.get<Deliveries>('/api/automations/deliveries')
      .then(r => { if (Array.isArray(r?.pending)) setData(r) }).catch(() => {})
  }, [])
  if (!data) return null

  const rows = [
    ...data.pending.map(p => ({ ...p, state: t('delivPending'), when: formatDateTime(p.next_at), bad: false })),
    ...data.failed.map(f => ({ ...f, state: t('delivFailed'), when: formatDateTime(f.at), bad: true })),
  ]
  return (
    <section className="panel" aria-label={t('delivTitle')} style={{ marginTop: 18 }}>
      <h2 className="as-h3" style={{ margin: 0 }}>{t('delivTitle')}</h2>
      <p className="muted" style={{ maxWidth: 820 }}>{t('delivIntro')}</p>
      {rows.length === 0 ? <p className="muted">{t('delivAllGood')}</p> : (
        <div className="table-wrap">
          <table className="grid auto-table">
            <thead><tr>
              <th>{t('delivColChannel')}</th><th>{t('delivColWhat')}</th><th>{t('delivColState')}</th>
              <th>{t('delivColAttempts')}</th><th>{t('delivColError')}</th><th>{t('delivColWhen')}</th>
            </tr></thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={`${r.channel}-${i}`}>
                  <td data-label={t('delivColChannel')}>{t(`delivCh_${r.channel}`)}</td>
                  <td data-label={t('delivColWhat')}>{r.label}</td>
                  <td data-label={t('delivColState')}>{r.bad ? <b className="whatif-over">{r.state}</b> : r.state}</td>
                  <td data-label={t('delivColAttempts')}>{r.attempts}</td>
                  <td data-label={t('delivColError')}><code>{r.error}</code></td>
                  <td data-label={t('delivColWhen')}>{r.when}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
