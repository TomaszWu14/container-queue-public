import { defineFeature } from '../feature'

// Przebieg procesu z historii statusów (US-038): czas w etapach, cofnięcia, kontenery utknięte.
export default defineFeature({
  pl: {
    procTitle: 'Przebieg procesu: gdzie kontenery stoją najdłużej', procIntro: 'Wyliczone z historii zmian statusu — bez ręcznego raportowania. Mediana to typowy czas w etapie, 90. percentyl to granica „dłużej niż zwykle”: kontener, który ją przekroczył, trafia na listę do sprawdzenia.',
    procTransitions: 'Zmian statusu · {days} dni', procBackward: 'Cofnięć statusu ({n}) — poprawki w procesie', procStuckKpi: 'Kontenerów dłużej niż zwykle',
    procStages: 'Czas w etapie', procColStage: 'Etap', procColCount: 'Przejść', procColMedian: 'Mediana', procColP90: '90. percentyl',
    procDays: '{n} dni', procLegend: 'Ciemny pasek — mediana, jasny — 90. percentyl.',
    procTop: 'Najczęstsze przejścia', procStuckTitle: 'Do sprawdzenia: dłużej niż zwykle w obecnym etapie',
    procColContainer: 'Kontener', procColInStage: 'W etapie',
    procStuckNone: 'Brak — albo etap ma mniej niż {n} zakończonych pobytów (za mało, by ocenić „zwykle”).',
    procEmpty: 'Brak zmian statusu w tym okresie.',
    procFlowTitle: 'Przepływ między etapami', procFlowForward: 'Przejście w przód', procFlowBack: 'Cofnięcie statusu',
  },
  en: {
    procTitle: 'Process flow: where containers wait longest', procIntro: 'Calculated from the status change history — no manual reporting. The median is the typical time in a stage, the 90th percentile is the “longer than usual” line: a container past it goes on the list to check.',
    procTransitions: 'Status changes · {days} days', procBackward: 'Status rollbacks ({n}) — rework in the process', procStuckKpi: 'Containers longer than usual',
    procStages: 'Time in stage', procColStage: 'Stage', procColCount: 'Transitions', procColMedian: 'Median', procColP90: '90th percentile',
    procDays: '{n} days', procLegend: 'Dark bar — median, light — 90th percentile.',
    procTop: 'Most frequent transitions', procStuckTitle: 'To check: longer than usual in the current stage',
    procColContainer: 'Container', procColInStage: 'In stage',
    procStuckNone: 'None — or the stage has fewer than {n} completed stays (too few to judge “usual”).',
    procEmpty: 'No status changes in this period.',
    procFlowTitle: 'Flow between stages', procFlowForward: 'Forward transition', procFlowBack: 'Status rollback',
  },
  pt: {
    procTitle: 'Fluxo do processo: onde os contentores esperam mais', procIntro: 'Calculado a partir do histórico de mudanças de estado — sem relatórios manuais. A mediana é o tempo típico numa etapa, o percentil 90 é a linha de “mais do que o habitual”: um contentor que a ultrapassa entra na lista a verificar.',
    procTransitions: 'Mudanças de estado · {days} dias', procBackward: 'Retrocessos de estado ({n}) — retrabalho no processo', procStuckKpi: 'Contentores acima do habitual',
    procStages: 'Tempo na etapa', procColStage: 'Etapa', procColCount: 'Transições', procColMedian: 'Mediana', procColP90: 'Percentil 90',
    procDays: '{n} dias', procLegend: 'Barra escura — mediana, clara — percentil 90.',
    procTop: 'Transições mais frequentes', procStuckTitle: 'A verificar: acima do habitual na etapa atual',
    procColContainer: 'Contentor', procColInStage: 'Na etapa',
    procStuckNone: 'Nenhum — ou a etapa tem menos de {n} estadias concluídas (poucas para avaliar o “habitual”).',
    procEmpty: 'Sem mudanças de estado neste período.',
    procFlowTitle: 'Fluxo entre etapas', procFlowForward: 'Transição para a frente', procFlowBack: 'Retrocesso de estado',
  },
})
