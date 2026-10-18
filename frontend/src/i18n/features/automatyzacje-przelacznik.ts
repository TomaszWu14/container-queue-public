import { defineFeature } from '../feature'

// Włącz / wyłącz automat z ekranu Automatyzacje (druga lista PO, pkt 6) — tylko admin.
export default defineFeature({
  pl: {
    autoSwitchOff: 'Wyłącz', autoSwitchOn: 'Włącz',
    autoSwitchedOffHint: 'Wyłączony przez administratora na tym ekranie — zmiana zapisana w historii zmian.',
  },
  en: {
    autoSwitchOff: 'Turn off', autoSwitchOn: 'Turn on',
    autoSwitchedOffHint: 'Turned off by an administrator on this screen — the change is in the change log.',
  },
  pt: {
    autoSwitchOff: 'Desligar', autoSwitchOn: 'Ligar',
    autoSwitchedOffHint: 'Desligada por um administrador neste ecrã — a alteração está no histórico.',
  },
})
