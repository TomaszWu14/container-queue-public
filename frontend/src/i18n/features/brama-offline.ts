import { defineFeature } from '../feature'

// Brama bez zasięgu (US-085)
export default defineFeature({
  pl: {
    gateOfflineBanner: 'Brak połączenia — lista z {time}. „Przyjechał” zapisze się sam po powrocie sieci; spóźnienie i etap rampy wymagają połączenia.',
    gateOfflineQueued: 'Brak sieci — zapisane w telefonie, wyślę po powrocie połączenia.',
    gateOfflineWaiting: 'Czeka na wysłanie: {n}.', gateOfflinePendingBadge: 'czeka na sieć',
    gateOfflineSent: 'Wysłano zaległe przyjazdy: {n}.', gateOfflineFailed: 'Nie udało się zapisać {n} przyjazdu(ów) — sprawdź listę.',
  },
  en: {
    gateOfflineBanner: 'No connection — list from {time}. “Arrived” is saved automatically when the network is back; delays and ramp stage need a connection.',
    gateOfflineQueued: 'No network — saved on this device, will be sent when the connection is back.',
    gateOfflineWaiting: 'Waiting to be sent: {n}.', gateOfflinePendingBadge: 'waiting for network',
    gateOfflineSent: 'Queued arrivals sent: {n}.', gateOfflineFailed: 'Could not save {n} arrival(s) — check the list.',
  },
  pt: {
    gateOfflineBanner: 'Sem ligação — lista das {time}. “Chegou” é gravado automaticamente quando a rede voltar; atrasos e fase da rampa precisam de ligação.',
    gateOfflineQueued: 'Sem rede — guardado neste dispositivo, será enviado quando a ligação voltar.',
    gateOfflineWaiting: 'À espera de envio: {n}.', gateOfflinePendingBadge: 'à espera de rede',
    gateOfflineSent: 'Chegadas pendentes enviadas: {n}.', gateOfflineFailed: 'Não foi possível gravar {n} chegada(s) — verifique a lista.',
  },
})
