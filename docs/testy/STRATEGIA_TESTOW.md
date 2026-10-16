# Strategia testów

[DEV], 2026-10-16, wersja 0.1. Uzupełnia istniejące: [`E2E.md`](E2E.md) (Playwright, strony bez testów),
[`ETAP-0-PLAN.md`](ETAP-0-PLAN.md) (plan systemu testów regresji, mapa ryzyk R1–R12). Progi: Z-013.

## Zasady

1. **Każde kryterium akceptacji ma test** wskazany w `../analiza/SLEDZENIE.md` — także kryteria
   bezpieczeństwa („rola X dostaje 403”, „obca spółka dostaje 404”). Wymaganie bez testu jest oznaczone wprost.
2. **Nowa trasa API** = wiersz w `tests/permissions.yaml` (rola × metoda) + wpis na liście `PUBLIC`, jeśli
   świadomie publiczna; `test_routes_require_auth.py` i `test_permissions_matrix.py` pilnują.
3. **Nowa reguła procesu** = test w `backend/tests/` + wpis w `docs/REGULY-PROCESU.md` w tym samym PR.
4. **Dane testowe wyłącznie syntetyczne**; fałszywe sekrety w testach oznaczone `gitleaks:allow`.
5. **Nie wyłączamy i nie kwarantannujemy testów**, żeby „przeszło”. Niestabilny test = naprawa przyczyny
   albo historyjka z uzasadnieniem; do czasu naprawy test zostaje czerwony i widoczny.
6. **Pokrycie backendu ≥ 92 % linii** (`pyproject.toml`, tylko w CI) — podnosimy po dopisaniu testów,
   nigdy nie obniżamy. Frontend bez progu liczbowego (Z-013), ale z zasadą 1.

## Piramida — stan 2026-10-16

| Warstwa | Narzędzie | Liczba | Czas | Gdzie biegnie |
|---|---|---|---|---|
| Jednostkowe i integracyjne backendu (API przez `TestClient`, SQLite per worker) | pytest, pytest-xdist | 2112 testów w 348 plikach | 2:17 na 4 rdzeniach | `ci-backend.yml` (PR ruszający backend), lokalnie |
| Jednostkowe i komponentowe frontendu (jsdom, RTL) | vitest | 964 testów w 238 plikach | 3:07 | `ci-frontend.yml`, lokalnie |
| Kontrakt front ↔ API (literały `/api/...` trafiają w trasy) | pytest `test_front_api_paths.py` | 1 | sekundy | oba workflowy |
| Migracje na prawdziwym PostgreSQL 16 + dryf schematu i enumów | alembic, `db_drift.py` | 3 kroki | min. | `ci-migrations.yml` |
| Statyczne: lint, typy (baseline), długość plików, macierz uprawnień, env ↔ docs, lock zależności | ruff, mypy, ESLint, tsc, skrypty | — | sekundy–minuty | CI, pre-commit |
| Bezpieczeństwo: sekrety, SAST, SCA, obraz | gitleaks, Bandit, pip-audit, npm audit, Trivy | — | min. | `security.yml`, `ci-infra.yml` |
| E2E (przeglądarka, 2 role) | Playwright | 16 | min. | **tylko lokalnie** w tym repo (`e2e.yml` jest w repo prywatnym) |
| Wizualne (zrzuty per system) | Playwright | 11 zrzutów | — | lokalnie |

## Rodzaje testów wymagane per typ zmiany

| Zmiana | Minimum |
|---|---|
| Reguła biznesowa (status, limit, odprawa) | test jednostkowy reguły + test API ścieżki szczęśliwej i odmowy |
| Nowa trasa | wiersz w `permissions.yaml`; test 401/403 per rola; test obcej spółki (404) dla tras z `{id}` |
| Zmiana modelu | migracja z `downgrade()`; przebieg `ci-migrations.yml`; test dryfu |
| Upload / import plików | test limitu rozmiaru (413), test złośliwej zawartości (odrzucenie, proces żyje) |
| Ekran lub modal frontendu | test RTL stanów: ładowanie, błąd (4xx i 5xx), sukces; brak fałszywego sukcesu |
| Integracja zewnętrzna | mock odpowiedzi poprawnej i niepoprawnej (nie 500 — US-026) |
| Poprawka bezpieczeństwa z `RYZYKA.md` | test odtwarzający zagrożenie przed poprawką (czerwony) i po (zielony) |

## Luki i plan

| Luka | Działanie |
|---|---|
| E2E nie biegnie w CI tego repozytorium | decyzja PO: dodać `e2e.yml` (koszt minut; wymaga uruchomionej aplikacji w jobie) |
| 21 modułów stron bez testu (`E2E.md`) | US-018: `ImportModal`, `ClearQueueModal`, reset hasła jako pierwsze |
| Brak testów współbieżności | US-003 (`test_concurrency.py`) |
| Testy potwierdzające z `BUGS-FOUND.md` nie powstały | US-001, US-006, US-008 tworzą je |
| Pokrycie tylko liniowe, tylko w CI | wystarczające na teraz; pokrycie gałęzi po przejściu na stabilny tracer |
| Brak testów wydajności | NFR-003: pomiar p95 `/api/containers` na danych demo (US-014) |

## Jak uruchomić lokalnie

```bash
cd backend && python -m pytest tests/ -q -n auto          # całość; pojedyncze pliki na słabszym sprzęcie
cd backend && python -m ruff check . && python scripts/mypy_baseline.py
cd frontend && npm run test && npm run typecheck && npm run lint
python3 scripts/check_file_lengths.py                     # z katalogu głównego
cd frontend && npx playwright install chromium && npm run e2e   # wymaga API na :8000 i panelu na :5173
```

Jeden `pytest` naraz na katalog roboczy (wspólny plik bazy testowej); równoległa praca = osobne `git worktree`.
