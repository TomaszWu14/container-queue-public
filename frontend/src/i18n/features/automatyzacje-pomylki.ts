import { defineFeature } from '../feature'

// Pomyłki modelu do przeglądu (druga lista PO, pkt 8).
export default defineFeature({
  pl: {
    aiqMistakesTitle: 'Pomyłki modelu do przeglądu', aiqMistakesNone: 'Brak poprawek człowieka w ostatnim czasie.',
    aiqMisContainer: 'Kontener / faktura', aiqMisLine: 'Pozycja', aiqMisSuggested: 'Podpowiedź modelu',
    aiqMisChosen: 'Wybrał człowiek', aiqMisConfidence: 'Pewność', aiqMisAuto: 'automat',
    aiqMisAutoHint: 'Pewność od progu — automat ustawiłby tę pozycję sam. Sprawdź regułę albo kartotekę.',
  },
  en: {
    aiqMistakesTitle: 'Model mistakes to review', aiqMistakesNone: 'No human corrections recently.',
    aiqMisContainer: 'Container / invoice', aiqMisLine: 'Line', aiqMisSuggested: 'Model suggestion',
    aiqMisChosen: 'Chosen by a person', aiqMisConfidence: 'Confidence', aiqMisAuto: 'automatic',
    aiqMisAutoHint: 'Confidence at or above the threshold — the automation would have applied this line itself. Check the rule or master data.',
  },
  pt: {
    aiqMistakesTitle: 'Erros do modelo para rever', aiqMistakesNone: 'Sem correções humanas recentes.',
    aiqMisContainer: 'Contentor / fatura', aiqMisLine: 'Linha', aiqMisSuggested: 'Sugestão do modelo',
    aiqMisChosen: 'Escolhido por uma pessoa', aiqMisConfidence: 'Confiança', aiqMisAuto: 'automático',
    aiqMisAutoHint: 'Confiança igual ou acima do limiar — a automatização teria aplicado esta linha sozinha. Verifique a regra ou os dados mestre.',
  },
})
