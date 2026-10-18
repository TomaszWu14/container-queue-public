// „Symuluj dzień” (US-040): przycisk w demo przechodzi obieg automatów na danych demo — mail →
// numer kontenera z treści → faktura → reguły → zdarzenie do n8n z podpisem → zaoszczędzone minuty.
// Serwer woła prawdziwe funkcje i niczego nie zapisuje (GET), więc konto demo zostaje tylko do odczytu.
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api, errorMessage } from '../api'
import { useT } from '../i18n'

export interface DaySimulation {
  available: boolean
  container_id?: number
  container_no?: string
  mail?: { text: string; found: string[] }
  invoice?: { invoice_number: string; lines: number; rules: number; ml: number; user: number; open: number } | null
  rules?: { name: string; count: number }[]
  event?: { id: string; event: string; signature: string; bytes: number }
  minutes?: Record<'mail' | 'invoice' | 'rules', number>
  total_minutes?: number
}

export default function SimulateDayPanel() {
  const t = useT()
  const [sim, setSim] = useState<DaySimulation | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const fill = (key: string, vars: Record<string, string | number>) =>
    Object.entries(vars).reduce((s, [k, v]) => s.replace(`{${k}}`, String(v)), t(key))

  const run = async () => {
    setBusy(true); setError('')
    try {
      setSim(await api.get<DaySimulation>('/api/automations/simulate-day'))
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  const steps = sim?.available ? [
    { key: 'mail', title: t('simStepMail'), body: <>
        <blockquote className="sim-mail">{sim.mail?.text}</blockquote>
        {sim.mail?.found.length
          ? fill('simMailFound', { no: sim.mail.found.join(', ') })
          : t('simMailNotFound')}
      </> },
    { key: 'invoice', title: t('simStepInvoice'), body: sim.invoice
        ? fill('simInvoice', { nr: sim.invoice.invoice_number || '—', n: sim.invoice.lines, r: sim.invoice.rules,
                               m: sim.invoice.ml, u: sim.invoice.user, o: sim.invoice.open })
        : t('simInvoiceNone') },
    { key: 'rules', title: t('simStepRules'), body: sim.rules?.length
        ? <ul className="sim-rules">{sim.rules.map(r => <li key={r.name}>{fill('simRule', { name: r.name, n: r.count })}</li>)}</ul>
        : t('simRulesNone') },
    { key: 'event', title: t('simStepEvent'), body: <>
        {fill('simEvent', { kind: sim.event?.event ?? '', b: sim.event?.bytes ?? 0 })}{' '}
        <code>{sim.event?.signature}</code>
      </> },
    { key: 'saved', title: t('simStepSaved'), body: fill('simSaved', {
        total: sim.total_minutes ?? 0, mail: sim.minutes?.mail ?? 0, inv: sim.minutes?.invoice ?? 0,
        rules: sim.minutes?.rules ?? 0 }) },
  ] : []

  return (
    <section className="panel sim" aria-label={t('simTitle')} style={{ marginTop: 18 }}>
      <div className="row" style={{ justifyContent: 'space-between', gap: 8, flexWrap: 'wrap' }}>
        <h2 className="as-h3" style={{ margin: 0 }}>{t('simTitle')}</h2>
        <button className="btn small" onClick={run} disabled={busy}>{busy ? t('simRunning') : t('simRun')}</button>
      </div>
      <p className="muted" style={{ maxWidth: 820 }}>{t('simIntro')}</p>
      {error && <p className="error" role="alert">{error}</p>}
      {sim && !sim.available && <p className="muted">{t('simUnavailable')}</p>}
      {steps.length > 0 && (
        <>
          <p style={{ margin: '4px 0 8px' }}>
            {t('simContainer')}{' '}
            <Link className="mono" to={`/kontenery/${sim?.container_id}`}>{sim?.container_no}</Link>
          </p>
          <ol className="sim-steps" aria-live="polite">
            {steps.map((s, i) => (
              <li key={s.key} className="sim-step" style={{ animationDelay: `${i * 450}ms` }}>
                <b>{s.title}</b>
                <div>{s.body}</div>
              </li>
            ))}
          </ol>
          <p className="muted" style={{ fontSize: 12 }}>{t('simNoWrite')}</p>
        </>
      )}
    </section>
  )
}
