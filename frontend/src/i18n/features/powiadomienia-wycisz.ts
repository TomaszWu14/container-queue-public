import { defineFeature } from '../feature'

// Wyciszenie alertów kontenera z dzwonka (trzecia lista PO, pkt 3).
export default defineFeature({
  pl: {
    muteAction: 'Nie przypominaj', muteHint: 'Wycisz automatyczne alerty o tym kontenerze tylko dla siebie',
    muteFor: 'Wycisz na:', muteDays1: '1 dzień', muteDays3: '3 dni', muteDays7: '7 dni',
    muteUntil: 'Wyciszone do {d}', muteUndo: 'Cofnij',
  },
  en: {
    muteAction: "Don't remind me", muteHint: 'Mute automatic alerts about this container for yourself only',
    muteFor: 'Mute for:', muteDays1: '1 day', muteDays3: '3 days', muteDays7: '7 days',
    muteUntil: 'Muted until {d}', muteUndo: 'Undo',
  },
  pt: {
    muteAction: 'Não lembrar', muteHint: 'Silenciar alertas automáticos deste contentor só para si',
    muteFor: 'Silenciar por:', muteDays1: '1 dia', muteDays3: '3 dias', muteDays7: '7 dias',
    muteUntil: 'Silenciado até {d}', muteUndo: 'Desfazer',
  },
})
