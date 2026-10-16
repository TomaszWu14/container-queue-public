import { useT } from '../../i18n'
import { formatDateTime } from '../../dates'
import type { AuditEntry } from '../../types'
import { containerStory } from './containerStory'

/** „Przebieg” kontenera: najważniejsze kroki procesu na osi czasu (styl jak oś podróży statku). */
export default function ContainerStory({ history }: { history: AuditEntry[] }) {
  const t = useT()
  const steps = containerStory(history, t)
  if (steps.length === 0) return <p className="muted">{t('storyEmpty')}</p>
  return (
    <ol className="ctimeline cstory" aria-label={t('storyTitle')}>
      {steps.map(s => (
        <li key={s.id} className={`done s-${s.kind}`}>
          <span className="ct-dot" aria-hidden="true" />
          <span className="ct-when">{formatDateTime(s.at)}</span>
          <span>
            <span className="ct-label">{s.text}</span>
            {s.who && <span className="muted" style={{ fontSize: 12 }}> · {s.who}</span>}
          </span>
        </li>
      ))}
    </ol>
  )
}
