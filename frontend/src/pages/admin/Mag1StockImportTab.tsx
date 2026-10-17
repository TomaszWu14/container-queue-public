import { CircleCheckIcon } from 'lucide-react'
import { useState } from 'react'
import { api, errorMessage } from '../../api'
import { TemplateButtons } from '../../importTemplate'
import { useT } from '../../i18n'
import { FilePicker } from '../../FilePicker'

interface Mag1Counts { rows: number; with_hu: number; produkty: number }
interface Mag1ImportResult { dry_run: boolean; counts: Mag1Counts }

// Import stanów MAG-1 z xlsx — snapshot (każdy import zastępuje poprzedni).
// Fallback dla analityki wywołań, gdy Power BI nie podaje stanów MAG-1.
export default function Mag1StockImportTab() {
  const t = useT()
  const [file, setFile] = useState<File | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<Mag1ImportResult | null>(null)

  const run = async () => {
    if (!file) return
    setBusy(true)
    setError('')
    setResult(null)
    try {
      const body = await api.upload<Mag1ImportResult>(
        '/api/import/mag1-stock?dry_run=false', file)
      setResult(body)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="panel">
      <h3>{t('mag1ImportTitle')}</h3>
      <p style={{ color: 'var(--muted)', fontSize: 14, margin: '0 0 12px' }}>
        {t('mag1ImportHint')}
      </p>
      <div className="row">
        <TemplateButtons kinds={['mag1']} />
        <FilePicker label={t('fieldFile')} accept=".xlsx,.xlsm" disabled={busy} file={file}
                    onChange={f => { setFile(f); setResult(null) }} />
        <button className="btn" disabled={!file || busy} onClick={run}>
          {busy ? t('loading') : t('mag1ImportBtn')}
        </button>
      </div>
      {error && <p className="error">{error}</p>}
      {result && (
        <p className="import-done">
          <CircleCheckIcon size={14} /> {t('mag1Rows')}: <b>{result.counts.rows}</b>
          {' · '}{t('mag1Produkty')}: <b>{result.counts.produkty}</b>
          {' · '}HU: <b>{result.counts.with_hu}</b>
        </p>
      )}
    </div>
  )
}
