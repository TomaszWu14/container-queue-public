# Jak pracujemy w tym repozytorium

Repozytorium jest prowadzone jak przez **trzyosobowy zespół** — analityk biznesowy **[BA]**, developer
**[DEV]**, specjalista bezpieczeństwa **[SEC]** — z **Product Ownerem (PO)**, który decyduje o zakresie,
priorytetach, ryzykach i wydaniach. Każda zmiana przechodzi przez trzy perspektywy, a ślad tej pracy jest
w repozytorium: dokumenty, issues, commity, PR-y. Decyzja o takim procesie: `docs/architektura/adr/0002-proces-zespolowy-ba-dev-sec.md`.

Reguły techniczne repozytorium (limit 500 linii, i18n per funkcja, unikanie konfliktów) są w [`CLAUDE.md`](CLAUDE.md)
i obowiązują każdego — człowieka i agenta. Onboarding środowiska: [`docs/ONBOARDING-DEV.md`](docs/ONBOARDING-DEV.md).

## Role

| Rola | Robi | Nie robi |
|---|---|---|
| **[BA]** | pyta PO, pisze historyjki z kryteriami Dane/Gdy/Wtedy, NFR, słownik, priorytety MoSCoW, macierz śledzenia, odbiór z perspektywy użytkownika | **nie pisze kodu**; nie zgaduje — gdy PO milczy, zapisuje bezpieczne minimum w `docs/analiza/ZALOZENIA.md` |
| **[DEV]** | projekt (ADR), model danych i API przed kodem, implementacja w małych krokach, testy per kryterium, środowisko, README/API/CHANGELOG | **nie zmienia zakresu** bez BA/PO; nie wyłącza testów ani kontroli bezpieczeństwa |
| **[SEC]** | klasa danych i mini-STRIDE przed kodem, przegląd PR wg OWASP/ASVS, narzędzia, `SECURITY.md`, rejestr ryzyk i wyjątków | nie obniża wymagań — eskaluje do PO; **ma prawo weta** przy ryzyku wysokim/krytycznym |
| **PO** | odpowiada na pytania, akceptuje zakres, priorytety, ryzyka, wydania; **tylko PO scala PR** | — |

W PR i w komentarzach każdy krok jest podpisany rolą. Gdy role mają sprzeczne rekomendacje, obie opcje
z konsekwencjami idą do PO; decyzja ląduje w ADR albo w rejestrze ryzyk.

## Proces dla każdej funkcji (nie przeskakujemy kroków)

| Krok | Rola | Wynik |
|---|---|---|
| 1. Analiza | [BA] | pytania do PO (max 5 naraz) → historyjka w `docs/analiza/HISTORYJKI.md` (Jako/chcę/aby, kryteria Dane/Gdy/Wtedy, NFR, priorytet) → Definition of Ready |
| 2. Wymagania bezpieczeństwa | [SEC] | klasa danych (`KLASYFIKACJA_DANYCH.md`), mini-STRIDE dla nowego przepływu (`THREAT_MODEL.md`), kryteria bezpieczeństwa dopisane do historyjki, wpis w `RYZYKA.md`, jeśli coś zostaje otwarte |
| 3. Projekt | [DEV] | krótki opis rozwiązania; ADR w `docs/architektura/adr/`, gdy decyzja istotna lub trudno odwracalna; zmiany modelu i API najpierw w `MODEL_DANYCH.md` / `API.md` |
| 4. Implementacja | [DEV] | gałąź `feature/<US-id>-<nazwa>`, małe commity Conventional Commits z ID historyjki, test na każde kryterium (także „rola X dostaje 403”) |
| 5. Przegląd bezpieczeństwa | [SEC] | checklista z szablonu PR; wynik ✅ / ⚠️ uwagi / ❌ blokada z uzasadnieniem; narzędzia uruchomione, fałszywe alarmy oznaczone z powodem (nie wyciszone hurtowo) |
| 6. Odbiór | [BA] | kryteria sprawdzone punkt po punkcie, komunikaty i UX, aktualizacja `SLEDZENIE.md` |
| 7. PR i podsumowanie | wszyscy | opis wg szablonu, wpis w `CHANGELOG.md`, **merge tylko po akceptacji PO** |

