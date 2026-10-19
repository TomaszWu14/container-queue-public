// Przegląd dostępów (US-076, czwarta lista PO, pkt 9): konta nieużywane od 90 dni (albo nigdy), admini bez 2FA
// i konta z dostępem do wszystkich spółek. Blokada to decyzja admina — przycisk woła ten sam PATCH co lista
// użytkowników (z audytem); automat niczego sam nie wyłącza. Raz na kwartał przypomnienie w dzwonku.
import { useEffect, useState } from 'react'
import { api, errorMessage } from '../../api'
import { useConfirm } from '../../ConfirmDialog'
import { formatDateTime } from '../../dates'
import { useT } from '../../i18n'

interface Row { id: number; login: string; full_name: string; role: string; last_seen: string | null; reason: string }
export interface AccessReview {
  stale_days: number; active: number; stale: Row[]; admins_without_2fa: Row[]; all_companies: Row[]
}

export default function AccessReviewPanel({ onChanged }: { onChanged?: () => void }) {
  const t = useT()
  const { confirm } = useConfirm()
  const [data, setData] = useState<AccessReview | null>(null)
  const [error, setError] = useState('')
  const load = () => api.get<AccessReview>('/api/users/access-review')
    .then(r => { if (Array.isArray(r?.stale)) setData(r) }).catch(() => {})
  useEffect(() => { load() }, [])

  const block = async (r: Row) => {
    if (!(await confirm(t('accReviewConfirm').replace('{login}', r.login), { danger: true }))) return
    setError('')
    try {
      await api.patch(`/api/users/${r.id}`, { is_active: false })
      load()
      onChanged?.()
    } catch (err) { setError(errorMessage(err)) }
  }
  if (!data) return null
  const rows = [...data.stale, ...data.admins_without_2fa, ...data.all_companies]
  return (
    <section className="panel" aria-label={t('accReviewTitle')} style={{ marginBottom: 14 }}>
      <h3 style={{ marginTop: 0 }}>{t('accReviewTitle')}</h3>
      <p className="muted" style={{ maxWidth: 820 }}>
        {t('accReviewIntro').replace('{days}', String(data.stale_days)).replace('{active}', String(data.active))}
      </p>
      {error && <p className="error">{error}</p>}
      {rows.length === 0 ? <p className="muted">{t('accReviewAllGood')}</p> : (
        <div className="table-wrap">
          <table className="grid">
            <thead><tr>
              <th>{t('loginField')}</th><th>{t('accReviewColWhy')}</th><th>{t('accReviewColLastSeen')}</th><th />
            </tr></thead>
            <tbody>
              {rows.map(r => (
                <tr key={`${r.reason}-${r.id}`}>
                  <td data-label={t('loginField')}><b>{r.login}</b> {r.full_name && <span className="muted">{r.full_name}</span>}</td>
                  <td data-label={t('accReviewColWhy')}>{t(`accReviewWhy_${r.reason}`)}</td>
                  <td data-label={t('accReviewColLastSeen')}>{r.last_seen ? formatDateTime(r.last_seen) : t('accReviewNever')}</td>
                  <td>{(r.reason === 'stale' || r.reason === 'never') &&
                    <button type="button" className="secondary" onClick={() => void block(r)}>{t('accReviewBlock')}</button>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
