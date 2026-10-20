import { defineFeature } from '../feature'

// Ekran logowania: serwer nie oddał brandingu mimo ponowień (pages/loginBranding.ts)
export default defineFeature({
  pl: {
    brandingUnavailable: 'Serwer chwilowo nie odpowiada — przycisk „Wejdź jako demo” pojawi się, gdy połączenie wróci.',
    brandingRetry: 'Spróbuj ponownie',
  },
  en: {
    brandingUnavailable: 'The server is not responding right now — the “Enter as demo” button will appear once the connection is back.',
    brandingRetry: 'Try again',
  },
  pt: {
    brandingUnavailable: 'O servidor não está a responder neste momento — o botão “Entrar como demo” aparecerá quando a ligação voltar.',
    brandingRetry: 'Tentar novamente',
  },
})