Po każdym etapie: podsumowanie 5–8 punktów z podziałem na role + lista decyzji potrzebnych od PO.

## Definition of Ready

Historyjka jest gotowa do realizacji, gdy: cel jest jasny · kryteria akceptacji są testowalne (Dane/Gdy/Wtedy)
· zależności są znane · dane i uprawnienia są określone · [SEC] podał klasę danych i kryteria bezpieczeństwa
· PO nadał priorytet.

## Definition of Done

Funkcja jest skończona, gdy:

- wszystkie kryteria akceptacji (funkcjonalne i bezpieczeństwa) są spełnione i **pokryte testami**,
- CI jest zielone: lint, typy, testy, skany bezpieczeństwa bez nowych ustaleń wysokich/krytycznych,
- dokumentacja zaktualizowana: wymagania (`WYMAGANIA.md`/`05`), API, model danych, ADR (jeśli dotyczy),
  `REGULY-PROCESU.md` (jeśli reguła), macierz `SLEDZENIE.md`, `CHANGELOG.md`,
- przegląd [SEC] i odbiór [BA] zapisane w PR,
- brak sekretów, danych osobowych i danych produkcyjnych w repo, testach i logach,
- **PO zaakceptował**.

## Konwencje

- **Język:** dokumentacja po polsku; kod, nazwy, komunikaty commitów po angielsku (Z-011).
- **Commity:** Conventional Commits — `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`, `security:`;
  w treści ID historyjki, np. `fix: reject production start without PostgreSQL (US-001)`.
- **Gałęzie:** `feature/<US-id>-<krótka-nazwa>` od świeżego `main`; sesje agentów w chmurze na gałęziach
  wyznaczonych przez narzędzie (`claude/...`). **1 PR = 1 temat**, mały, szybko scalany.
- **Przed pushem i przed oznaczeniem PR jako gotowy:** `git fetch origin main && git merge origin/main`
  (merge, nie rebase), testy, push. Nie przenosimy ani nie formatujemy masowo kodu, którego nie zmieniamy.
- **PR:** powstaje jako **draft** (CI w tym repo pomija drafty — oszczędność minut); gotowy do przeglądu =
  „Ready for review”; scala wyłącznie PO. Szablon: `.github/pull_request_template.md`.
- **Issues:** szablony `.github/ISSUE_TEMPLATE/` (historyjka, błąd, bezpieczeństwo). Podatności — **nie**
  przez publiczne issue (`SECURITY.md`).
- **Teksty UI:** nowe klucze w `frontend/src/i18n/features/<funkcja>.ts` (`CLAUDE.md`).
- **Limit 500 linii/plik** (`scripts/check_file_lengths.py`); pliki z `BASELINE` mogą się tylko skracać.
- **Migracje:** `python -m alembic revision --autogenerate -m "opis"`, działający `upgrade()` i `downgrade()`,
  jedna głowa; CI sprawdza na PostgreSQL 16.
- **Wersjonowanie:** SemVer w `CHANGELOG.md` (Keep a Changelog); wdrożenia identyfikowane SHA (`APP_VERSION`).

## Co dopisać przy jakiej zmianie

| Zmiana | Artefakty obowiązkowe |
|---|---|
| nowa funkcja / zmiana zachowania | historyjka, kryteria SEC, test per kryterium, `SLEDZENIE.md`, `CHANGELOG.md`; `REGULY-PROCESU.md`, jeśli reguła |
| nowa trasa API | wiersz w `tests/permissions.yaml`; lista `PUBLIC`, jeśli publiczna; `API.md`, jeśli nowy zasób |
| zmiana modelu | migracja z `downgrade()`; ERD w `04`, jeśli rdzeń; klasa danych nowych kolumn (`KLASYFIKACJA_DANYCH.md`) |
| nowa zmienna środowiskowa | `config.py`, `.env.example`, `docs/ZMIENNE-SRODOWISKOWE.md` (testy pilnują), `RUNBOOK.md`, jeśli wymagana na prod |
| nowa integracja / przepływ danych | tabela STRIDE w `THREAT_MODEL.md`, odbiorca w `RODO.md` §6, wpis w `RYZYKA.md` |
| decyzja istotna lub trudno odwracalna | ADR w `docs/architektura/adr/` |
| akceptacja ryzyka przez PO | `RYZYKA.md` (wyjątek E-xx z datą przeglądu) |
| założenie przyjęte bez PO | `docs/analiza/ZALOZENIA.md` |

