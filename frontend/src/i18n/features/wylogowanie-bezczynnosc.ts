// Wylogowanie po bezczynności — komunikat na ekranie logowania (idleLogout.ts)
import { defineFeature } from '../feature'

export default defineFeature({
  pl: { idleLoggedOut: 'Wylogowano po dłuższej bezczynności. Zaloguj się ponownie.' },
  en: { idleLoggedOut: 'You were signed out after a period of inactivity. Please sign in again.' },
  pt: { idleLoggedOut: 'Sessão terminada após um período de inatividade. Inicie sessão novamente.' },
})
