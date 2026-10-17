import { defineFeature } from '../feature'

// Wywołania MAG-1: jeden baner zamiast surowego „POWERBI_PROVIDER=off” (audyt UI B19)
export default defineFeature({
  pl: { pcPbiOff: 'Integracja Power BI jest wyłączona — dane stanów MAG-1 są niedostępne. Skontaktuj się z administratorem.' },
  en: { pcPbiOff: 'Power BI integration is turned off — MAG-1 stock data is unavailable. Contact your administrator.' },
  pt: { pcPbiOff: 'A integração Power BI está desativada — os dados de stock MAG-1 não estão disponíveis. Contacte o administrador.' },
})