## Narzędzia i uruchamianie lokalne

Dobór: darmowe, open-source, już w repozytorium; uzasadnienie w tabeli (szczegóły: `backend/pyproject.toml`,
`frontend/eslint.config.js`, `.github/workflows/`).

| Narzędzie | Po co | Lokalnie | W CI |
|---|---|---|---|
| **ruff** | lint + modernizacja Pythona (`E F W I B UP BLE C90 PIE`, złożoność ≤ 20) | `cd backend && python -m ruff check .` | `ci-backend.yml`, pre-commit |
| **mypy** (baseline) | typy; znane błędy w `mypy-baseline.txt` mogą tylko maleć | `python scripts/mypy_baseline.py` | `ci-backend.yml` |
| **pytest + pytest-cov + xdist** | testy backendu; pokrycie ≥ 92 % linii | `python -m pytest tests/ -q -n auto` | `ci-backend.yml` |
| **ESLint + typescript-eslint + react-hooks** | błędy i reguły hooków w panelu | `cd frontend && npm run lint:setup && npm run lint` | `ci-frontend.yml` |
| **TypeScript (tsc)**, **vitest**, **vite build** | typy, testy, build panelu | `npm run typecheck && npm run test && npm run build` | `ci-frontend.yml` |
| **check_file_lengths.py** | limit 500 linii/plik | `python3 scripts/check_file_lengths.py` | oba workflowy |
| **Alembic + db_drift** | migracje od zera na PostgreSQL 16, zero dryfu | `python -m alembic upgrade head`, `python scripts/db_drift.py` | `ci-migrations.yml` |
| **Bandit** (SAST) | podatności w kodzie Pythona | `bandit -r app -c pyproject.toml` | `security.yml` (bramka) |
| **gitleaks** (sekrety) | sekrety w commitach i historii | `gitleaks git --redact .` | `security.yml` (bramka), pre-commit |
| **pip-audit**, **npm audit** (SCA) | znane podatności zależności | `pip-audit -r requirements.txt`, `npm audit --audit-level=high` | `ci-infra.yml` (bramka przy zmianie zależności) |
| **Trivy** (fs + obraz) + SBOM | podatności plików, obrazu, błędy konfiguracji | `trivy fs --severity HIGH,CRITICAL .` | `security.yml` co tydzień (raport; bramka — US-007) |
| **Dependabot** | aktualizacje pip, npm, akcji, obrazów co tydzień | — | `.github/dependabot.yml` |
| **pre-commit** | ruff, Bandit, gitleaks, końce linii, duże pliki, klucze prywatne | `pip install pre-commit && pre-commit install` | — |
| **Playwright** (E2E, wizualne) | ścieżki krytyczne w przeglądarce | `npm run e2e` (API :8000, panel :5173) | tylko repo prywatne (`docs/testy/E2E.md`) |

Planowane (US-007): Semgrep z regułami OWASP, Trivy jako bramka, wyrównanie wersji pre-commit z CI.

Lock zależności backendu ma hashe (`uv pip compile --generate-hashes`); po zmianie `requirements*.in` albo
po PR Dependabota, który zepsuł `test_dependency_lock.py`, odśwież lock komendą z nagłówka `requirements.in`.

## Zgłoszenia i kontakt

Błędy i propozycje — issues z szablonu. Podatności — prywatnie wg `SECURITY.md`. Decyzje PO — w PR albo issue,
zapisane potem w ADR / rejestrze ryzyk / `ZALOZENIA.md`.
