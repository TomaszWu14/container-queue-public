import { FormEvent, useState } from 'react'
import { api } from '../api'
import { useT } from '../i18n'

/*
 * Bramka przed kontem demo: uprzejme przedstawienie się (imię, nazwisko, firma + informacja RODO).
 * Dane idą na serwer (POST /api/public/demo-visitor), który ustawia ciasteczko HttpOnly na 30 dni;
 * frontend niczego nie zapamiętuje. Pole `website` to honeypot — ukryte przed ludźmi.
 * Style klas .kl2-* pochodzą z LoginPage (komponent renderuje się wewnątrz jego karty).
 */
export default function DemoVisitorForm({ onDone, onBack }: { onDone: () => void; onBack: () => void }) {
  const t = useT()
  const [v, setV] = useState({ first_name: '', last_name: '', company: '', website: '' })
  const [consent, setConsent] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const set = (k: keyof typeof v) => (e: { target: { value: string } }) => setV(s => ({ ...s, [k]: e.target.value }))

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      await api.post('/api/public/demo-visitor', { ...v, consent })
      onDone()
    } catch {
      setError(t('visitorError'))
    } finally {
      setBusy(false)
    }
  }
  const ready = v.first_name.trim().length >= 2 && v.last_name.trim().length >= 2
    && v.company.trim().length >= 2 && consent

  return (
    <form onSubmit={submit} data-testid="visitor-form"
          style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      <h2>{t('visitorTitle')}</h2>
      {([['first_name', 'visitorFirstName', 'given-name'], ['last_name', 'visitorLastName', 'family-name'],
         ['company', 'visitorCompany', 'organization']] as const).map(([key, label, ac]) => (
        <div className="kl2-field" key={key}>
          <label htmlFor={`kl2-v-${key}`}>{t(label)}</label>
          <input id={`kl2-v-${key}`} required minLength={2} maxLength={100} autoComplete={ac}
                 value={v[key]} onChange={set(key)} />
        </div>
      ))}
      {/* honeypot: poza ekranem, bez fokusu i bez autouzupełniania */}
      <div aria-hidden="true" style={{ position: 'absolute', left: -9999, height: 0, overflow: 'hidden' }}>
        <input name="website" aria-label="website" tabIndex={-1} autoComplete="off" value={v.website} onChange={set('website')} />
      </div>
      <label className="kl2-note" style={{ display: 'flex', gap: 8, alignItems: 'flex-start' }}>
        <input type="checkbox" required checked={consent} onChange={e => setConsent(e.target.checked)} />
        <span>{t('visitorConsent')}</span>
      </label>
      {error && <p className="kl2-error" role="alert">{error}</p>}
      <button className="kl2-submit" type="submit" disabled={busy || !ready}>{t('visitorSubmit')}</button>
      <button type="button" className="kl2-forgot" onClick={onBack}>{t('visitorBack')}</button>
      <p className="kl2-fwd" style={{ fontSize: 12 }}>{t('visitorGdpr')}</p>
    </form>
  )
}
