# Changelog

Format: [Keep a Changelog 1.1.0](https://keepachangelog.com/pl/1.1.0/), wersjonowanie [SemVer](https://semver.org/lang/pl/).
Wersja aplikacji: `0.1.0` (`backend/app/main.py`, `frontend/package.json`); wdrożenia identyfikuje SHA
commita (`APP_VERSION` w `/api/health`). Sekcje: Added · Changed · Deprecated · Removed · Fixed · Security.
Wpis w tym pliku jest częścią Definition of Done (`CONTRIBUTING.md`).

## [Unreleased]

### Added
- **Ekran „Automatyzacje”** (US-032, US-033): katalog wszystkiego, co aplikacja robi sama — 20 automatów
  z harmonogramu i 3 obiegi z n8n, każdy z wyzwalaczem, akcją, stanem (działa / spóźniony / błąd / wyłączony)
  i licznikami przebiegów, błędów i efektów z 7 dni. Menu → Automatyzacje (admin, logistyka, demo).
  Backlog „wizytówki automatyzacji” (US-032…US-051) w `HISTORYJKI.md`.
- **Testy ekranów wysyłki do firm zewnętrznych i włączania 2FA** (US-031, TEST-007): wysyłka do awizacji,
  kolejka dnia do spedycji (tylko po potwierdzeniu), propozycja terminu od spedytora i wymuszone 2FA administratora.
  Lista stron bez testu: 16 → 12.
- **Testy ekranów o wysokim ryzyku** (US-018, TEST-007): reset i wymuszona zmiana hasła (bez zdradzania, czy konto
  istnieje), czyszczenie kolejki (podgląd przed usunięciem, liczba na przycisku) i import Excela (podgląd bez zapisu,
  pominięte w wyniku). Lista stron bez testu: 21 → 16.
- **Projekty decyzji do akceptacji PO:** ADR-0004 (publiczne API tylko do odczytu z kluczami per firma) i ADR-0005
  (własna kopia demo dla każdego odwiedzającego) — opcje, przegląd bezpieczeństwa STRIDE i pytania; bez kodu.
- **Skaner kodu QR na bramie** (US-030, pomysł 4 PO): ochrona skanuje telefonem kod z karty rozładunku albo wpisuje
  numer kontenera i jednym przyciskiem wpuszcza auto. Kontener spoza dzisiejszej listy dostaje ostrzeżenie zamiast
  przycisku; obraz z aparatu nie opuszcza telefonu. Na iPhonie: zwykły aparat albo numer (Z-021).
- **Pulpit analityczny** (prośba PO, widok w stylu Power BI): przepływ kontenerów przez 9 etapów procesu w 4 fazach
  z nazwanym wąskim gardłem, trzy wykresy kołowe (rodzaj transportu, porty, stan odprawy — liczba i udział
  w legendzie, podświetlanie po najechaniu) i rozładunki tydzień po tygodniu (minione / bieżący / zaplanowane).
  Paleta sprawdzona pod kątem daltonizmu, osobne odcienie dla ciemnego motywu; `GET /api/stats/overview`
  (zakres jak pulpit, odprawa ukryta dla spedytora). Demo dostało realny podział portów i transportu.
- **„Ścieżka rekrutera” w testach przeglądarkowych** (`npm run e2e:demo`, workflow „E2E — ścieżka rekrutera”):
  demo przeklikane na komputerze i telefonie — wejście bez hasła, historia kontenera, pulpit, „Jak to zbudowano”,
  tryb tylko-do-odczytu; strona bez przewijania w bok, przyciski z nazwą dla czytnika ekranu. Film do README:
  `docs/video/sciezka-rekrutera.mp4` (`scripts/record_demo_video.sh`).
- **Ryzyko kary za przestój z wyjaśnieniem** (pomysł 10 PO): karta na pulpicie mówi, dlaczego grozi kara i co
  zrobić — dostawa zaplanowana po końcu wolnych dni („3 dni kary, zaplanuj najpóźniej na …”) albo brak terminu
  tuż przed końcem wolnych dni. Jawne reguły (`backend/app/demurrage_risk.py`), bez kwot (stawek armatorów nie
  przechowujemy); `GET /api/stats/demurrage-risk`.
- **Kopia zapasowa poza serwer** (US-013, R-10): po każdej kopii zaszyfrowane pliki trafiają do magazynu zgodnego
  z S3 (`BACKUP_OFFSITE_*`, `docs/BACKUPY.md`). Jawna kopia nigdy nie wychodzi z serwera; błąd wysyłki = alert
  (brak heartbeatu). Włączenie: magazyn + 4 zmienne w Coolify.
- **„Wyślij plan” w kolejce** (US-017, P-09): zaznaczone kontenery → spedytor dostaje maila z proponowanymi datami
  dostaw i linkiem do zakładki Spedycja, gdzie potwierdza albo zmienia datę. Jeden mail na spedytora i spółkę,
  bez danych dostawcy; brak adresu e-mail lub działającej poczty jest pokazany wprost. Dotąd funkcja nie miała
  przycisku i nie wysyłała maila.
- **Demo: „historia jednego kontenera”** (pomysł 1 PO): ekran powitalny zaczyna od kontenera pokazowego, który
  przeszedł cały proces — jeden klik otwiera jego „Przebieg”. Dane demo dostały kroki odprawy, dokumentów i planu
  w kolejności zgodnej z etapami (`backend/scripts/seed_demo_story.py`).
- **„Przebieg” kontenera** (pomysł 3 PO): w zakładce historii czytelna oś czasu najważniejszych kroków —
  status, odprawa, dokumenty, plan, termin, slot, braki — z datą i osobą; pełna tabela zmian zostaje niżej.
- **Panel „Ile to oszczędza” na pulpicie** (pomysł 2 PO, mierniki z `WIZJA.md`): z danych aplikacji za 30 dni —
  zaoszczędzony czas (zmiany × 3 min, założenie Z-020 pokazane wprost), dostawy na czas, komplet dokumentów
  u agencji, kontenery ostrzeżone o karze za przestój. Logistyka i admin; zakres jak cała aplikacja.
- **Strona „Jak to zbudowano”** (pomysł 6 PO, `/jak-zbudowano`): architektura, jakość w liczbach i kluczowe decyzje
  z linkami do dokumentów w repozytorium; w menu użytkownika i na banerze demo.
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
- **Portugalia: SMS do kierowcy i kraj magazynu** (US-016, P-05, P-06): numer kierowcy bez kierunkowego dostaje
  kierunkowy kraju magazynu (PT +351 zamiast zawsze +48), więc SMS do kierowcy portugalskiego dochodzi. Magazyn
  tworzony z kolejki dziedziczy kraj spółki zamiast zawsze PL (Z-022).
- Telefon: panel „Ile to oszczędza” chował podpisy kafelków (założenie minut, „a z b”) — teraz widoczne.
- Demo: ostrzeżenia o karach za przestój w danych pokazowych (panel pokazywał 0 obok karty ryzyka); licznik
  karty ryzyka pokazuje wszystkie ryzyka, lista — najpilniejsze 8.
- **Demo: „Invalid host header”** — `ALLOWED_HOSTS` wpisany na stałe w `docker-compose.demo.yml`
  (`container.queue.twapp.pl`, `127.0.0.1`, `localhost`); błędna wartość w panelu Coolify blokowała całe demo.
- Obraz aplikacji nie miał `age` ani `curl`: szyfrowanie kopii (`BACKUP_AGE_RECIPIENT`) kończyło się błędem,
  a heartbeat kopii (`BACKUP_PING_URL`) nie dochodził. Oba programy są teraz w `Dockerfile.coolify`.
- **Zmiana statusu na nieaktualnym widoku nie nadpisuje cudzej zmiany** (US-003, R-02, P-13, ADR-0003). Status
  kontenera, odprawy i zlecenia transportowego: panel wysyła status, który widział; inny w bazie = 409
  `state_changed` z aktualną wartością. Niezwiązane zmiany (notatka, tracking) nie dają konfliktu. Pole
  opcjonalne — importy, n8n i zmiany masowe działają jak dotąd. Formularz kontenera był chroniony już wcześniej.
- **Formularz awizacji nie pokazuje sukcesu, gdy zapis się nie udał** (US-009, P-01). Dotąd każdy błąd 409
  (poza zajętym slotem) w etapie 1, a każdy 409 w etapie 2 (dane kierowców) kończył się ekranem
  „odpowiedź zapisana”. Teraz sukces tylko po 2xx; „już odpowiedziano” ma osobny ekran; każda inna odmowa
  zostawia formularz z powodem z API. Przegrany wyścig dwóch wysyłek zwraca kod `already_submitted`.

### Changed
- **Testy na wersjach z produkcji** (US-015, NFR-011): CI i README używają Pythona 3.14 i Node 26 — tych samych
  co obraz produkcyjny (dotąd CI testowało 3.12 i 24). Test pilnuje, żeby obraz, CI i README się nie rozjechały.
- Walidacja konfiguracji przy starcie wydzielona z `backend/app/main.py` do `backend/app/settings_check.py`
  (limit 500 linii); `main` re-eksportuje dotychczasowe nazwy, logi startu nadal pod nazwą `app.main`.
- `SECURITY.md`: poprawione stwierdzenia niezgodne z repozytorium (runnery GitHub zamiast self-hosted,
  brak `automerge.yml`), rozszerzone zgłaszanie podatności, sekcja o polityce i rejestrze ryzyk.
- `README.md`, `docs/README.md`: sekcja procesu zespołowego i mapa nowych dokumentów.

### Security
- **Eksport CSV z przeglądarki chroni przed formułami jak serwer** (US-008): wartość zaczynająca się od spacji
  i znaku `= + - @` (Excel pomija spacje) dostaje apostrof, tak jak dotąd tabulator i powrót karetki.
- **Semgrep blokuje PR** (US-007): reguły OWASP Top 10 jako bramka; pierwszy przegląd — 6 fałszywych alarmów
  (zapytania ze stałych nazw tabel) oznaczonych z uzasadnieniem.
- **Trivy blokuje PR** (US-007, R-08): podatność HIGH/CRITICAL z dostępną poprawką w zależnościach albo błąd
  konfiguracji zatrzymuje PR; cotygodniowy skan obrazu też jest bramką. Wyjątki tylko w `.trivyignore` z powodem i
  datą przeglądu. Obraz panelu jawnie działa jako użytkownik bez uprawnień (`USER 101`). Semgrep (OWASP Top 10)
  dochodzi jako raport; pre-commit używa tych samych wersji Bandit, gitleaks i ruff co CI.
- **Strażnik izolacji spółek** (US-011, R-01): nowa trasa z identyfikatorem w adresie bez kontroli spółki
  z `deps.py` zatrzymuje testy, chyba że trafi na jawną listę wyjątków z powodem. Decyzja o wymuszeniu w bazie:
  ADR-0006 (do akceptacji).
- **Publiczne linki chronione jednakowo** (US-005, R-06): link wywołań palet dla magazynu zewnętrznego (DLT) ma
  ten sam limit żądań i kontrolę pochodzenia co formularz awizacji, a jego adres nie wycieka w nagłówku Referer;
  wolne sloty awizacji można sprawdzić tylko w oknie ± 30 dni.
- **Spreparowane pliki nie zatrzymują aplikacji** (US-006, R-07): ZIP z plikiem rozpakowującym się ponad 100×
  (zip-bomba) jest pomijany z powodem; testy potwierdzają odrzucenie XML z „billion laughs” i XXE.
- **Wgrywane pliki sprawdzane po zawartości** (US-004, R-03): `faktura.pdf`, który nie jest PDF-em (albo
  „Excel”, który nie jest Excelem), jest odrzucany z czytelnym powodem i nic nie zostaje zapisane. Dotyczy
  załączników, faktur transportowych, archiwów ZIP i poczty przychodzącej. Bez weryfikacji zostają .doc, .xls,
  .msg i .eml (brak pewnej sygnatury).
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
