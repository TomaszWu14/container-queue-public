import { CircleCheckIcon, ScanLineIcon, XIcon } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { useT } from '../../i18n'
import type { GateItem } from '../GatePage'
import { findGateItem, parseScan } from './gateScan'

// Pomysł 4 PO: ochrona skanuje telefonem kod QR z karty rozładunku (albo wpisuje numer) i jednym
// przyciskiem wpuszcza auto. Odczyt kodu: BarcodeDetector przeglądarki (Chrome/Android) — obraz z aparatu
// zostaje w telefonie, nic nie jest wysyłane. Bez BarcodeDetector zostaje pole na numer.
type Detector = { detect: (source: HTMLVideoElement) => Promise<{ rawValue: string }[]> }
type DetectorCtor = new (opts: { formats: string[] }) => Detector

const detectorCtor = (): DetectorCtor | null =>
  (globalThis as { BarcodeDetector?: DetectorCtor }).BarcodeDetector ?? null

export default function GateScanner({ items, busy, onCheckin, fmtTime }: {
  items: GateItem[]; busy: number; onCheckin: (id: number) => void; fmtTime: (iso: string | null) => string
}) {
  const t = useT()
  const [camera, setCamera] = useState(false)
  const [message, setMessage] = useState('')
  const [foundId, setFoundId] = useState<number | null>(null)
  const [typed, setTyped] = useState('')
  const video = useRef<HTMLVideoElement>(null)
  const found = foundId === null ? null : items.find(i => i.id === foundId) ?? null

  const lookup = (raw: string) => {
    const item = findGateItem(items, parseScan(raw))
    setFoundId(item?.id ?? null)
    setMessage(item ? '' : t('gateScanNotToday'))
    if (item) document.getElementById(`gate-row-${item.id}`)?.scrollIntoView?.({ block: 'center' })
    return item
  }

  useEffect(() => {
    if (!camera) return
    const Ctor = detectorCtor()
    if (!Ctor || !navigator.mediaDevices?.getUserMedia) {
      setMessage(t('gateScanNoCamera')); setCamera(false); return
    }
    let stream: MediaStream | null = null
    let timer = 0
    let stopped = false
    const detector = new Ctor({ formats: ['qr_code'] })
    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: false })
      .then(s => {
        if (stopped) { s.getTracks().forEach(tr => tr.stop()); return }
        stream = s
        if (video.current) { video.current.srcObject = s; void video.current.play() }
        timer = window.setInterval(async () => {
          if (!video.current || video.current.readyState < 2) return
          const codes = await detector.detect(video.current).catch(() => [])
          if (codes.length && !stopped) { lookup(codes[0].rawValue); setCamera(false) }
        }, 300)
      })
      .catch(() => { setMessage(t('gateScanDenied')); setCamera(false) })
    return () => {
      stopped = true
      window.clearInterval(timer)
      stream?.getTracks().forEach(tr => tr.stop())   // aparat gaśnie od razu po odczycie / zamknięciu
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [camera])

  return (
    <section className="panel gate-scan" aria-label={t('gateScanBtn')}>
      <div className="gate-scan-row">
        <button className="btn gate-btn" onClick={() => { setMessage(''); setCamera(c => !c) }}>
          {camera ? <><XIcon size={16} /> {t('gateScanStop')}</> : <><ScanLineIcon size={16} /> {t('gateScanBtn')}</>}
        </button>
        <form className="gate-scan-form" onSubmit={e => { e.preventDefault(); lookup(typed) }}>
          <input value={typed} onChange={e => setTyped(e.target.value)} aria-label={t('gateScanInput')}
                 placeholder={t('gateScanInput')} autoCapitalize="characters" className="mono" />
          <button className="btn secondary" type="submit" disabled={!typed.trim()}>{t('gateScanFind')}</button>
        </form>
      </div>
      {camera && (
        <div className="gate-scan-camera">
          <video ref={video} muted playsInline aria-label={t('gateScanHint')} />
          <p className="muted">{t('gateScanHint')}</p>
        </div>
      )}
      {message && <p className="gate-scan-msg" role="status">{message}</p>}
      {found && (
        <div className="gate-scan-found" role="status">
          <b className="mono gate-no">{found.container_no}</b>
          {(found.truck_no || found.trailer_no) && (
            <span className="mono">{[found.truck_no, found.trailer_no].filter(Boolean).join(' / ')}</span>)}
          {found.driver_name && <span>{found.driver_name}</span>}
          <span className="muted">{found.warehouse}</span>
          {found.checked_in_at
            ? <span className="badge st-DOSTARCZONY">{t('gateScanAlready').replace('{time}', fmtTime(found.checked_in_at))}</span>
            : <button className="btn gate-btn" disabled={busy === found.id} onClick={() => onCheckin(found.id)}>
                <CircleCheckIcon size={16} /> {t('gateScanLetIn')}
              </button>}
        </div>
      )}
    </section>
  )
}
