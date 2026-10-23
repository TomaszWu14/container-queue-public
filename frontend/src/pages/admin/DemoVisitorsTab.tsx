import { useEffect, useState } from 'react'
import { api, downloadFile, errorMessage } from '../../api'
import { formatDateTime } from '../../dates'
import { useT } from '../../i18n'
import { DictTable } from './shared'

interface Visitor {
  id: number; first_name: string; last_name: string; company: string; created_at: string
  page_views?: number; duration_min?: number | null; top_sections?: string[]
}

export default function DemoVisitorsTab() {
  const t = useT()
  const [rows, setRows] = useState<Visitor[]>([])
  const [error, setError] = useState('')
  useEffect(() => {
    api.get<Visitor[]>('/api/admin/demo-visitors').then(setRows).catch(e => setError(errorMessage(e)))
  }, [])
  return (
    <div className="panel">
      <h3>{t('visitorsTitle')}</h3>
      <p className="muted">{t('visitorsInfo')}</p>
      {error && <p className="error">{error}</p>}
      <button className="btn secondary" style={{ marginBottom: 12 }}
              onClick={() => void downloadFile('/api/admin/demo-visitors.csv', 'demo-odwiedzajacy.csv')
                .catch(e => setError(errorMessage(e)))}>
        {t('visitorsCsv')}
      </button>
      <DictTable cols={[{ label: t('visitorsWhen'), width: '160px' }, t('visitorFirstName'),
                        t('visitorLastName'), t('visitorCompany'), t('visitorsViews'), t('visitorsTime'),
                        t('visitorsTop')]}>
        {rows.map(v => (
          <tr key={v.id}>
            <td>{formatDateTime(v.created_at)}</td><td>{v.first_name}</td>
            <td>{v.last_name}</td><td>{v.company}</td>
            <td>{v.page_views ?? 0}</td>
            <td>{v.duration_min == null ? '—' : t('visitorsMinutes').replace('{n}', String(v.duration_min))}</td>
            <td>{(v.top_sections ?? []).join(', ') || '—'}</td>
          </tr>
        ))}
        {rows.length === 0 && <tr><td colSpan={7}>{t('visitorsEmpty')}</td></tr>}
      </DictTable>
    </div>
  )
}
