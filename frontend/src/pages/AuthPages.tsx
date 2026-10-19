import { FormEvent, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { api, errorMessage } from '../api'
import { useT } from '../i18n'
import PasswordInput from '../PasswordInput'

// Publiczne (bez logowania): prośba o reset i ustawienie nowego hasła.

export function ForgotPasswordPage() {
  const t = useT()
  const [email, setEmail] = useState('')
  const [busy, setBusy] = useState(false)
  const [sent, setSent] = useState(false)

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setBusy(true)
    try {
      await api.post('/api/auth/forgot-password', { email })
    } catch { /* anty-enumeracja: nie ujawniamy błędów */ }
    setSent(true)   // zawsze ten sam komunikat, niezależnie od wyniku
    setBusy(false)
  }

  return (
    <div className="login-wrap">
      <form className="login-card" onSubmit={submit}>
        <h1>{t('forgotTitle')}</h1>
        {sent ? (
          <p style={{ color: 'var(--muted)' }}>{t('forgotSent')}</p>
        ) : (
          <>
            <label>{t('forgotEmail')}
              <input type="email" value={email} autoFocus
                     onChange={e => setEmail(e.target.value)} />
            </label>
            <button className="btn" disabled={busy || !email}>{t('forgotSend')}</button>
          </>
        )}
        <a href="/" className="login-link">{t('backToLogin')}</a>
      </form>
    </div>
  )
}

// Wymuszona zmiana hasła (zalogowany użytkownik z zaproszenia): blokuje aplikację,
// dopóki nie ustawi własnego hasła. onDone przeładowuje konto (czyści flagę).
export function ChangePasswordPage({ onDone }: { onDone: () => void }) {
  const t = useT()
  const [password, setPassword] = useState('')
  const [repeat, setRepeat] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    if (password.length < 8) { setError(t('passwordTooShort')); return }
    if (password !== repeat) { setError(t('passwordsMismatch')); return }
    setBusy(true)
    try {
      await api.post('/api/auth/change-password', { new_password: password })
      onDone()
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="login-wrap">
      <form className="login-card" onSubmit={submit}>
        <h1>{t('mustChangeTitle')}</h1>
        <p style={{ color: 'var(--muted)' }}>{t('mustChangeInfo')}</p>
        <div className="pw-labelled">
          <label htmlFor="change-pw-new">{t('newPassword')}</label>
          <PasswordInput id="change-pw-new" value={password} autoFocus autoComplete="new-password" showStrength
            onChange={e => setPassword(e.target.value)} />
        </div>
        <div className="pw-labelled">
          <label htmlFor="change-pw-repeat">{t('repeatPassword')}</label>
          <PasswordInput id="change-pw-repeat" value={repeat} autoComplete="new-password"
            onChange={e => setRepeat(e.target.value)} />
        </div>
        {error && <p className="error">{error}</p>}
        <button className="btn" disabled={busy || !password || !repeat}>{t('resetSet')}</button>
      </form>
    </div>
  )
}

export function ResetPasswordPage() {
  const t = useT()
  const [params] = useSearchParams()
  const token = params.get('token') ?? ''
  const [password, setPassword] = useState('')
  const [repeat, setRepeat] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [done, setDone] = useState(false)

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    if (password.length < 8) { setError(t('passwordTooShort')); return }
    if (password !== repeat) { setError(t('passwordsMismatch')); return }
    setBusy(true)
    try {
      await api.post('/api/auth/reset-password', { token, password })
      setDone(true)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="login-wrap">
      <form className="login-card" onSubmit={submit}>
        <h1>{t('resetTitle')}</h1>
        {!token ? (
          <p className="error">{t('resetNoToken')}</p>
        ) : done ? (
          <p style={{ color: 'var(--muted)' }}>{t('resetDone')}</p>
        ) : (
          <>
            <div className="pw-labelled">
              <label htmlFor="reset-pw-new">{t('newPassword')}</label>
              <PasswordInput id="reset-pw-new" value={password} autoFocus autoComplete="new-password" showStrength
              onChange={e => setPassword(e.target.value)} />
            </div>
            <div className="pw-labelled">
              <label htmlFor="reset-pw-repeat">{t('repeatPassword')}</label>
              <PasswordInput id="reset-pw-repeat" value={repeat} autoComplete="new-password"
              onChange={e => setRepeat(e.target.value)} />
            </div>
            {error && <p className="error">{error}</p>}
            <button className="btn" disabled={busy || !password || !repeat}>{t('resetSet')}</button>
          </>
        )}
        <a href="/" className="login-link">{t('backToLogin')}</a>
      </form>
    </div>
  )
}
