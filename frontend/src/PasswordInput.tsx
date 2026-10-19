import { useState, type InputHTMLAttributes } from 'react'
import { Eye, EyeOff } from 'lucide-react'
import { useT } from './i18n'
import { passwordStrength } from './passwordStrength'

type Props = Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> & { showStrength?: boolean }

/** Pole hasła z przyciskiem „pokaż / ukryj” (ASVS 2.1.12) i opcjonalnym miernikiem siły (2.1.8), US-090. */
export default function PasswordInput({ showStrength, className, ...rest }: Props) {
  const t = useT()
  const [visible, setVisible] = useState(false)
  const value = typeof rest.value === 'string' ? rest.value : ''
  const level = passwordStrength(value)
  return (
    <span className="pw-wrap">
      <span className="pw-field">
        <input {...rest} className={className} type={visible ? 'text' : 'password'} />
        <button type="button" className="pw-toggle" aria-pressed={visible}
                aria-label={t(visible ? 'pwHide' : 'pwShow')} title={t(visible ? 'pwHide' : 'pwShow')}
                onClick={() => setVisible(v => !v)}>
          {visible ? <EyeOff size={16} aria-hidden="true" /> : <Eye size={16} aria-hidden="true" />}
        </button>
      </span>
      {showStrength && value && (
        <span className={`pw-meter pw-meter-${level}`} role="status" aria-live="polite">
          <span className="pw-bar" aria-hidden="true"><span /></span>
          <span className="pw-label">{t('pwStrength')}: {t(`pwStrength${level}`)}</span>
        </span>
      )}
    </span>
  )
}
