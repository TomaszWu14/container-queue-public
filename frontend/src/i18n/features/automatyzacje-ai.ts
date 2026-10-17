import { defineFeature } from '../feature'

// Jakość odczytu faktur przez AI (US-037): reguły / model ML / człowiek i trafność podpowiedzi wg pewności.
export default defineFeature({
  pl: {
    aiqTitle: 'Odczyt faktur: automat i człowiek', aiqIntro: 'Każda pozycja faktury jest dopasowywana do kartoteki: najpierw regułami, potem modelem uczonym na decyzjach operatorów. Pewne podpowiedzi automat stosuje sam, niepewne trafiają do człowieka — a każda poprawka uczy model.',
    aiqAutomated: 'Pozycji dopasowanych automatycznie', aiqHit: 'Trafność podpowiedzi modelu', aiqItems: 'Pozycji faktur · {weeks} tyg.',
    aiqSrc_rules: 'Reguły', aiqSrc_ml: 'Model ML', aiqSrc_user: 'Człowiek', aiqSrc_open: 'Do decyzji',
    aiqWeekly: 'Kto dopasował pozycje — tydzień po tygodniu', aiqWeekOf: 'tydzień od {d}',
    aiqCalibration: 'Trafność wg pewności modelu', aiqColBucket: 'Pewność', aiqColSuggested: 'Podpowiedzi',
    aiqColDecided: 'Rozstrzygnięte', aiqColHits: 'Trafione', aiqColHitPct: 'Trafność',
    aiqBucket_low: 'poniżej 70% — tylko podpowiedź', aiqBucket_high: '70%–próg — tylko podpowiedź',
    aiqBucket_auto: 'od {t}% — automat ustawia sam',
    aiqEmpty: 'Brak faktur w tym okresie.', aiqNone: '—',
  },
  en: {
    aiqTitle: 'Invoice reading: automation and people', aiqIntro: 'Each invoice line is matched to master data: first by rules, then by a model trained on operators’ decisions. Confident suggestions are applied automatically, uncertain ones go to a person — and every correction teaches the model.',
    aiqAutomated: 'Lines matched automatically', aiqHit: 'Model suggestion accuracy', aiqItems: 'Invoice lines · {weeks} wk',
    aiqSrc_rules: 'Rules', aiqSrc_ml: 'ML model', aiqSrc_user: 'Person', aiqSrc_open: 'Pending',
    aiqWeekly: 'Who matched the lines — week by week', aiqWeekOf: 'week of {d}',
    aiqCalibration: 'Accuracy by model confidence', aiqColBucket: 'Confidence', aiqColSuggested: 'Suggestions',
    aiqColDecided: 'Decided', aiqColHits: 'Correct', aiqColHitPct: 'Accuracy',
    aiqBucket_low: 'below 70% — suggestion only', aiqBucket_high: '70%–threshold — suggestion only',
    aiqBucket_auto: 'from {t}% — applied automatically',
    aiqEmpty: 'No invoices in this period.', aiqNone: '—',
  },
  pt: {
    aiqTitle: 'Leitura de faturas: automatização e pessoas', aiqIntro: 'Cada linha da fatura é associada aos dados mestre: primeiro por regras, depois por um modelo treinado com as decisões dos operadores. As sugestões seguras aplicam-se sozinhas, as incertas vão para uma pessoa — e cada correção ensina o modelo.',
    aiqAutomated: 'Linhas associadas automaticamente', aiqHit: 'Precisão das sugestões do modelo', aiqItems: 'Linhas de faturas · {weeks} sem.',
    aiqSrc_rules: 'Regras', aiqSrc_ml: 'Modelo ML', aiqSrc_user: 'Pessoa', aiqSrc_open: 'Por decidir',
    aiqWeekly: 'Quem associou as linhas — semana a semana', aiqWeekOf: 'semana de {d}',
    aiqCalibration: 'Precisão por confiança do modelo', aiqColBucket: 'Confiança', aiqColSuggested: 'Sugestões',
    aiqColDecided: 'Decididas', aiqColHits: 'Corretas', aiqColHitPct: 'Precisão',
    aiqBucket_low: 'abaixo de 70% — só sugestão', aiqBucket_high: '70%–limiar — só sugestão',
    aiqBucket_auto: 'a partir de {t}% — aplicada automaticamente',
    aiqEmpty: 'Sem faturas neste período.', aiqNone: '—',
  },
})
