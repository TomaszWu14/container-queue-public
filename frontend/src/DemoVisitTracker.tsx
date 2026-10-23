import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { api } from './api'

// Konto demo (user.is_demo): przy każdej zmianie ekranu lekki sygnał do statystyki gościa bramki
// (backend: app/visitor_activity.py). Ciasteczko gościa jest HttpOnly — front go nie widzi, więc
// sygnał idzie zawsze na koncie demo, a serwer liczy tylko gościa z ważnym ciasteczkiem bramki.
// Wysyłamy samą ścieżkę (bez ?query i #) — błąd sieci nic nie zmienia na ekranie.
export default function DemoVisitTracker() {
  const { pathname } = useLocation()
  useEffect(() => {
    Promise.resolve().then(() => api.post('/api/public/demo-visitor/view', { path: pathname }))
      .catch(() => { /* statystyka — bez komunikatu */ })
  }, [pathname])
  return null
}
