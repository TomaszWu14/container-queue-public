// Pomyłki modelu do przeglądu (druga lista PO, pkt 8): pozycje faktur, w których człowiek wybrał inny
// materiał niż podpowiedź modelu. Najpierw te z pewnością ≥ progu — tam automat ustawiłby błąd sam.
// Każda poprawka i tak uczy model; lista służy do przeglądu reguł i kartoteki.
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { useT } from '../i18n'

export interface AiMistake {
  container_id: number; container_no: string; invoice_number: string; at: string; line_no: number
  raw_ref: string; descr: string; suggestion: string; chosen: string; confidence: number; auto: boolean
}

export default function AiMistakesTable() {
  const t = useT()
  const [rows, setRows] = useState<AiMistake[] | null>(null)
  useEffect(() => {
    api.get<AiMistake[]>('/api/automations/ai-quality/mistakes')
      .then(r => setRows(Array.isArray(r) ? r : [])).catch(() => setRows([]))
  }, [])
  if (rows === null) return null
  return (
    <>
      <h3 className="aiq-sub">{t('aiqMistakesTitle')}</h3>
      {rows.length === 0 ? <p className="muted">{t('aiqMistakesNone')}</p> : (
        <div style={{ overflowX: 'auto' }}>
          <table className="grid auto-table aiq-mistakes">
            <thead><tr>
              <th>{t('aiqMisContainer')}</th><th>{t('aiqMisLine')}</th><th>{t('aiqMisSuggested')}</th>
              <th>{t('aiqMisChosen')}</th><th>{t('aiqMisConfidence')}</th>
            </tr></thead>
            <tbody>
              {rows.map(m => (
                <tr key={`${m.container_id}-${m.invoice_number}-${m.line_no}`}>
                  <td className="mono"><Link to={`/kontenery/${m.container_id}`}>{m.container_no}</Link>
                    <div className="muted" style={{ fontSize: 12 }}>{m.invoice_number} · {m.line_no}</div></td>
                  <td data-label={t('aiqMisLine')}>{m.raw_ref}{m.descr ? ` — ${m.descr}` : ''}</td>
                  <td data-label={t('aiqMisSuggested')} className="mono">{m.suggestion}</td>
                  <td data-label={t('aiqMisChosen')} className="mono"><b>{m.chosen}</b></td>
                  <td data-label={t('aiqMisConfidence')}>{Math.round(m.confidence * 100)}%
                    {m.auto && <span className="badge cs-REWIZJA" style={{ marginLeft: 6 }}
                                     title={t('aiqMisAutoHint')}>{t('aiqMisAuto')}</span>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  )
}
