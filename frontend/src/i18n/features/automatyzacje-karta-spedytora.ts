import { defineFeature } from '../feature'

// Karta spedytora (US-079)
export default defineFeature({
  pl: {
    fwdScoreTitle: 'Karta spedytora',
    fwdScoreIntro: 'Jak spedycje odpowiadają na awizacje w ostatnich {days} dniach: ile odpowiedzi przyszło w ciągu {hours} h, mediana czasu odpowiedzi, prośby o inny termin, zgłoszone problemy i awizacje odesłane do poprawy.',
    fwdScoreEmpty: 'Brak awizacji w tym okresie.',
    fwdScoreColName: 'Spedycja', fwdScoreColRequests: 'Odpowiedzi / awizacje', fwdScoreColOnTime: 'Odpowiedź w {hours} h',
    fwdScoreColMedian: 'Mediana odpowiedzi', fwdScoreColDateChange: 'Inny termin', fwdScoreColProblem: 'Problem',
    fwdScoreColRejected: 'Do poprawy',
  },
  en: {
    fwdScoreTitle: 'Forwarder scorecard',
    fwdScoreIntro: 'How forwarders answer delivery notices over the last {days} days: answers within {hours} h, median response time, date change requests, reported problems and notices sent back for correction.',
    fwdScoreEmpty: 'No delivery notices in this period.',
    fwdScoreColName: 'Forwarder', fwdScoreColRequests: 'Answers / notices', fwdScoreColOnTime: 'Answer within {hours} h',
    fwdScoreColMedian: 'Median response', fwdScoreColDateChange: 'Date change', fwdScoreColProblem: 'Problem',
    fwdScoreColRejected: 'Sent back',
  },
  pt: {
    fwdScoreTitle: 'Cartão do transitário',
    fwdScoreIntro: 'Como os transitários respondem aos avisos de entrega nos últimos {days} dias: respostas em {hours} h, mediana do tempo de resposta, pedidos de outra data, problemas comunicados e avisos devolvidos para correção.',
    fwdScoreEmpty: 'Sem avisos de entrega neste período.',
    fwdScoreColName: 'Transitário', fwdScoreColRequests: 'Respostas / avisos', fwdScoreColOnTime: 'Resposta em {hours} h',
    fwdScoreColMedian: 'Mediana da resposta', fwdScoreColDateChange: 'Outra data', fwdScoreColProblem: 'Problema',
    fwdScoreColRejected: 'Devolvidos',
  },
})
