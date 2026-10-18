// „Co jeśli statek się spóźni” (US-062): wybierz statek i liczbę dni — serwer przesuwa awizacje jego
// kontenerów tylko w pamięci i pokazuje, w które dni magazyn przekroczy limit. Nic nie zapisuje (GET).
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, errorMessage } from '../api'
import { formatDate } from '../dates'
import { useT } from '../i18n'

export interface WhatIfResult {
  vessel: string
  delay: number
  containers: { id: number; container_no: string; warehouse: string; from: string; to: string }[]
  days: { warehouse: string; day: string; before: number; after: number; limit: number
          over_before: boolean; over_after: boolean }[]
  new_overloads: number
  resolved_overloads: number
}

const URL = '/api/automations/what-if'

export default function WhatIfPanel() {
  const t = useT()
  const [vessels, setVessels] = useState<string[] | null>(null)
  const [vessel, setVessel] = useState('')
  const [delay, setDelay] = useState(5)
  const [result, setResult] = useState<WhatIfResult | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const fill = (key: string, vars: Record<string, string | number>) =>
    Object.entries(vars).reduce((s, [k, v]) => s.replace(`{${k}}`, String(v)), t(key))

  useEffect(() => {
    api.get<{ vessels: string[] }>(URL)
      .then(r => { setVessels(r.vessels); setVessel(r.vessels[0] ?? '') })
      .catch(err => setError(errorMessage(err)))
  }, [])

  const run = async () => {
    setBusy(true); setError('')
    try {
      const q = new URLSearchParams({ vessel, delay: String(delay) })
      setResult(await api.get<WhatIfResult>(`${URL}?${q}`))
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  const mark = (over: boolean) => over ? <b className="whatif-over">{t('whatIfOver')}</b> : null

  return (
    <section className="panel whatif" aria-label={t('whatIfTitle')} style={{ marginTop: 18 }}>
      <h2 className="as-h3" style={{ margin: 0 }}>{t('whatIfTitle')}</h2>
      <p className="muted" style={{ maxWidth: 820 }}>{t('whatIfIntro')}</p>
      {error && <p className="error" role="alert">{error}</p>}
      {vessels && vessels.length === 0 && <p className="muted">{t('whatIfNoVessels')}</p>}
      {vessels && vessels.length > 0 && (
        <div className="row" style={{ gap: 8, flexWrap: 'wrap', alignItems: 'flex-end' }}>
          <label>{t('whatIfVessel')}{' '}
            <select value={vessel} onChange={e => setVessel(e.target.value)}>
              {vessels.map(v => <option key={v} value={v}>{v}</option>)}
            </select>
          </label>
          <label>{t('whatIfDelay')}{' '}
            <input type="number" min={1} max={21} value={delay} style={{ width: 64 }}
                   onChange={e => setDelay(Math.min(21, Math.max(1, Number(e.target.value) || 1)))} />
          </label>
          <button className="btn small" onClick={run} disabled={busy || !vessel}>
            {busy ? t('whatIfRunning') : t('whatIfRun')}</button>
        </div>
      )}
      {result && (
        <div aria-live="polite" style={{ marginTop: 10 }}>
          <p>{fill('whatIfSummary', { vessel: result.vessel, d: result.delay, n: result.containers.length,
                                      add: result.new_overloads, fix: result.resolved_overloads })}</p>
          {result.days.length === 0
            ? <p className="muted">{t('whatIfNoChange')}</p>
            : (
              <div className="table-wrap">
                <table className="grid auto-table">
                  <thead><tr>
                    <th>{t('whatIfColDay')}</th><th>{t('whatIfColWarehouse')}</th>
                    <th>{t('whatIfColBefore')}</th><th>{t('whatIfColAfter')}</th><th>{t('whatIfColLimit')}</th>
                  </tr></thead>
                  <tbody>
                    {result.days.map(d => (
                      <tr key={`${d.warehouse}-${d.day}`} className={d.over_after && !d.over_before ? 'whatif-new' : ''}>
                        <td data-label={t('whatIfColDay')}>{formatDate(d.day)}</td>
                        <td data-label={t('whatIfColWarehouse')}>{d.warehouse}</td>
                        <td data-label={t('whatIfColBefore')}>{d.before} {mark(d.over_before)}</td>
                        <td data-label={t('whatIfColAfter')}>{d.after} {mark(d.over_after)}</td>
                        <td data-label={t('whatIfColLimit')}>{d.limit}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          {result.containers.length > 0 && (
            <details style={{ marginTop: 8 }}>
              <summary>{fill('whatIfMoved', { n: result.containers.length })}</summary>
              <ul className="whatif-moved">
                {result.containers.map(c => (
                  <li key={c.id}>
                    <Link className="mono" to={`/kontenery/${c.id}`}>{c.container_no}</Link>{' '}
                    {c.warehouse}: {formatDate(c.from)} → {formatDate(c.to)}
                  </li>
                ))}
              </ul>
            </details>
          )}
          <p className="muted" style={{ fontSize: 12 }}>{t('whatIfNoWrite')}</p>
        </div>
      )}
    </section>
  )
}
