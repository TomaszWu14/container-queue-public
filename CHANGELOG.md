# Changelog

Format: [Keep a Changelog 1.1.0](https://keepachangelog.com/pl/1.1.0/), wersjonowanie [SemVer](https://semver.org/lang/pl/).
Wersja aplikacji: `0.1.0` (`backend/app/main.py`, `frontend/package.json`); wdrożenia identyfikuje SHA
commita (`APP_VERSION` w `/api/health`). Sekcje: Added · Changed · Deprecated · Removed · Fixed · Security.
Wpis w tym pliku jest częścią Definition of Done (`CONTRIBUTING.md`).

## [Unreleased]

### Added
- **„Wyślij plan” w kolejce** (US-017, P-09): zaznaczone kontenery → spedytor dostaje maila z proponowanymi datami
  dostaw i linkiem do zakładki Spedycja, gdzie potwierdza albo zmienia datę. Jeden mail na spedytora i spółkę,
  bez danych dostawcy; brak adresu e-mail lub działającej poczty jest pokazany wprost. Dotąd funkcja nie miała
  przycisku i nie wysyłała maila.
- **Ograniczenia widoków kont demo** (US-029): demo nie zmienia danych także przez pobranie szkicu maila do
  agencji i XML SADUE (dotąd ustawiało status „wysłane” / pisało audyt); ukryte i zablokowane w API: dziennik
  zmian, eksporty i ZIP, wywołania DLT, powiadomienia; profil bez ustawień bezpieczeństwa; goście nie widzą się
  w pasku obecności; pogoda bez zapytań zewnętrznych; zapis odcinany w przeglądarce, przyciski wyszarzone.
- **Demo pokazuje cały proces** (US-027): odprawa zgodna z etapem kontenera (z rewizjami), armatorzy i porty
  docelowe, alerty demurrage, 30 zamówień, dokumenty PDF z celowymi brakami, awizacje we wszystkich stanach.
  Moduł `backend/scripts/seed_demo_process.py`; demo odtwarza też typy dokumentów, które czyszczenie kasowało.
- **Konta demo per rola** (US-028): `demo-spedytor`, `demo-agencja`, `demo-magazyn` — tylko odczyt, każde widzi
  tylko swoje kontenery (`docker-compose.demo.yml`, `README.md`).
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
- `docs/analiza/spec/WYSYLKA-DOKUMENTOW-DO-AGENCJI.md` — specyfikacja wysyłki dokumentów do agencji celnej
  (dwa kanały: powiadomienie i szkic .eml, kryteria AK-01…AK-20 z testami, mini-STRIDE, luki L-1…L-8, pytania do PO).
- `docs/AUDYT.md` — audyt repozytorium z trzech perspektyw (stan na 2026-10-15), z wynikami narzędzi.

### Fixed
- **Zmiana statusu na nieaktualnym widoku nie nadpisuje cudzej zmiany** (US-003, R-02, P-13, ADR-0003). Status
  kontenera, odprawy i zlecenia transportowego: panel wysyła status, który widział; inny w bazie = 409
  `state_changed` z aktualną wartością. Niezwiązane zmiany (notatka, tracking) nie dają konfliktu. Pole
  opcjonalne — importy, n8n i zmiany masowe działają jak dotąd. Formularz kontenera był chroniony już wcześniej.
- **Formularz awizacji nie pokazuje sukcesu, gdy zapis się nie udał** (US-009, P-01). Dotąd każdy błąd 409
  (poza zajętym slotem) w etapie 1, a każdy 409 w etapie 2 (dane kierowców) kończył się ekranem
  „odpowiedź zapisana”. Teraz sukces tylko po 2xx; „już odpowiedziano” ma osobny ekran; każda inna odmowa
  zostawia formularz z powodem z API. Przegrany wyścig dwóch wysyłek zwraca kod `already_submitted`.

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
