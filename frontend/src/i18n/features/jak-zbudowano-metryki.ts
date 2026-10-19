import { defineFeature } from '../feature'

// Metryki projektu na stronie „Jak to zbudowano” (US-080)
export default defineFeature({
  pl: {
    pmTitle: 'Metryki projektu',
    pmIntro: 'Policzone z repozytorium skryptem scripts/project_metrics.py, stan na {date}. Testy liczone jako funkcje testowe (warianty parametryzowane uruchamiają się wielokrotnie).',
    pmBackendTests: 'testów backendu (pytest)', pmFrontendTests: 'testów frontendu (vitest)',
    pmE2eTests: 'scenariuszy w przeglądarce (Playwright)', pmApiOps: 'operacji API z opisaną rolą',
    pmStories: 'historyjek wdrożonych', pmAdrs: 'zapisanych decyzji architektonicznych (ADR)',
    pmPrs: 'pull requestów (numer ostatniego)',
  },
  en: {
    pmTitle: 'Project metrics',
    pmIntro: 'Counted from the repository by scripts/project_metrics.py, as of {date}. Tests are counted as test functions (parametrised variants run several times).',
    pmBackendTests: 'backend tests (pytest)', pmFrontendTests: 'frontend tests (vitest)',
    pmE2eTests: 'browser scenarios (Playwright)', pmApiOps: 'API operations with documented roles',
    pmStories: 'user stories shipped', pmAdrs: 'architecture decision records (ADR)',
    pmPrs: 'pull requests (latest number)',
  },
  pt: {
    pmTitle: 'Métricas do projeto',
    pmIntro: 'Contadas a partir do repositório por scripts/project_metrics.py, em {date}. Os testes são contados como funções de teste (variantes parametrizadas correm várias vezes).',
    pmBackendTests: 'testes de backend (pytest)', pmFrontendTests: 'testes de frontend (vitest)',
    pmE2eTests: 'cenários no navegador (Playwright)', pmApiOps: 'operações de API com papéis documentados',
    pmStories: 'histórias entregues', pmAdrs: 'decisões de arquitetura registadas (ADR)',
    pmPrs: 'pull requests (último número)',
  },
})
