import { defineFeature } from '../feature'

// Zdarzenia do n8n (US-035): przycisk „Wyślij zdarzenie testowe” na ekranie Automatyzacje (admin).
export default defineFeature({
  pl: {
    autoTestEventBtn: 'Wyślij zdarzenie testowe',
    autoTestEventOk: 'Zdarzenie testowe dotarło (HTTP {code}).',
    autoTestEventUnsigned: 'Uwaga: bez podpisu HMAC — ustaw AUTOMATION_WEBHOOK_SECRET.',
    autoTestEventFail: 'Odbiorca nie przyjął zdarzenia: {error}. Szczegóły w Administracja → Logi → Zadania.',
  },
  en: {
    autoTestEventBtn: 'Send a test event',
    autoTestEventOk: 'The test event arrived (HTTP {code}).',
    autoTestEventUnsigned: 'Note: no HMAC signature — set AUTOMATION_WEBHOOK_SECRET.',
    autoTestEventFail: 'The receiver rejected the event: {error}. Details in Administration → Logs → Jobs.',
  },
  pt: {
    autoTestEventBtn: 'Enviar evento de teste',
    autoTestEventOk: 'O evento de teste chegou (HTTP {code}).',
    autoTestEventUnsigned: 'Atenção: sem assinatura HMAC — defina AUTOMATION_WEBHOOK_SECRET.',
    autoTestEventFail: 'O destinatário rejeitou o evento: {error}. Detalhes em Administração → Registos → Tarefas.',
  },
})
