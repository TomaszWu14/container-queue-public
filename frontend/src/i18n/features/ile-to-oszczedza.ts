import { defineFeature } from '../feature'

// Panel „Ile to oszczędza” na pulpicie (ValueCard) — dane za ostatnie N dni, jawne założenie minut
export default defineFeature({
  pl: {
    valueTitle: 'Ile to oszczędza', valuePeriod: 'ostatnie {days} dni',
    valueHours: 'Czas pracy zaoszczędzony', valueHoursSub: '{n} zmian w aplikacji × {m} min (założenie)',
    valueOnTime: 'Dostawy na czas', valueOfDelivered: '{a} z {b} dostarczonych',
    valueDocs: 'Komplet dokumentów u agencji', valueOfContainers: '{a} z {b} kontenerów w odprawie',
    valueDemurrage: 'Ostrzeżenia o karach za przestój', valueDemurrageSub: 'kontenery ostrzeżone z wyprzedzeniem',
  },
  en: {
    valueTitle: 'What it saves', valuePeriod: 'last {days} days',
    valueHours: 'Work time saved', valueHoursSub: '{n} changes in the app × {m} min (assumption)',
    valueOnTime: 'On-time deliveries', valueOfDelivered: '{a} of {b} delivered',
    valueDocs: 'Complete documents at the agency', valueOfContainers: '{a} of {b} containers in clearance',
    valueDemurrage: 'Demurrage warnings', valueDemurrageSub: 'containers warned in advance',
  },
  pt: {
    valueTitle: 'Quanto poupa', valuePeriod: 'últimos {days} dias',
    valueHours: 'Tempo de trabalho poupado', valueHoursSub: '{n} alterações na aplicação × {m} min (pressuposto)',
    valueOnTime: 'Entregas a tempo', valueOfDelivered: '{a} de {b} entregues',
    valueDocs: 'Documentos completos no despachante', valueOfContainers: '{a} de {b} contentores em desalfandegamento',
    valueDemurrage: 'Avisos de sobreestadia', valueDemurrageSub: 'contentores avisados com antecedência',
  },
})
