import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { useNavigate } from 'react-router-dom'
import { api } from './api'
import DemoGuide, { stepsFor } from './DemoGuide'
import { useT } from './i18n'
import { Modal } from './Modal'
import { useUser } from './userContext'

// Instancja portfolio (konto z DEMO_READONLY_LOGINS, user.is_demo): stały baner „dane fikcyjne,
// tylko podgląd” + ekran powitalny z czterema miejscami do obejrzenia (zamiast ogólnego onboardingu).
// Pokazuje się raz na przeglądarkę (localStorage), z banera można go otworzyć ponownie.
const SEEN = 'demo-welcome-seen'
const STEPS = [
  { to: '/pulpit', n: 1 },
  { to: '/kolejka', n: 2 },
  { to: '/kalendarz', n: 3 },
  { to: '/sledzenie', n: 4 },
  // US-032: katalog automatyzacji — ekran logistyki (konta demo partnerów go nie mają)
  { to: '/automatyzacje', n: 5, roles: ['admin', 'logistics'] },
]

function seen(): boolean {
  try { return localStorage.getItem(SEEN) === '1' } catch { return false }
}

export default function DemoMode() {
  const t = useT()
  const navigate = useNavigate()
  const role = useUser()?.role ?? ''
  const [open, setOpen] = useState(() => !seen())
  const [support, setSupport] = useState('')
  const [storyId, setStoryId] = useState<number | null>(null)   // kontener pokazowy (seed_demo_story)
  const [guide, setGuide] = useState<number | null>(null)          // US-081: krok przewodnika
  useEffect(() => {
    api.get<{ support_email?: string; demo_story_container_id?: number | null }>('/api/public/branding')
      .then(b => { setSupport(b?.support_email ?? ''); setStoryId(b?.demo_story_container_id ?? null) })
      .catch(() => {})
  }, [])

  const close = () => {
    try { localStorage.setItem(SEEN, '1') } catch { /* tryb prywatny — pokaże się znowu */ }
    setOpen(false)
  }
  const go = (to: string) => { close(); navigate(to) }
  const startGuide = () => { close(); setGuide(0) }

  return (
    <>
      <div className="demo-banner" data-testid="demo-banner" role="status">
        <span>{t('demoBanner')}</span>
        {support && <span>{t('demoBannerReport')} <a href={`mailto:${support}`}>{support}</a></span>}
        <button type="button" className="btn small" onClick={() => setOpen(true)}>
          {t('demoBannerTour')}
        </button>
        <button type="button" className="btn small secondary" onClick={() => setGuide(0)}>
          {t('tourStart')}
        </button>
        <button type="button" className="btn small secondary" onClick={() => navigate('/jak-zbudowano')}>
          {t('hbNav')}
        </button>
      </div>
      {/* portal: tło modala ma ten sam z-index co górny pasek, a pasek stoi w DOM dalej */}
      {open && createPortal(
        <Modal title={t('demoWelcomeTitle')} onClose={close} width={560}>
          <p className="muted" style={{ marginTop: 0 }}>{t('demoWelcomeIntro')}</p>
          <p><button type="button" className="btn" onClick={startGuide}>{t('tourStartLong')}</button></p>
          <ol className="demo-steps">
            {storyId !== null && (
              <li className="demo-step-story">
                <div>
                  <b>{t('demoStoryTitle')}</b>
                  <p className="muted">{t('demoStoryBody')}</p>
                </div>
                <button type="button" className="btn small" onClick={() => go(`/kontenery/${storyId}?akcja=history`)}>
                  {t('demoWelcomeGo')}
                </button>
              </li>
            )}
            {STEPS.filter(s => !s.roles || s.roles.includes(role)).map(s => (
              <li key={s.to}>
                <div>
                  <b>{t(`demoStep${s.n}Title`)}</b>
                  <p className="muted">{t(`demoStep${s.n}Body`)}</p>
                </div>
                <button type="button" className="btn ghost small" onClick={() => go(s.to)}>
                  {t('demoWelcomeGo')}
                </button>
              </li>
            ))}
          </ol>
          <div className="modal-actions" style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button type="button" className="btn" data-autofocus onClick={close}>
              {t('demoWelcomeClose')}
            </button>
          </div>
        </Modal>,
        document.body,
      )}
      {guide !== null && (
        <DemoGuide steps={stepsFor(role)} index={guide} onIndex={setGuide} onClose={() => setGuide(null)} />
      )}
    </>
  )
}
