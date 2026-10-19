import { defineFeature } from '../feature'

// Interaktywny przewodnik po demo (US-081)
export default defineFeature({
  pl: {
    tourStart: 'Przewodnik', tourStartLong: 'Przewodnik krok po kroku (2 min)', tourTitle: 'Przewodnik po demo',
    tourStep: 'Krok {n} z {total}', tourNext: 'Dalej', tourBack: 'Wstecz', tourEnd: 'Zakończ', tourDone: 'Gotowe',
    tour_queue_title: 'Kolejka dostaw', tour_queue_body: 'Każdy wiersz to kontener: status, ETA, dzień dostawy, odprawa i magazyn. Kolumny filtrujesz, widoki zapisujesz — zamiast arkusza Excel wysyłanego mailem.',
    tour_dashboard_title: 'Pulpit', tour_dashboard_body: 'Najważniejsze liczby dnia i ile czasu aplikacja oszczędza (z założeniem minut pokazanym obok wyniku).',
    tour_calendar_title: 'Kalendarz magazynów', tour_calendar_body: 'Rozładunki dzień po dniu z limitem magazynu — przeciążony dzień widać, zanim nastąpi.',
    tour_tracking_title: 'Śledzenie statków', tour_tracking_body: 'Gdzie są statki z kontenerami, opóźnienia z AIS i zatory w portach.',
    tour_automations_title: 'Automatyzacje', tour_automations_body: 'Co aplikacja robi sama: wyzwalacz, akcja, stan i zaoszczędzony czas każdego automatu.',
    tour_simulate_title: 'Symuluj dzień', tour_simulate_body: 'Kliknij „Uruchom symulację”, żeby zobaczyć cały obieg: mail, odczyt numeru, faktura, reguły i zdarzenie dla n8n.',
    tour_built_title: 'Jak to zbudowano', tour_built_body: 'Architektura, metryki projektu i kluczowe decyzje z linkami do dokumentów w repozytorium.',
  },
  en: {
    tourStart: 'Guided tour', tourStartLong: 'Step-by-step tour (2 min)', tourTitle: 'Demo tour',
    tourStep: 'Step {n} of {total}', tourNext: 'Next', tourBack: 'Back', tourEnd: 'End', tourDone: 'Done',
    tour_queue_title: 'Delivery queue', tour_queue_body: 'Each row is a container: status, ETA, delivery day, customs and warehouse. Filter columns and save views — instead of an Excel sheet sent by email.',
    tour_dashboard_title: 'Dashboard', tour_dashboard_body: 'The key numbers of the day and how much time the app saves (with the minutes assumption shown next to the result).',
    tour_calendar_title: 'Warehouse calendar', tour_calendar_body: 'Unloadings day by day against the warehouse limit — an overloaded day is visible before it happens.',
    tour_tracking_title: 'Vessel tracking', tour_tracking_body: 'Where the vessels with containers are, AIS delays and port congestion.',
    tour_automations_title: 'Automations', tour_automations_body: 'What the app does on its own: trigger, action, status and time saved for each automation.',
    tour_simulate_title: 'Simulate a day', tour_simulate_body: 'Press “Run simulation” to see the whole flow: email, number read, invoice, rules and an n8n event.',
    tour_built_title: 'How it was built', tour_built_body: 'Architecture, project metrics and key decisions with links to documents in the repository.',
  },
  pt: {
    tourStart: 'Visita guiada', tourStartLong: 'Visita passo a passo (2 min)', tourTitle: 'Visita à demo',
    tourStep: 'Passo {n} de {total}', tourNext: 'Seguinte', tourBack: 'Anterior', tourEnd: 'Terminar', tourDone: 'Concluído',
    tour_queue_title: 'Fila de entregas', tour_queue_body: 'Cada linha é um contentor: estado, ETA, dia de entrega, desalfandegamento e armazém. Filtre colunas e guarde vistas — em vez de uma folha Excel enviada por email.',
    tour_dashboard_title: 'Painel', tour_dashboard_body: 'Os números principais do dia e quanto tempo a aplicação poupa (com a hipótese de minutos ao lado do resultado).',
    tour_calendar_title: 'Calendário de armazéns', tour_calendar_body: 'Descargas dia a dia face ao limite do armazém — um dia sobrecarregado vê-se antes de acontecer.',
    tour_tracking_title: 'Seguimento de navios', tour_tracking_body: 'Onde estão os navios com contentores, atrasos AIS e congestionamento nos portos.',
    tour_automations_title: 'Automatizações', tour_automations_body: 'O que a aplicação faz sozinha: gatilho, ação, estado e tempo poupado de cada automatização.',
    tour_simulate_title: 'Simular um dia', tour_simulate_body: 'Carregue em “Executar simulação” para ver todo o fluxo: email, leitura do número, fatura, regras e evento n8n.',
    tour_built_title: 'Como foi construído', tour_built_body: 'Arquitetura, métricas do projeto e decisões principais com ligações para documentos no repositório.',
  },
})
