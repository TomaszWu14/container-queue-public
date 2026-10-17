// Kreator reguł bez kodu (US-036): lista reguł „gdy warunek → powiadom”, podgląd na dzisiejszych
// danych (w zakresie użytkownika) i zapis całej listy (tylko admin, audyt po stronie serwera).
import { useEffect, useState } from 'react'
import { api, errorMessage } from '../api'
import { useT } from '../i18n'

type Condition = 'eta_passed' | 'notify_soon_status' | 'no_driver' | 'plan_unconfirmed'
export interface AutomationRule {
  id: string; name: string; enabled: boolean; condition: Condition; days: number
  status: string | null; notify: 'watchers' | 'admins'
}
interface RulesResponse { rules: AutomationRule[]; conditions: Condition[]; statuses: string[]; max_rules: number }
interface Preview { count: number; sample: { id: number; container_no: string }[] }

const NEW_RULE: AutomationRule = {
  id: '', name: '', enabled: true, condition: 'no_driver', days: 2, status: null, notify: 'watchers',
}

export default function AutomationRulesPanel({ canEdit }: { canEdit: boolean }) {
  const t = useT()
  const [data, setData] = useState<RulesResponse | null>(null)
  const [rules, setRules] = useState<AutomationRule[]>([])
  const [previews, setPreviews] = useState<Record<number, Preview | string>>({})
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    api.get<RulesResponse>('/api/automations/rules')
      .then(r => { if (Array.isArray(r?.rules)) { setData(r); setRules(r.rules) } }).catch(err => setMsg({ ok: false, text: errorMessage(err) }))
  }, [])
  if (!data) return msg ? <p className="error">{msg.text}</p> : null

  const fill = (key: string, vars: Record<string, string | number>) =>
    Object.entries(vars).reduce((s, [k, v]) => s.replace(`{${k}}`, String(v)), t(key))
  const describe = (r: AutomationRule) =>
    fill(`ruleCond_${r.condition}`, { n: r.days, s: r.status ? t(`st_${r.status}`) : '…' })
  const update = (i: number, patch: Partial<AutomationRule>) => {
    setRules(rs => rs.map((r, j) => {
      if (j !== i) return r
      const next = { ...r, ...patch }
      if (next.condition === 'notify_soon_status' && !next.status) next.status = 'ODPRAWA'
      if (next.condition !== 'notify_soon_status') next.status = null
      return next
    }))
    setPreviews(p => { const { [i]: _drop, ...rest } = p; return rest })
  }

  const preview = async (i: number) => {
    const r = rules[i]
    const q = new URLSearchParams({ condition: r.condition, days: String(r.days) })
    if (r.status) q.set('status', r.status)
    try {
      const p = await api.get<Preview>(`/api/automations/rules/preview?${q}`)
      setPreviews(ps => ({ ...ps, [i]: p }))
    } catch (err) {
      setPreviews(ps => ({ ...ps, [i]: errorMessage(err) }))
    }
  }

  const save = async () => {
    setBusy(true)
    setMsg(null)
    try {
      const r = await api.put<RulesResponse>('/api/automations/rules', { rules })
      setRules(r.rules)
      setMsg({ ok: true, text: t('ruleSaved') })
    } catch (err) {
      setMsg({ ok: false, text: errorMessage(err) })
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="panel auto-rules" aria-label={t('ruleTitle')} style={{ marginTop: 18 }}>
      <h2 className="as-h3">{t('ruleTitle')}</h2>
      <p className="muted" style={{ marginTop: 0 }}>{t('ruleIntro')}</p>
      {!canEdit && <p className="muted">{t('ruleReadOnly')}</p>}
      {rules.length === 0 && <p className="muted">{t('ruleEmpty')}</p>}
      <ol className="auto-rule-list">
        {rules.map((r, i) => {
          const p = previews[i]
          return (
            <li key={r.id || `new-${i}`} className="auto-rule" data-testid="auto-rule">
              {canEdit ? (
                <div className="row" style={{ gap: 8, flexWrap: 'wrap', alignItems: 'flex-end' }}>
                  <label>{t('ruleName')}
                    <input value={r.name} maxLength={80} onChange={e => update(i, { name: e.target.value })} /></label>
                  <label>{t('ruleCondition')}
                    <select value={r.condition} onChange={e => update(i, { condition: e.target.value as Condition })}>
                      {data.conditions.map(c => <option key={c} value={c}>{fill(`ruleCond_${c}`, { n: 'N', s: '…' })}</option>)}
                    </select></label>
                  <label>{t('ruleDays')}
                    <input type="number" min={0} max={60} style={{ width: 70 }} value={r.days}
                           onChange={e => update(i, { days: Number(e.target.value) })} /></label>
                  {r.condition === 'notify_soon_status' && (
                    <label>{t('ruleStatus')}
                      <select value={r.status ?? ''} onChange={e => update(i, { status: e.target.value })}>
                        {data.statuses.map(s => <option key={s} value={s}>{t(`st_${s}`)}</option>)}
                      </select></label>
                  )}
                  <label>{t('ruleNotify')}
                    <select value={r.notify} onChange={e => update(i, { notify: e.target.value as AutomationRule['notify'] })}>
                      <option value="watchers">{t('ruleNotify_watchers')}</option>
                      <option value="admins">{t('ruleNotify_admins')}</option>
                    </select></label>
                  <label className="row" style={{ gap: 6 }}>
                    <input type="checkbox" checked={r.enabled} onChange={e => update(i, { enabled: e.target.checked })} />
                    {t('ruleEnabled')}</label>
                  <button type="button" className="btn ghost small"
                          onClick={() => setRules(rs => rs.filter((_, j) => j !== i))}>{t('ruleDelete')}</button>
                </div>
              ) : (
                <b>{r.name}{r.enabled ? '' : ` (${t('autoStatus_off')})`}</b>
              )}
              <div className="row" style={{ gap: 8, marginTop: 4, flexWrap: 'wrap' }}>
                <span className="muted">{describe(r)} → {t(`ruleNotify_${r.notify}`)}</span>
                <button type="button" className="btn secondary small" onClick={() => preview(i)}>{t('rulePreview')}</button>
                {typeof p === 'string' && <span className="error">{p}</span>}
                {p && typeof p !== 'string' && (
                  <span role="status">{p.count
                    ? `${fill('rulePreviewResult', { n: p.count })}: ${p.sample.map(s => s.container_no).join(', ')}${p.count > p.sample.length ? '…' : ''}`
                    : t('rulePreviewNone')}</span>
                )}
              </div>
            </li>
          )
        })}
      </ol>
      {canEdit && (
        <div className="row" style={{ gap: 8 }}>
          <button type="button" className="btn secondary" disabled={rules.length >= data.max_rules}
                  title={rules.length >= data.max_rules ? fill('ruleLimit', { n: data.max_rules }) : undefined}
                  onClick={() => setRules(rs => [...rs, { ...NEW_RULE }])}>{t('ruleAdd')}</button>
          <button type="button" className="btn" disabled={busy} onClick={save}>{busy ? t('loading') : t('ruleSave')}</button>
        </div>
      )}
      {msg && <p className={msg.ok ? 'muted' : 'error'}>{msg.text}</p>}
    </section>
  )
}
