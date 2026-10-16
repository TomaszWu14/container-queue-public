// US-009 (P-01): formularz awizacji, na który już odpowiedziano — osobny ekran, nie ekran sukcesu
import { defineFeature } from '../feature'

export default defineFeature({
  pl: {
    avAlreadyTitle: 'Na tę awizację już odpowiedziano',
    avAlreadyInfo: 'Odpowiedź wysłano wcześniej. Jeśli przed chwilą wysyłali Państwo formularz ponownie, ' +
      'te zmiany nie zostały zapisane — prosimy o kontakt z działem logistyki.',
  },
  en: {
    avAlreadyTitle: 'This notice has already been answered',
    avAlreadyInfo: 'A reply was sent earlier. If you just submitted the form again, those changes were ' +
      'not saved — please contact the logistics team.',
  },
  pt: {
    avAlreadyTitle: 'Este aviso já foi respondido',
    avAlreadyInfo: 'A resposta foi enviada anteriormente. Se acabou de reenviar o formulário, essas ' +
      'alterações não foram guardadas — contacte a equipa de logística.',
  },
})
