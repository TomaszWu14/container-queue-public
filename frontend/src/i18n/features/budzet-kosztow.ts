import { defineFeature } from '../feature'

// Budżet kosztów transportu i portu (US-084)
export default defineFeature({
  pl: {
    budgetTitle: 'Budżet kosztów transportu',
    budgetIntro: 'Faktury transportowe (B/L) z bieżącego miesiąca w EUR (inne waluty kursem NBP), bez odrzuconych. Dzień {day} z {days}: prognoza = tempo dotychczasowe × cały miesiąc. Ostrzeżenie, gdy prognoza przekroczy {pct}% budżetu.',
    budgetColCompany: 'Spółka', budgetColBudget: 'Budżet / mies.', budgetColSpent: 'Wydane', budgetColForecast: 'Prognoza na koniec miesiąca',
    budgetColState: 'Stan', budgetSave: 'Zapisz', budgetUnconverted: '{n} faktur(y) bez kursu NBP — pominięte',
    budgetState_none: 'brak budżetu', budgetState_ok: 'w budżecie', budgetState_warn: 'uwaga — prognoza blisko budżetu', budgetState_over: 'budżet przekroczony',
  },
  en: {
    budgetTitle: 'Transport cost budget',
    budgetIntro: 'Transport invoices (B/L) of the current month in EUR (other currencies at NBP rates), excluding rejected ones. Day {day} of {days}: forecast = pace so far × whole month. Warning when the forecast exceeds {pct}% of the budget.',
    budgetColCompany: 'Company', budgetColBudget: 'Budget / month', budgetColSpent: 'Spent', budgetColForecast: 'Month-end forecast',
    budgetColState: 'Status', budgetSave: 'Save', budgetUnconverted: '{n} invoice(s) without an NBP rate — skipped',
    budgetState_none: 'no budget', budgetState_ok: 'within budget', budgetState_warn: 'warning — forecast close to budget', budgetState_over: 'budget exceeded',
  },
  pt: {
    budgetTitle: 'Orçamento de custos de transporte',
    budgetIntro: 'Faturas de transporte (B/L) do mês corrente em EUR (outras moedas à taxa do NBP), sem as rejeitadas. Dia {day} de {days}: previsão = ritmo até agora × mês inteiro. Aviso quando a previsão ultrapassa {pct}% do orçamento.',
    budgetColCompany: 'Empresa', budgetColBudget: 'Orçamento / mês', budgetColSpent: 'Gasto', budgetColForecast: 'Previsão no fim do mês',
    budgetColState: 'Estado', budgetSave: 'Guardar', budgetUnconverted: '{n} fatura(s) sem taxa NBP — ignoradas',
    budgetState_none: 'sem orçamento', budgetState_ok: 'dentro do orçamento', budgetState_warn: 'atenção — previsão perto do orçamento', budgetState_over: 'orçamento ultrapassado',
  },
})
