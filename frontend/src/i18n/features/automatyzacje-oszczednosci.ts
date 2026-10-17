import { defineFeature } from '../feature'

// Licznik oszczędności per automat (US-034): godziny pracy ręcznej zastąpionej przez automaty,
// z jawnymi założeniami minut (Z-024), które admin zmienia w oknie „Założenia minut”.
export default defineFeature({
  pl: {
    autoKpiSaved: 'Zaoszczędzony czas · {days} dni', autoSavedHours: '{h} h',
    autoSavedAssumption: 'założenie: minuty pracy ręcznej na jeden efekt automatu',
    autoColSaved: 'Oszczędność', autoSavedPer: '{m} min × {n}',
    autoMinutesBtn: 'Założenia minut', autoMinutesTitle: 'Minuty pracy ręcznej na jeden efekt',
    autoMinutesInfo: 'Ile minut zajmuje człowiekowi to, co automat robi raz (np. jedno powiadomienie, jedna faktura, jeden mail z poczty). Wartości startowe to założenia do potwierdzenia — zmiana trafia do dziennika zmian.',
    autoMinutesSave: 'Zapisz założenia',
  },
  en: {
    autoKpiSaved: 'Time saved · {days} days', autoSavedHours: '{h} h',
    autoSavedAssumption: 'assumption: minutes of manual work per automation effect',
    autoColSaved: 'Saving', autoSavedPer: '{m} min × {n}',
    autoMinutesBtn: 'Minute assumptions', autoMinutesTitle: 'Manual minutes per effect',
    autoMinutesInfo: 'How many minutes a person needs for what the automation does once (e.g. one notification, one invoice, one e-mail). Starting values are assumptions to be confirmed — changes go to the change log.',
    autoMinutesSave: 'Save assumptions',
  },
  pt: {
    autoKpiSaved: 'Tempo poupado · {days} dias', autoSavedHours: '{h} h',
    autoSavedAssumption: 'pressuposto: minutos de trabalho manual por efeito da automatização',
    autoColSaved: 'Poupança', autoSavedPer: '{m} min × {n}',
    autoMinutesBtn: 'Pressupostos de minutos', autoMinutesTitle: 'Minutos manuais por efeito',
    autoMinutesInfo: 'Quantos minutos uma pessoa precisa para o que a automatização faz uma vez (p. ex. uma notificação, uma fatura, um e-mail). Os valores iniciais são pressupostos a confirmar — as alterações vão para o registo de alterações.',
    autoMinutesSave: 'Guardar pressupostos',
  },
})
