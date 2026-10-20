// Branding ekranu logowania (/api/public/branding): konto demo, podpowiedź, adres zgłoszeń.
// Chwilowy błąd (wdrożenie, limit zapytań, słaba sieć) nie może po cichu chować przycisku
// „Wejdź jako demo” — ponawiamy kilka razy, a gdy dalej nic, ekran mówi, że serwer nie odpowiada.
import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from '../api'

export type Branding = {
  demo_hint?: string; demo_login?: string; demo_password?: string; support_email?: string
}

export const BRANDING_RETRY_MS = [2_000, 5_000]   // przerwy przed 2. i 3. próbą

export function useBranding() {
  const [brand, setBrand] = useState<Branding>({})
  const [failed, setFailed] = useState(false)
  const run = useRef(0)

  const load = useCallback(() => {
    const id = ++run.current
    setFailed(false)
    const attempt = (n: number) => {
      api.get<Branding>('/api/public/branding')
        .then(b => { if (run.current === id) setBrand(b ?? {}) })
        .catch(() => {
          if (run.current !== id) return
          if (n < BRANDING_RETRY_MS.length) window.setTimeout(() => attempt(n + 1), BRANDING_RETRY_MS[n])
          else setFailed(true)
        })
    }
    attempt(0)
  }, [])

  // odmontowany ekran nie dostaje spóźnionych odpowiedzi (nowy numer przebiegu unieważnia stary)
  const stop = useCallback(() => { run.current++ }, [])
  useEffect(() => { load(); return stop }, [load, stop])

  return { brand, failed, retry: load }
}
