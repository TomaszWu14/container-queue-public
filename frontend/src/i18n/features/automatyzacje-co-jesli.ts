import { defineFeature } from '../feature'

// Symulacja „co jeśli statek się spóźni” (druga lista PO, pkt 10).
export default defineFeature({
  pl: {
    whatIfTitle: 'Co jeśli statek się spóźni?',
    whatIfIntro: 'Wybierz statek i liczbę dni opóźnienia. Przesuniemy awizacje jego kontenerów i pokażemy, w które dni magazyn przekroczy dzienny limit rozładunków.',
    whatIfNoVessels: 'Brak statków z zaplanowanymi awizacjami.',
    whatIfVessel: 'Statek', whatIfDelay: 'Opóźnienie (dni)', whatIfRun: 'Policz', whatIfRunning: 'Liczę…',
    whatIfSummary: 'Statek {vessel} spóźniony o {d} dni: przesuniętych kontenerów {n}, nowe przekroczenia limitu {add}, znikające przekroczenia {fix}.',
    whatIfNoChange: 'Obciążenie magazynów się nie zmienia.',
    whatIfColDay: 'Dzień', whatIfColWarehouse: 'Magazyn', whatIfColBefore: 'Teraz', whatIfColAfter: 'Po opóźnieniu',
    whatIfColLimit: 'Limit', whatIfOver: 'ponad limit', whatIfMoved: 'Przesunięte kontenery ({n})',
    whatIfNoWrite: 'Tylko symulacja — plan awizacji zostaje bez zmian.',
  },
  en: {
    whatIfTitle: 'What if a vessel is late?',
    whatIfIntro: 'Pick a vessel and the delay in days. We shift the delivery dates of its containers and show the days on which a warehouse goes over its daily unloading limit.',
    whatIfNoVessels: 'No vessels with planned deliveries.',
    whatIfVessel: 'Vessel', whatIfDelay: 'Delay (days)', whatIfRun: 'Calculate', whatIfRunning: 'Calculating…',
    whatIfSummary: 'Vessel {vessel} late by {d} days: containers moved {n}, new limit overruns {add}, overruns removed {fix}.',
    whatIfNoChange: 'Warehouse load does not change.',
    whatIfColDay: 'Day', whatIfColWarehouse: 'Warehouse', whatIfColBefore: 'Now', whatIfColAfter: 'After delay',
    whatIfColLimit: 'Limit', whatIfOver: 'over limit', whatIfMoved: 'Moved containers ({n})',
    whatIfNoWrite: 'Simulation only — the delivery plan stays unchanged.',
  },
  pt: {
    whatIfTitle: 'E se o navio atrasar?',
    whatIfIntro: 'Escolha um navio e o atraso em dias. Deslocamos as datas de entrega dos seus contentores e mostramos os dias em que um armazém ultrapassa o limite diário de descargas.',
    whatIfNoVessels: 'Sem navios com entregas planeadas.',
    whatIfVessel: 'Navio', whatIfDelay: 'Atraso (dias)', whatIfRun: 'Calcular', whatIfRunning: 'A calcular…',
    whatIfSummary: 'Navio {vessel} atrasado {d} dias: contentores deslocados {n}, novos excessos de limite {add}, excessos eliminados {fix}.',
    whatIfNoChange: 'A carga dos armazéns não muda.',
    whatIfColDay: 'Dia', whatIfColWarehouse: 'Armazém', whatIfColBefore: 'Agora', whatIfColAfter: 'Após atraso',
    whatIfColLimit: 'Limite', whatIfOver: 'acima do limite', whatIfMoved: 'Contentores deslocados ({n})',
    whatIfNoWrite: 'Apenas simulação — o plano de entregas não muda.',
  },
})
