import { defineFeature } from '../feature'

// Asystent bez modelu AI (US-039): przykładowe pytania i oznaczenie odpowiedzi z szablonu.
export default defineFeature({
  pl: {
    asExamples: 'Przykładowe pytania',
    asTemplateNote: 'Odpowiedź z szablonu, złożona z danych systemu — na tym serwerze nie działa model AI.',
  },
  en: {
    asExamples: 'Example questions',
    asTemplateNote: 'Template answer built from system data — no AI model runs on this server.',
  },
  pt: {
    asExamples: 'Perguntas de exemplo',
    asTemplateNote: 'Resposta de modelo fixo, construída com dados do sistema — não há modelo de IA neste servidor.',
  },
})
