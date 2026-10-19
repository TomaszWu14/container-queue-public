import { defineFeature } from '../feature'

// Ponawianie nieudanych wysyłek (US-022, trzecia lista PO, pkt 1).
export default defineFeature({
  pl: {
    delivTitle: 'Wysyłki do ponowienia',
    delivIntro: 'E-mail, karta w Teams albo zdarzenie do n8n, które się nie udały, są ponawiane po 1, 5 i 30 minutach. Tu widać, co czeka i co ostatecznie nie doszło.',
    delivAllGood: 'Wszystkie wysyłki doszły.', delivPending: 'czeka na ponowienie', delivFailed: 'nie doszło',
    delivColChannel: 'Kanał', delivColWhat: 'Czego dotyczy', delivColState: 'Stan', delivColAttempts: 'Próby',
    delivColError: 'Błąd', delivColWhen: 'Następna próba / kiedy',
    delivCh_email: 'e-mail', delivCh_teams: 'Teams', delivCh_n8n: 'n8n',
  },
  en: {
    delivTitle: 'Deliveries to retry',
    delivIntro: 'An e-mail, Teams card or n8n event that failed is retried after 1, 5 and 30 minutes. Here you see what is waiting and what finally did not get through.',
    delivAllGood: 'All deliveries got through.', delivPending: 'waiting for retry', delivFailed: 'not delivered',
    delivColChannel: 'Channel', delivColWhat: 'About', delivColState: 'State', delivColAttempts: 'Attempts',
    delivColError: 'Error', delivColWhen: 'Next attempt / when',
    delivCh_email: 'e-mail', delivCh_teams: 'Teams', delivCh_n8n: 'n8n',
  },
  pt: {
    delivTitle: 'Envios a repetir',
    delivIntro: 'Um e-mail, cartão do Teams ou evento n8n que falhou é repetido após 1, 5 e 30 minutos. Aqui vê o que está à espera e o que acabou por não chegar.',
    delivAllGood: 'Todos os envios chegaram.', delivPending: 'à espera de nova tentativa', delivFailed: 'não entregue',
    delivColChannel: 'Canal', delivColWhat: 'Assunto', delivColState: 'Estado', delivColAttempts: 'Tentativas',
    delivColError: 'Erro', delivColWhen: 'Próxima tentativa / quando',
    delivCh_email: 'e-mail', delivCh_teams: 'Teams', delivCh_n8n: 'n8n',
  },
})
