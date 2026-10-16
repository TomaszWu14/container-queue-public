import { defineFeature } from '../feature'

// Brama: skanowanie kodu QR z karty rozładunku telefonem albo wpisanie numeru → wpuszczenie auta
export default defineFeature({
  pl: {
    gateScanBtn: 'Skanuj kod QR',
    gateScanStop: 'Zamknij aparat',
    gateScanHint: 'Skieruj aparat na kod QR z karty rozładunku.',
    gateScanNoCamera: 'Ten telefon lub przeglądarka nie odczyta kodu w aplikacji. Zeskanuj kod zwykłym aparatem albo wpisz numer kontenera.',
    gateScanDenied: 'Brak zgody na aparat. Zezwól na aparat w przeglądarce albo wpisz numer kontenera.',
    gateScanInput: 'Numer kontenera',
    gateScanFind: 'Szukaj',
    gateScanNotToday: 'Tego kontenera nie ma na dzisiejszej liście bramy — nie wpuszczaj bez sprawdzenia z logistyką.',
    gateScanAlready: 'Już wpuszczony o {time}.',
    gateScanLetIn: 'Przyjechał — wpuść',
  },
  en: {
    gateScanBtn: 'Scan QR code',
    gateScanStop: 'Close camera',
    gateScanHint: 'Point the camera at the QR code on the unloading card.',
    gateScanNoCamera: 'This phone or browser cannot read the code in the app. Scan it with the regular camera or type the container number.',
    gateScanDenied: 'No camera permission. Allow the camera in the browser or type the container number.',
    gateScanInput: 'Container number',
    gateScanFind: 'Find',
    gateScanNotToday: 'This container is not on today’s gate list — do not let it in without checking with logistics.',
    gateScanAlready: 'Already let in at {time}.',
    gateScanLetIn: 'Arrived — let in',
  },
  pt: {
    gateScanBtn: 'Ler código QR',
    gateScanStop: 'Fechar câmara',
    gateScanHint: 'Aponte a câmara para o código QR do cartão de descarga.',
    gateScanNoCamera: 'Este telemóvel ou navegador não lê o código na aplicação. Leia-o com a câmara normal ou escreva o número do contentor.',
    gateScanDenied: 'Sem permissão para a câmara. Permita a câmara no navegador ou escreva o número do contentor.',
    gateScanInput: 'Número do contentor',
    gateScanFind: 'Procurar',
    gateScanNotToday: 'Este contentor não está na lista de hoje da portaria — não deixe entrar sem confirmar com a logística.',
    gateScanAlready: 'Já entrou às {time}.',
    gateScanLetIn: 'Chegou — deixar entrar',
  },
})
