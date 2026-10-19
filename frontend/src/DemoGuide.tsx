// Interaktywny przewodnik po demo (US-081, czwarta lista PO, pkt 14): przechodzi po kolei przez ekrany,
// podświetla miejsce, na które warto spojrzeć, i mówi jednym zdaniem, co tam widać. Karta na dole ekranu
// (działa też na telefonie), „Dalej / Wstecz / Zakończ”, Escape zamyka. Bez zapisu w bazie.
import { useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'
import { useNavigate } from 'react-router-dom'
import { useT } from './i18n'

export interface GuideStep { path: string; selector: string; key: string; roles?: string[] }

export const GUIDE_STEPS: GuideStep[] = [
  { path: '/kolejka', selector: 'table.kq-table, table.grid', key: 'queue' },
  { path: '/pulpit', selector: '.ctl-kpis', key: 'dashboard' },
  { path: '/kalendarz', selector: 'main .panel, main', key: 'calendar' },
  { path: '/sledzenie', selector: 'main .panel, main', key: 'tracking' },
  { path: '/automatyzacje', selector: '.auto-table', key: 'automations', roles: ['admin', 'logistics'] },
  { path: '/automatyzacje', selector: '.panel.sim', key: 'simulate', roles: ['admin', 'logistics'] },
  { path: '/jak-zbudowano', selector: 'main .panel', key: 'built' },
]
const HIGHLIGHT = 'tour-highlight'

export function stepsFor(role: string): GuideStep[] {
  return GUIDE_STEPS.filter(s => !s.roles || s.roles.includes(role))
}

export default function DemoGuide({ steps, index, onIndex, onClose }: {
  steps: GuideStep[]; index: number; onIndex: (i: number) => void; onClose: () => void
}) {
  const t = useT()
  const navigate = useNavigate()
  const nextRef = useRef<HTMLButtonElement>(null)
  const step = steps[index]

  useEffect(() => {
    navigate(step.path)
    let scrolled = false
    // ekran ładuje się leniwie i doładowuje dane (bywa przerysowany) — przez cały krok pilnujemy,
    // żeby cel był podświetlony; przewijamy do niego raz, gdy pojawi się pierwszy raz
    const timer = window.setInterval(() => {
      const el = document.querySelector(step.selector)
      if (!el) return
      el.classList.add(HIGHLIGHT)
      if (!scrolled) {
        scrolled = true
        el.scrollIntoView?.({ block: 'start' })   // cel u góry, karta przewodnika na dole go nie zasłania
      }
    }, 100)
    nextRef.current?.focus()
    return () => {
      window.clearInterval(timer)
      document.querySelectorAll(`.${HIGHLIGHT}`).forEach(e => e.classList.remove(HIGHLIGHT))
    }
  }, [index])  // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {   // miejsce pod treścią na kartę — ostatnie elementy strony da się przewinąć nad nią
    document.body.classList.add('tour-active')
    return () => document.body.classList.remove('tour-active')
  }, [])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const last = index === steps.length - 1
  return createPortal(
    <div className="tour-card" role="dialog" aria-label={t('tourTitle')} aria-live="polite">
      <div className="muted tour-count">{t('tourStep').replace('{n}', String(index + 1)).replace('{total}', String(steps.length))}</div>
      <b>{t(`tour_${step.key}_title`)}</b>
      <p>{t(`tour_${step.key}_body`)}</p>
      <div className="tour-actions">
        <button type="button" className="btn ghost small" onClick={onClose}>{t('tourEnd')}</button>
        <span style={{ flex: 1 }} />
        {index > 0 && <button type="button" className="btn secondary small" onClick={() => onIndex(index - 1)}>{t('tourBack')}</button>}
        <button type="button" ref={nextRef} className="btn small" onClick={() => (last ? onClose() : onIndex(index + 1))}>
          {last ? t('tourDone') : t('tourNext')}
        </button>
      </div>
    </div>,
    document.body,
  )
}
