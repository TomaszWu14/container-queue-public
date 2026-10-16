import { defineFeature } from '../feature'

// „Przebieg” kontenera w zakładce historii (ContainerStory): kamienie milowe procesu
export default defineFeature({
  pl: {
    storyTitle: 'Przebieg', storyAllChanges: 'Wszystkie zmiany',
    storyEmpty: 'Brak kroków procesu do pokazania — szczegóły w tabeli zmian niżej.',
    storyStatus: 'Status: {v}', storyCustoms: 'Odprawa: {v}', storyAgency: 'Zlecono odprawę agencji {v}',
    storyDocsSent: 'Dokumenty przekazane agencji', storyDocsSentMissing: 'Dokumenty przekazane agencji mimo braków',
    storyAgencyMail: 'Przygotowano mail do agencji z dokumentami', storyDocAdded: 'Dodano dokument: {v}',
    storyPlanSent: 'Plan wysłany do spedycji', storyPlanConfirmed: 'Spedycja potwierdziła termin',
    storyDelivery: 'Termin dostawy: {v}', storySlot: 'Godzina dostawy: {v}', storyDocsMissing: 'Braki dokumentów: {v}',
  },
  en: {
    storyTitle: 'Timeline', storyAllChanges: 'All changes',
    storyEmpty: 'No process steps to show — details in the change table below.',
    storyStatus: 'Status: {v}', storyCustoms: 'Customs: {v}', storyAgency: 'Clearance ordered from agency {v}',
    storyDocsSent: 'Documents handed to the agency', storyDocsSentMissing: 'Documents handed to the agency despite gaps',
    storyAgencyMail: 'E-mail to the agency prepared with documents', storyDocAdded: 'Document added: {v}',
    storyPlanSent: 'Plan sent to the forwarder', storyPlanConfirmed: 'Forwarder confirmed the date',
    storyDelivery: 'Delivery date: {v}', storySlot: 'Delivery time: {v}', storyDocsMissing: 'Missing documents: {v}',
  },
  pt: {
    storyTitle: 'Percurso', storyAllChanges: 'Todas as alterações',
    storyEmpty: 'Sem etapas do processo para mostrar — detalhes na tabela de alterações abaixo.',
    storyStatus: 'Estado: {v}', storyCustoms: 'Desalfandegamento: {v}', storyAgency: 'Desalfandegamento pedido ao despachante {v}',
    storyDocsSent: 'Documentos entregues ao despachante', storyDocsSentMissing: 'Documentos entregues ao despachante apesar de faltas',
    storyAgencyMail: 'E-mail ao despachante preparado com documentos', storyDocAdded: 'Documento adicionado: {v}',
    storyPlanSent: 'Plano enviado ao transitário', storyPlanConfirmed: 'O transitário confirmou a data',
    storyDelivery: 'Data de entrega: {v}', storySlot: 'Hora de entrega: {v}', storyDocsMissing: 'Documentos em falta: {v}',
  },
})
