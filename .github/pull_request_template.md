<!-- Każdy krok podpisany rolą: [BA] [DEV] [SEC]. PR powstaje jako draft; „Ready for review” = gotowy do
     przeglądów; scala wyłącznie PO. Bez sekretów, danych osobowych i danych produkcyjnych (także na zrzutach). -->

## Co i dlaczego

<1–3 zdania: jaki problem, jaka zmiana. Dla czytelnika z zewnątrz.>

**Historyjka:** US-xxx (`docs/analiza/HISTORYJKI.md`) · **Wymagania:** FR-/NFR-/SR-xxx · **Ryzyka:** R-xx / brak
**Typ:** feat / fix / docs / test / refactor / chore / security

## Jak przetestować

1. …
2. …

**Testy dodane/zmienione:** `…` (każde kryterium akceptacji ma test — `docs/analiza/SLEDZENIE.md` zaktualizowane)

## Zrzuty ekranu (jeśli UI)

<przed / po; dane syntetyczne>

## Checklista [DEV]

- [ ] 1 PR = 1 temat; gałąź od świeżego `main`, `origin/main` wmergowany przed oznaczeniem jako gotowy
- [ ] testy lokalnie zielone: `pytest -n auto`, `ruff`, `mypy_baseline.py`, `npm run test/typecheck/lint`, `check_file_lengths.py`
- [ ] migracja z `upgrade()` i `downgrade()`, jedna głowa (jeśli model)
- [ ] nowa trasa → `tests/permissions.yaml` (+ lista `PUBLIC`, jeśli publiczna); `API.md`, jeśli nowy zasób
- [ ] nowa zmienna env → `config.py`, `.env.example`, `ZMIENNE-SRODOWISKOWE.md`, `RUNBOOK.md`, jeśli wymagana na prod
- [ ] teksty UI w `i18n/features/<funkcja>.ts`; limit 500 linii/plik
- [ ] ADR, jeśli decyzja istotna lub trudno odwracalna
- [ ] `CHANGELOG.md` — wpis w `[Unreleased]`

## Przegląd bezpieczeństwa [SEC]

**Wynik:** ✅ bez uwag / ⚠️ uwagi (poniżej) / ❌ blokada (powód)

- [ ] uwierzytelnianie i sesje bez zmian albo przejrzane
- [ ] autoryzacja: każda trasa ma zależność roli; zasoby przez `get_scoped`/`scope_*`; test obcej spółki (404) i roli bez dostępu (403)
- [ ] walidacja wejścia (Pydantic, limity długości), brak surowego SQL z danymi użytkownika
- [ ] wyjście: autoescape / React; eksporty przez `append_row` / `csv_safe`
- [ ] CSRF: zapisy tylko z `X-Requested-With` albo własnego `Origin`
- [ ] pliki: `read_upload_capped`, weryfikacja typu, nazwa z losowym składnikiem, poza katalogiem publicznym
- [ ] sekrety tylko w env; brak w kodzie, testach (fałszywe z `gitleaks:allow`), logach, zrzutach
- [ ] logi bez haseł, tokenów, danych osobowych; audyt operacji wrażliwych
- [ ] nagłówki bezpieczeństwa nienaruszone (test `test_security_headers.py`)
- [ ] zależności: lock z hashami odświeżony; pip-audit / npm audit czyste
- [ ] klasa danych nowych pól (`KLASYFIKACJA_DANYCH.md`); nowy przepływ → STRIDE w `THREAT_MODEL.md`; RODO: retencja, odbiorcy
- [ ] fałszywe alarmy narzędzi oznaczone z uzasadnieniem (`# nosec <id> — powód`), nie wyciszone hurtowo
- [ ] `RYZYKA.md` zaktualizowany (nowe ryzyko / zamknięte / wyjątek z datą)

**Uwagi [SEC]:** …

## Odbiór [BA]

**Wynik:** ✅ przyjęte / ⚠️ uwagi / ❌ odrzucone

- [ ] każde kryterium akceptacji sprawdzone (lista z numerami)
- [ ] komunikaty i UX zrozumiałe dla roli docelowej; brak fałszywych komunikatów sukcesu
- [ ] `SLEDZENIE.md` zaktualizowana (wymaganie → historyjka → test → ten PR)
- [ ] `REGULY-PROCESU.md`, jeśli zmieniła się reguła; `SLOWNIK.md`, jeśli nowe pojęcie

**Uwagi [BA]:** …

## Ryzyka i decyzje dla PO

<co zostaje otwarte, co wymaga decyzji; „brak”>

## Akceptacja PO

- [ ] PO akceptuje zakres i wynik przeglądów — można scalić
