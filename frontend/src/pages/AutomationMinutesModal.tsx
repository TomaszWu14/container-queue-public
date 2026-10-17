// Założenia minut licznika oszczędności (US-034, Z-024): admin ustawia, ile minut pracy ręcznej
// zastępuje jeden efekt każdego automatu. Zapis: PUT /api/automations/minutes (wpis w dzienniku zmian).
import { useState } from 'react'
import { api, errorMessage } from '../api'
import { useT } from '../i18n'
import { Modal } from '../Modal'
import type { AutomationItem } from './AutomationsPage'

export default function AutomationMinutesModal({ items, onSaved, onClose }: {
  items: AutomationItem[]
  onSaved: () => void
  onClose: () => void
}) {
  const t = useT()
  const [values, setValues] = useState<Record<string, string>>(
    () => Object.fromEntries(items.map(i => [i.key, String(i.minutes_per_effect)])))
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const save = async () => {
    setBusy(true)
    setError('')
    try {
      const minutes = Object.fromEntries(Object.entries(values).map(([k, v]) => [k, Number(v)]))
      await api.put('/api/automations/minutes', { minutes })
      onSaved()
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <Modal title={t('autoMinutesTitle')} onClose={onClose} busy={busy} width={560}>
      <p className="muted" style={{ marginTop: 0 }}>{t('autoMinutesInfo')}</p>
      <div style={{ display: 'grid', gap: 6, maxHeight: '55vh', overflowY: 'auto' }}>
        {items.map(i => (
          <label key={i.key} className="row" style={{ justifyContent: 'space-between', gap: 12 }}>
            <span>{t(`autoName_${i.key}`)}</span>
            <input type="number" min={0} max={240} step={1} style={{ width: 80 }}
                   value={values[i.key]} onChange={e => setValues(v => ({ ...v, [i.key]: e.target.value }))} />
          </label>
        ))}
      </div>
      {error && <p className="error">{error}</p>}
      <div className="actions">
        <button className="btn secondary" disabled={busy} onClick={onClose}>{t('cancel')}</button>
        <button className="btn" disabled={busy} onClick={save}>{busy ? t('loading') : t('autoMinutesSave')}</button>
      </div>
    </Modal>
  )
}
