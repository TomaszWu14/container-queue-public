import { defineFeature } from '../feature'

// „Wyślij plan” w kolejce (US-017): propozycje dat do spedytora mailem, potwierdzenie w aplikacji
export default defineFeature({
  pl: {
    kqbSendPlan: 'Wyślij plan',
    sendPlanConfirm: 'Wysłać spedytorom proponowane daty dostaw dla {n} kontenerów? Dostaną maila z linkiem do potwierdzenia w aplikacji.',
    sendPlanSent: 'Plan wysłany: {n} kont.',
    sendPlanMailed: 'mail: {list}',
    sendPlanNoEmail: 'brak adresu e-mail: {list}',
    sendPlanMailFailed: 'mail nie wyszedł: {list}',
    sendPlanNoForwarder: 'bez spedytora: {list}',
    sendPlanSkipped: 'już potwierdzone: {list}',
  },
  en: {
    kqbSendPlan: 'Send plan',
    sendPlanConfirm: 'Send the proposed delivery dates for {n} containers to the forwarders? They will get an e-mail with a link to confirm in the app.',
    sendPlanSent: 'Plan sent: {n} cont.',
    sendPlanMailed: 'e-mail: {list}',
    sendPlanNoEmail: 'no e-mail address: {list}',
    sendPlanMailFailed: 'e-mail not sent: {list}',
    sendPlanNoForwarder: 'no forwarder: {list}',
    sendPlanSkipped: 'already confirmed: {list}',
  },
  pt: {
    kqbSendPlan: 'Enviar plano',
    sendPlanConfirm: 'Enviar aos transitários as datas de entrega propostas para {n} contentores? Receberão um e-mail com um link para confirmar na aplicação.',
    sendPlanSent: 'Plano enviado: {n} cont.',
    sendPlanMailed: 'e-mail: {list}',
    sendPlanNoEmail: 'sem endereço de e-mail: {list}',
    sendPlanMailFailed: 'e-mail não enviado: {list}',
    sendPlanNoForwarder: 'sem transitário: {list}',
    sendPlanSkipped: 'já confirmados: {list}',
  },
})
