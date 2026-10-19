import { defineFeature } from '../feature'

// Test reguły na ostatnich 30 dniach (trzecia lista PO, pkt 2).
export default defineFeature({
  pl: {
    ruleBacktest: 'Sprawdź na 30 dniach',
    ruleBacktestResult: 'W ostatnich {d} dniach: {n} alertów o {c} kontenerach (średnio {avg} dziennie, najwięcej {max}).',
    ruleBacktestNone: 'W ostatnich {d} dniach reguła nie wysłałaby żadnego alertu.',
    ruleBacktestNoisy: 'Dużo alertów — rozważ węższy warunek.',
  },
  en: {
    ruleBacktest: 'Test on last 30 days',
    ruleBacktestResult: 'In the last {d} days: {n} alerts about {c} containers (average {avg} a day, at most {max}).',
    ruleBacktestNone: 'In the last {d} days the rule would not have sent any alert.',
    ruleBacktestNoisy: 'Many alerts — consider a narrower condition.',
  },
  pt: {
    ruleBacktest: 'Testar nos últimos 30 dias',
    ruleBacktestResult: 'Nos últimos {d} dias: {n} alertas sobre {c} contentores (média {avg} por dia, no máximo {max}).',
    ruleBacktestNone: 'Nos últimos {d} dias a regra não teria enviado nenhum alerta.',
    ruleBacktestNoisy: 'Muitos alertas — considere uma condição mais restrita.',
  },
})
