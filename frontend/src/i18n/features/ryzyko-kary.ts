import { defineFeature } from '../feature'

// Pulpit: ryzyko kary za przestój z wyjaśnieniem (DemurrageRiskCard) — powód i działanie, bez kwot
export default defineFeature({
  pl: {
    riskTitle: 'Ryzyko kary za przestój',
    riskPlannedAfter: 'Dostawa zaplanowana na {planned}, a wolne dni kończą się {deadline} — {n} dni kary. Zaplanuj dostawę najpóźniej na {deadline}.',
    riskUnplannedNear: 'Wolne dni kończą się {deadline} (za {left} dni), a dostawa nie ma terminu — zaplanuj ją teraz.',
    riskUnplannedOver: 'Wolne dni skończyły się {deadline}, a dostawa nie ma terminu — kara już biegnie ({n} dni).',
  },
  en: {
    riskTitle: 'Demurrage risk',
    riskPlannedAfter: 'Delivery planned for {planned}, but free days end on {deadline} — {n} days of demurrage. Plan the delivery for {deadline} at the latest.',
    riskUnplannedNear: 'Free days end on {deadline} (in {left} days) and the delivery has no date — plan it now.',
    riskUnplannedOver: 'Free days ended on {deadline} and the delivery has no date — demurrage is already running ({n} days).',
  },
  pt: {
    riskTitle: 'Risco de sobreestadia',
    riskPlannedAfter: 'Entrega planeada para {planned}, mas os dias livres terminam a {deadline} — {n} dias de sobreestadia. Planeie a entrega até {deadline}.',
    riskUnplannedNear: 'Os dias livres terminam a {deadline} (dentro de {left} dias) e a entrega não tem data — planeie-a já.',
    riskUnplannedOver: 'Os dias livres terminaram a {deadline} e a entrega não tem data — a sobreestadia já está a correr ({n} dias).',
  },
})
