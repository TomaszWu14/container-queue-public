import { defineFeature } from '../feature'

// Ograniczenia widoków konta demo (demoLimits.ts): profil bez ustawień bezpieczeństwa
export default defineFeature({
  pl: {
    demoProfileInfo: 'Wersja demo — konto jest wspólne dla wszystkich odwiedzających, więc zdjęcie, logowanie dwuetapowe i sesje są tu wyłączone.',
  },
  en: {
    demoProfileInfo: 'Demo version — the account is shared by all visitors, so the photo, two-step login and sessions are disabled here.',
  },
  pt: {
    demoProfileInfo: 'Versão de demonstração — a conta é partilhada por todos os visitantes, por isso a foto, o login em dois passos e as sessões estão desativados.',
  },
})
