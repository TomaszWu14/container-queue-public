// Powiadomienia push na tym urządzeniu (PushSection.tsx, US-086)
import { defineFeature } from '../feature'

export default defineFeature({
  pl: {
    pushTitle: 'Powiadomienia push', pushTurnOn: 'Włącz na tym urządzeniu', pushTurnOff: 'Wyłącz na tym urządzeniu',
    pushIntro: 'Najpilniejsze alerty (demurrage, spóźnione ETA, brama, wzmianki, pilne palety, akceptacja frachtu) jako powiadomienie na telefonie lub komputerze — także gdy aplikacja jest zamknięta.',
    pushServerOff: 'Powiadomienia push nie są jeszcze włączone na serwerze — poproś administratora.',
    pushUnsupported: 'Ta przeglądarka nie obsługuje powiadomień push. Na iPhonie dodaj aplikację do ekranu głównego.',
    pushDenied: 'Przeglądarka nie dała zgody na powiadomienia — zmień to w ustawieniach strony.',
    pushOnHere: 'Włączone na tym urządzeniu', pushTest: 'Wyślij próbne',
    pushTestSent: 'Wysłano na {sent} z {devices} urządzeń.', pushDevices: 'Twoje urządzenia z push: {n}.',
  },
  en: {
    pushTitle: 'Push notifications', pushTurnOn: 'Turn on for this device', pushTurnOff: 'Turn off for this device',
    pushIntro: 'The most urgent alerts (demurrage, overdue ETA, gate, mentions, urgent pallets, freight approval) as a notification on your phone or computer — even when the app is closed.',
    pushServerOff: 'Push notifications are not enabled on the server yet — ask your administrator.',
    pushUnsupported: 'This browser does not support push notifications. On iPhone, add the app to your home screen.',
    pushDenied: 'The browser did not allow notifications — change it in the site settings.',
    pushOnHere: 'On for this device', pushTest: 'Send a test',
    pushTestSent: 'Sent to {sent} of {devices} devices.', pushDevices: 'Your devices with push: {n}.',
  },
  pt: {
    pushTitle: 'Notificações push', pushTurnOn: 'Ativar neste dispositivo', pushTurnOff: 'Desativar neste dispositivo',
    pushIntro: 'Os alertas mais urgentes (demurrage, ETA em atraso, portaria, menções, paletes urgentes, aprovação de frete) como notificação no telemóvel ou computador — mesmo com a aplicação fechada.',
    pushServerOff: 'As notificações push ainda não estão ativas no servidor — fale com o administrador.',
    pushUnsupported: 'Este navegador não suporta notificações push. No iPhone, adicione a aplicação ao ecrã principal.',
    pushDenied: 'O navegador não permitiu notificações — altere nas definições do site.',
    pushOnHere: 'Ativo neste dispositivo', pushTest: 'Enviar teste',
    pushTestSent: 'Enviado para {sent} de {devices} dispositivos.', pushDevices: 'Os seus dispositivos com push: {n}.',
  },
})
