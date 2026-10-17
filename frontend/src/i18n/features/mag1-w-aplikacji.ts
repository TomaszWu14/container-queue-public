import { defineFeature } from '../feature'

// Magazyn MAG-1 (konto, rola warehouse) potwierdza wywołanie w aplikacji zamiast linku z maila (2026-10-07)
export default defineFeature({
  pl: {
    pcStatus_przygotowane: 'Przygotowane w MAG-1', pcStatus_wyslane_z_mag1: 'Wysłane z MAG-1',
    pcMarkPrepared: 'Przygotowane', pcMarkShipped: 'Wysłane z MAG-1',
  },
  en: {
    pcStatus_przygotowane: 'Prepared at MAG-1', pcStatus_wyslane_z_mag1: 'Shipped from MAG-1',
    pcMarkPrepared: 'Prepared', pcMarkShipped: 'Shipped from MAG-1',
  },
  pt: {
    pcStatus_przygotowane: 'Preparado no MAG-1', pcStatus_wyslane_z_mag1: 'Enviado do MAG-1',
    pcMarkPrepared: 'Preparado', pcMarkShipped: 'Enviado do MAG-1',
  },
})
