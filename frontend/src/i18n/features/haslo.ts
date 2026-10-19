// Pole hasła: pokaż / ukryj i miernik siły (PasswordInput.tsx, US-090)
import { defineFeature } from '../feature'

export default defineFeature({
  pl: {
    pwShow: 'Pokaż hasło', pwHide: 'Ukryj hasło', pwStrength: 'Siła hasła',
    pwStrength0: 'za krótkie', pwStrength1: 'słabe', pwStrength2: 'dobre', pwStrength3: 'mocne',
  },
  en: {
    pwShow: 'Show password', pwHide: 'Hide password', pwStrength: 'Password strength',
    pwStrength0: 'too short', pwStrength1: 'weak', pwStrength2: 'good', pwStrength3: 'strong',
  },
  pt: {
    pwShow: 'Mostrar palavra-passe', pwHide: 'Ocultar palavra-passe', pwStrength: 'Força da palavra-passe',
    pwStrength0: 'demasiado curta', pwStrength1: 'fraca', pwStrength2: 'boa', pwStrength3: 'forte',
  },
})
