# Changelog

Format: [Keep a Changelog 1.1.0](https://keepachangelog.com/pl/1.1.0/), wersjonowanie [SemVer](https://semver.org/lang/pl/).
Wersja aplikacji: `0.1.0` (`backend/app/main.py`, `frontend/package.json`); wdrożenia identyfikuje SHA
commita (`APP_VERSION` w `/api/health`). Sekcje: Added · Changed · Deprecated · Removed · Fixed · Security.
Wpis w tym pliku jest częścią Definition of Done (`CONTRIBUTING.md`).

## [Unreleased]

### Added
- Proces zespołowy BA / DEV / SEC z Product Ownerem: `CONTRIBUTING.md` (role, 7 kroków, Definition of
  Ready/Done, konwencje, narzędzia), ADR-0002.
- Szablony issues (`historyjka`, `błąd`, `bezpieczeństwo`) i PR z checklistami BA/DEV/SEC; `CODEOWNERS`;
  `.github/dependabot.yml` (pip, npm, GitHub Actions, Docker — co tydzień).
- `docs/analiza/`: wizja z propozycją mierników, interesariusze, indeks procesów, wymagania 0.1 (FR-001…028,
  NFR-001…013, SR-001…014), backlog MoSCoW (US-001…026) z pilnymi poprawkami bezpieczeństwa na czele, słownik,
  założenia przyjęte bez decyzji PO (Z-001…018), macierz śledzenia.
- `docs/architektura/`: indeks architektury i modelu danych, opis API, ADR-0001 (indeksy zamiast przenoszenia).
- `docs/bezpieczenstwo/`: klasyfikacja danych, model zagrożeń STRIDE 0.1 (13 przepływów), rejestr ryzyk
  (R-01…R-20) i wyjątków (E-01…E-10), RODO 0.1, checklista ASVS L2 (ocena wstępna).
- `docs/testy/STRATEGIA_TESTOW.md`, `docs/operacje/RUNBOOK.md` (wdrożenie, kopie, odtworzenie, incydent,
  rotacja kluczy, wniosek RODO).
- `docs/AUDYT.md` — audyt repozytorium z trzech perspektyw (stan na 2026-10-15), z wynikami narzędzi.

### Changed
- Walidacja konfiguracji przy starcie wydzielona z `backend/app/main.py` do `backend/app/settings_check.py`
  (limit 500 linii); `main` re-eksportuje dotychczasowe nazwy, logi startu nadal pod nazwą `app.main`.
- `SECURITY.md`: poprawione stwierdzenia niezgodne z repozytorium (runnery GitHub zamiast self-hosted,
  brak `automerge.yml`), rozszerzone zgłaszanie podatności, sekcja o polityce i rejestrze ryzyk.
- `README.md`, `docs/README.md`: sekcja procesu zespołowego i mapa nowych dokumentów.

### Security
- **Produkcja odmawia startu, gdy `DATABASE_URL` nie wskazuje PostgreSQL** (US-001, R-04, B-005). Dotąd brak
  zmiennej uruchamiał pustą bazę SQLite w kontenerze, bez kopii. **Przed wdrożeniem:** sprawdź `DATABASE_URL`
  w Coolify (`docker-compose.coolify.yml` i `docker-compose.demo.yml` ustawiają go poprawnie).
- Zidentyfikowane ryzyka bez zmian w kodzie: izolacja spółek tylko w aplikacji (R-01), ciche nadpisanie
  przy równoczesnej edycji (R-02), załączniki weryfikowane po rozszerzeniu (R-03), produkcja bez
  `DATABASE_URL` startuje na SQLite (R-04), jeden sekret do JWT i szyfrowania (R-05). Poprawki w backlogu
  (US-001…US-008) czekają na akceptację PO.

## [0.1.0] - 2026-10-13

Stan początkowy repozytorium publicznego: anonimizowana kopia aplikacji w fazie testów z użytkownikami,
17 PR-ów dokumentacyjnych i demo (README dla rekrutera, instancja demo, wideo). Zakres funkcjonalny:
`docs/01-problem-i-zakres.md`; stan jakości i bezpieczeństwa: `docs/AUDYT.md`.

[Unreleased]: https://github.com/TomaszWu14/container-queue-public/compare/3373194...HEAD
[0.1.0]: https://github.com/TomaszWu14/container-queue-public/commit/3373194
