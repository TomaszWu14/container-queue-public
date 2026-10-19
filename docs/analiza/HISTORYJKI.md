# Backlog — historyjki użytkownika

Wersja 0.1 (2026-10-16), [BA]. Priorytety MoSCoW przyjęte na podstawie audytu (`docs/AUDYT.md`) i założeń
Z-005…Z-007 — **do potwierdzenia przez PO**. Nic z tej listy nie jest zaplanowane do realizacji, dopóki PO nie
zaakceptuje priorytetów; kolejność w ramach *Must* jest propozycją zespołu.

Rozmiar: XS (< 2 h), S (≤ 1 dzień), M (2–3 dni), L (> 3 dni). Role: [BA] [DEV] [SEC] [OPS].
Każda historyjka przechodzi proces z `CONTRIBUTING.md` (analiza → wymagania bezpieczeństwa → projekt →
implementacja → przegląd SEC → odbiór BA → PR). Śledzenie: `SLEDZENIE.md`. Ryzyka: `../bezpieczenstwo/RYZYKA.md`.

## Definition of Ready (skrót)

Cel jasny · kryteria testowalne (Dane/Gdy/Wtedy) · zależności znane · dane i uprawnienia określone ·
klasa danych i mini-STRIDE od [SEC] · priorytet od PO.

---

## Must — pilne poprawki z audytu

### US-001 · [SEC] Produkcja odmawia startu bez PostgreSQL
- **Rozmiar:** S · **Źródło:** R-04, B-005 · **Wymagania:** NFR-011, SR-009
- **Stan (2026-10-16):** zrealizowane w PR #18 (draft); odbiór [BA] ✅, przegląd [SEC] ✅. **Czeka na PO:**
  potwierdzenie, że produkcja ma `DATABASE_URL=postgresql…` (Z-007), i decyzję o scaleniu.
- **Jako** administrator aplikacji **chcę**, aby instancja z `ENVIRONMENT=production` odmówiła startu, gdy
  `DATABASE_URL` nie wskazuje PostgreSQL, **aby** błąd konfiguracji nie uruchomił pustej bazy SQLite bez kopii.
- **Kryteria akceptacji**
  - Dane: `ENVIRONMENT=production`, `DATABASE_URL` puste albo `sqlite://…` → Gdy aplikacja startuje → Wtedy
    `RuntimeError` z nazwą zmiennej w komunikacie (jak dla `SECRET_KEY`), proces nie nasłuchuje.
  - Dane: `ENVIRONMENT=production`, `DATABASE_URL=postgresql+psycopg2://…` → Gdy start → Wtedy start przechodzi.
  - Dane: `ENVIRONMENT=dev`, SQLite → Gdy start → Wtedy start przechodzi (jak dziś).
- **[SEC]:** bez nowych danych. Ryzyko operacyjne: zatrzymany start przy złej konfiguracji — **merge po
  potwierdzeniu PO** (Z-007). Sprawdzone 2026-10-16: `docker-compose.coolify.yml` i `docker-compose.demo.yml`
  ustawiają PostgreSQL.
- **Test:** `backend/tests/test_config_failfast.py` (planowany w `ETAP-0-PLAN.md`, nie istnieje).
- **DoR:** spełnione poza priorytetem PO.

### US-002 · [SEC] Osobny klucz szyfrowania danych na produkcji
- **Rozmiar:** S · **Źródło:** R-05, SEC-017 · **Wymagania:** SR-009
- **Jako** administrator **chcę**, aby produkcja wymagała `DATA_ENCRYPTION_KEY` osobnego od `SECRET_KEY`,
  **aby** rotacja klucza JWT po incydencie nie niszczyła zaszyfrowanych danych, a wyciek jednego sekretu nie
  otwierał obu zastosowań.
- **Kryteria akceptacji**
  - Dane: production bez `DATA_ENCRYPTION_KEY` albo z wartością równą `SECRET_KEY` → Gdy start → Wtedy odmowa
    startu z nazwą zmiennej.
  - Dane: klucz ustawiony, w bazie wartości zaszyfrowane starym kluczem → Gdy odczyt → Wtedy odszyfrowanie
    działa (MultiFernet), nowy zapis idzie nowym kluczem.
  - `docs/operacje/RUNBOOK.md` opisuje rotację obu kluczy krok po kroku.
- **[SEC]:** jak US-001 — **merge po ustawieniu zmiennej w Coolify przez PO** (Z-007).
- **Test:** `test_config_failfast.py`, istniejące testy `crypto`.

### US-003 · [DEV][SEC] Ochrona przed cichym nadpisaniem przy równoczesnej edycji
- **Rozmiar:** M · **Źródło:** R-02, B-004, P-13 · **Wymagania:** FR-006 (historia), NFR-013
- **Stan (2026-10-16):** zrealizowane w PR #18; odbiór [BA] ✅, przegląd [SEC] ✅. Rozpoznanie: formularz kontenera
  i panel kierowcy były już chronione (`expected_updated_at`, audyt DB-005). Dołożono przejścia statusu kontenera,
  odprawy i zlecenia transportowego — oczekiwany status zamiast `updated_at` (ADR-0003). Zmiany masowe
  i import Excela świadomie bez kontroli (ADR-0003, konsekwencje).
- **Jako** logistyk **chcę**, aby zapis kontenera, statusu, odprawy albo zlecenia, którego ktoś zmienił
  w międzyczasie, został odrzucony z czytelnym komunikatem, **aby** cudza zmiana nie znikała bez śladu.
- **Kryteria akceptacji**
  - Dane: dwa klienty mają rekord w wersji N → Gdy A zapisuje → Wtedy rekord ma wersję N+1 (odpowiedź zawiera wersję).
  - Dane: B wysyła zapis z wersją N → Gdy zapis → Wtedy 409 z komunikatem „Ktoś zmienił ten rekord w międzyczasie”
    i aktualnym stanem; nic nie jest zapisane.
  - Dane: panel dostaje 409 → Gdy użytkownik widzi komunikat → Wtedy może odświeżyć i powtórzyć; brak napisu „zapisano”.
  - Zakres: `PATCH /api/containers/{id}`, zmiana statusu, odprawa, zlecenia transportowe; import z Excela i n8n
    poza zakresem tej historyjki (osobna decyzja).
- **[DEV]:** ADR o mechanizmie (kolumna `version` vs `updated_at`/`If-Match`) przed kodem.
- **Test:** `test_concurrency.py` (planowany, nie istnieje) + test RTL komunikatu.

### US-004 · [SEC] Załączniki sprawdzane po zawartości, nie tylko po rozszerzeniu
- **Rozmiar:** S/M · **Źródło:** R-03, T-05 · **Wymagania:** SR-007
- **Jako** logistyk **chcę**, aby plik od spedytora z rozszerzeniem `.pdf`, który nie jest PDF-em, był
  odrzucony przy wgrywaniu, **aby** złośliwy plik nie krążył między firmami pod fałszywą nazwą.
- **Kryteria akceptacji**
  - Dane: plik `x.pdf` o bajtach nie-PDF → Gdy upload załącznika → Wtedy 422 z powodem; nic nie zapisane.
  - Dane: PDF, PNG/JPG/WEBP/GIF, DOCX/XLSX (ZIP z `[Content_Types].xml`), ZIP, XML/JSON/TXT/CSV (tekst bez bajtów NUL)
    zgodne z rozszerzeniem → Gdy upload → Wtedy 201 jak dziś.
  - Dane: rozszerzenie dozwolone, sygnatura nieznana (np. `.msg`, `.eml`, `.doc`, `.xls`) → Gdy upload → Wtedy
    przyjęty, ale w rejestrze ryzyk wpis o braku weryfikacji dla tych typów.
- **[SEC]:** wspólna funkcja z istniejącym sniffingiem zdjęć; pobieranie już idzie jako `attachment`.
- **Test:** `backend/tests/test_file_signatures.py` (31 przypadków: sygnatury, API, ZIP).
- **Stan:** zrealizowane („rób A”, PO 2026-10-16). `backend/app/file_signatures.py` sprawdza zawartość w czterech
  wejściach plików: załączniki kontenera, faktury transportowe, rozpakowywany ZIP i poczta przychodząca (ZIP
  i poczta: plik niezgodny pominięty z powodem, reszta wgrana). Testy z „udawanymi” plikami .xlsx dostały
  prawdziwe minimalne pliki (`tests/conftest.py::xlsx_bytes`).

### US-005 · [SEC] Jednolita ochrona wszystkich tras publicznych
- **Rozmiar:** S · **Źródło:** R-06, T-01, T-03 · **Wymagania:** FR-021, SR-002
- **Jako** administrator **chcę**, aby link wywołań palet (MAG-1) i wolne sloty awizacji miały ten sam limit
  żądań, kontrolę pochodzenia i walidację parametrów co formularz awizacji, **aby** żadna publiczna trasa nie
  była słabszym ogniwem.
- **Kryteria akceptacji**
  - Dane: > 30 żądań/min z jednego IP na `/api/mag1/{token}` → Gdy kolejne → Wtedy 429 z `Retry-After`.
  - Dane: żądanie POST z obcym `Origin` → Gdy wysyłka → Wtedy 403.
  - Dane: `GET /api/avizo/{token}/slots` z datą poza zakresem ważności linku ± 30 dni → Gdy żądanie → Wtedy 422.
- **Test:** `test_public_routes_guard.py`, `test_mag1_confirm.py`, `test_avizo_slots.py`.
- **Stan:** wdrożone w PR #30. Ochrona w jednym miejscu: `app/public_guards.py`
  (awizacja i MAG-1); link MAG-1 dostał też nagłówki `no-referrer` / `noindex`.

### US-006 · [SEC] Bezpieczne parsowanie XML i archiwów ZIP
- **Rozmiar:** S · **Źródło:** R-07, T-06 · **Wymagania:** SR-006
- **Jako** administrator **chcę**, aby XML (SAD) parsował `defusedxml`, a limit ZIP liczył się z faktycznie
  rozpakowanych bajtów, **aby** spreparowany plik nie zatrzymał całej aplikacji.
- **Kryteria akceptacji**
  - Dane: XML z DTD/encjami zewnętrznymi albo „billion laughs” → Gdy import SAD → Wtedy 422, proces żyje.
  - Dane: ZIP deklarujący 1 MB, rozpakowujący się do 2 GB → Gdy upload archiwum → Wtedy 413 po przekroczeniu
    `MAX_UPLOAD_MB` w trakcie rozpakowywania; współczynnik kompresji > 100 odrzucony.
- **Test:** `test_imports_malicious.py`, `test_sad_xml.py`, `test_archive_upload.py`.
- **Stan:** wdrożone w PR #30. Rozpoznanie: XML był już chroniony odrzuceniem DTD
  przed parserem (expat; ten sam efekt co `defusedxml`, bez nowej zależności), a `zipfile` nie czyta więcej
  niż rozmiar z nagłówka. Dołożono limit kompresji > 100× dla plików powyżej 1 MB i testy na spreparowane pliki.

### US-007 · [SEC][OPS] Bramki bezpieczeństwa w CI domknięte
- **Rozmiar:** S · **Źródło:** R-08 · **Wymagania:** SR-013
- **Jako** SEC **chcę**, aby Trivy (HIGH/CRITICAL z dostępną poprawką) i Semgrep (reguły OWASP) blokowały PR,
  a wersje narzędzi pre-commit były równe CI, **aby** znane podatności nie wchodziły do `main`.
- **Kryteria akceptacji**
  - Dane: obraz z CVE HIGH z poprawką → Gdy `security.yml` → Wtedy job czerwony; wyjątki tylko w `.trivyignore`
    z uzasadnieniem i datą przeglądu.
  - Dane: kod z wzorcem z `p/owasp-top-ten` → Gdy PR → Wtedy job Semgrep czerwony; fałszywy alarm oznaczony
    `# nosemgrep: <id>` z powodem.
  - `.pre-commit-config.yaml`: Bandit 1.9.4, gitleaks 8.30.1 (jak CI).
  - Zrobione w PR procesu: `.github/dependabot.yml` (Z-016).
- **Uwaga:** CI nie biegnie na draftach — walidacja wymaga oznaczenia PR jako gotowy.
- **Stan (2026-10-17):** wdrożone w PR #33 i #34. Trivy: bramka na PR (fs, HIGH/CRITICAL z poprawką) i w cotygodniowym
  skanie obrazu; `.trivyignore` z formatem wyjątków; obraz panelu z jawnym `USER 101` (jedyne znalezisko Trivy).
  pre-commit: Bandit 1.9.4, gitleaks 8.30.1, ruff 0.17.0 jak CI (test `test_runtime_versions.py`).
- **Domknięcie (PR #34, wdrożone):** Semgrep p/owasp-top-ten jest bramką. Pierwszy raport: 6 znalezisk, wszystkie fałszywe
  (zapytania DDL/COUNT sklejane ze stałych nazw w `backup_verify.py` i `db_bootstrap.py` — nazw tabel i baz nie da się
  związać parametrem); oznaczone `# nosemgrep: <id>` z powodem.

### US-008 · [SEC] `csv_safe` neutralizuje tabulator i powrót karetki
- **Rozmiar:** XS · **Źródło:** B-002 · **Wymagania:** SR-006
- Dane: wartość `\t=1+1` albo `\r=cmd` w eksporcie CSV → Gdy pobranie → Wtedy pole poprzedzone apostrofem,
  jak dla `= + - @`. **Test:** parametryzowany test `csv_safe` na wszystkie prefiksy OWASP.
- **Stan:** serwer (`exports.csv_safe`) był już poprawiony w audycie SEC-008 (test `test_csv_safe_leading_whitespace_and_control_chars`).
  Luka została w eksporcie budowanym w przeglądarce (`api.ts::csvCell`): formuła po wiodącej spacji (` =1+1`) nie była
  neutralizowana — wyrównane z serwerem (PR po #34), test `csv.export.dom.test.ts`.

### US-009 · [BA][DEV] Odpowiedź na awizację w aplikacji nie udaje sukcesu
- **Rozmiar:** S · **Źródło:** P-01 · **Wymagania:** FR-020, NFR-007
- **Stan (2026-10-16):** zrealizowane w PR #18; odbiór [BA] ✅, przegląd [SEC] ✅. Zakres szerszy niż P-01:
  ten sam błąd był w formularzu danych kierowców (etap 2) i przy ponownym wejściu na wysłany link.
- **Jako** spedytor z kontem **chcę** zobaczyć błąd, gdy mojej odpowiedzi nie da się zapisać (409: link
  użyty, awizacja zamknięta), **aby** nie wyjść z aplikacji w przekonaniu, że termin potwierdziłem.
- **Kryteria akceptacji**
  - Dane: awizacja już odpowiedziana → Gdy spedytor wysyła odpowiedź → Wtedy komunikat błędu z powodem z API,
    formularz zostaje, brak komunikatu „wysłano”.
  - Dane: błąd sieci/5xx → Gdy wysyłka → Wtedy komunikat „nie udało się”, możliwość ponowienia.
- **Test:** test RTL `AvizoFormPage` (409 i 5xx).

### US-010 · [DEV] Dokumentacja po audycie zgodna ze stanem repozytorium
- **Rozmiar:** XS · **Źródło:** `AUDYT.md` §4
- `BUGS-FOUND.md`: B-001, B-003 → NAPRAWIONE; `CLAUDE.md` i `ONBOARDING-DEV.md` bez odwołań do
  `graphify-out/`; `docs/testy/E2E.md` i `docs/CLAUDE-GITHUB.md` z notą, że workflowy istnieją tylko w repo
  prywatnym; `README.md`: czas testów. `SECURITY.md` poprawiono w PR procesu.

### US-027 · [BA][DEV] Demo pokazuje cały proces, nie tylko kolejkę
- **Rozmiar:** M · **Źródło:** pomysły 1–5 PO, 2026-10-16 („aplikacja flagowa”) · **Wymagania:** FR-005, FR-009…FR-011,
  FR-019, FR-020, FR-028 · **Priorytet:** Must (decyzja PO 2026-10-16: „rób”)
- **Stan:** zrealizowane w PR #18; odbiór [BA] ✅, przegląd [SEC] ✅; scalone (wdrożone).
- **Jako** osoba z zewnątrz oglądająca demo **chcę** zobaczyć odprawę, dokumenty, awizację, zamówienia i demurrage
  na żywych danych, **aby** ocenić cały proces, a nie samą listę kontenerów.
- **Kryteria akceptacji**
  - Dane: świeży seed → Wtedy status odprawy zgodny z etapem (przed portem BRAK, ZREALIZOWANY = ROZLICZONY,
    ODPRAWA nigdy BRAK), kilka REWIZJI z notatką i datą, agencja przypisana dokładnie wtedy, gdy odprawę zlecono.
  - Wtedy każdy kontener ma armatora i port docelowy, a co najmniej 3 mają termin demurrage za ≤ 3 dni (alert FR-028).
  - Wtedy 30 zamówień po 3 kontenery.
  - Wtedy wymagane kafelki dokumentów (PI, CI, PL, BL, SAD) mają pliki PDF na dysku, z celowymi brakami
    w części kontenerów; po rozładunku jest CMR; status obiegu dokumentów zgodny z odprawą.
  - Wtedy awizacje w stanach: czeka na spedytora, odpowiedź do decyzji (zgoda + prośba o inny termin),
    odrzucona z komentarzem, etap kierowców (wysłany i podany), zamknięta.
  - Słowniki usuwane przez czyszczenie demo (typy dokumentów z migracji) są odtwarzane.
- **[SEC]:** tylko dane syntetyczne (PDF z napisem „DEMO”, numery 000, domena example.com); bez nowych tras i danych osobowych.
- **Test:** `backend/tests/test_seed_demo_process.py`.

### US-028 · [BA][SEC] Konta demo per rola (spedytor, agencja celna, magazyn)
- **Rozmiar:** S · **Źródło:** pomysł 7 PO, 2026-10-16 · **Wymagania:** FR-022…FR-024 · **Priorytet:** Must („rób”)
- **Stan:** zrealizowane w PR #18; odbiór [BA] ✅, przegląd [SEC] ✅.
- **Jako** osoba oglądająca demo **chcę** zalogować się jako spedytor, agencja i magazyn, **aby** zobaczyć,
  że każdy partner widzi tylko swoje kontenery.
- **Kryteria akceptacji**
  - Dane: `DEMO_READONLY_LOGINS=demo,demo-spedytor,demo-agencja,demo-magazyn` → Gdy seed → Wtedy role wg słowa
    w loginie (logistyka, spedytor, agencja celna, magazyn MAG-1), to samo hasło `DEMO_PASSWORD`.
  - Gdy każde konto pobiera listę kontenerów → Wtedy ma co oglądać; spedytor widzi tylko swoje zlecenia,
    agencja tylko zlecone odprawy, magazyn tylko swój magazyn.
  - Gdy którekolwiek konto próbuje zapisu → Wtedy 403 „Konto demo — tylko podgląd”.
- **[SEC]:** rola przypisywana tylko kontom z listy `DEMO_READONLY_LOGINS` (seed tworzy konta wyłącznie z niej),
  więc każde jest tylko do odczytu po stronie API. Wyjątek E-05 rozszerzony o konta per rola.

### US-029 · [BA][SEC] Ograniczenia widoków kont demo (top 10)
- **Rozmiar:** M · **Źródło:** PO, 2026-10-16 („wdrażaj wszystkie”) · **Wymagania:** E-05, R-12 · **Priorytet:** Must
- **Stan:** wdrożone w PR #27.
- **Jako** właściciel publicznego demo **chcę**, żeby goście widzieli proces, ale nie zmieniali danych,
  nie podglądali siebie nawzajem i nie obciążali serwera, **aby** demo było bezpieczne i czytelne.
- **Kryteria akceptacji** (testy: `backend/tests/test_demo_limits.py`, `frontend/src/demoLimits.dom.test.tsx`,
  `frontend/src/pages/ProfilePage.demo.dom.test.tsx`)
  1. Gdy demo pobiera szkic .eml lub XML SADUE → 403; obieg dokumentów kontenera bez zmian; podgląd maila działa.
  2. Gdy demo otwiera mapę → pogoda bez zapytania do open-meteo.
  3. Dziennik zmian i audyt: ukryte w menu, trasa niedostępna, API 403.
  4. Obecność: demo nie widzi innych i nie jest widoczne.
  5. ZIP dokumentów, eksport kolejki do Excela, CSV wycen, raport błędów importu: ukryte, API 403.
  6. Profil: zamiast zdjęcia, 2FA i sesji — informacja o koncie wspólnym.
  7. Import SAD i Master data: ukryte w menu i trasach.
  8. Wywołania MAG-1 (linki publiczne dla partnera): ukryte, API 403. Linki awizacji nie są odczytywalne
     z bazy (tokeny jako SHA-256), więc demo ich nie zobaczy.
  9. Dzwonek powiadomień i aktualności na pulpicie: ukryte, API powiadomień 403.
  10. Baner „tylko podgląd” (był); przyciski zapisu w formularzach wyszarzone; każdy zapis odcinany
      w przeglądarce bez żądania, z tym samym komunikatem co serwer.
- **[SEC]:** egzekwowanie w API w jednym miejscu (`backend/app/demo_limits.py`, wołane z
  `security._enforce_demo_readonly`); ekrany tylko chowają. Zwykłe konta bez zmian (test).
- **Test:** `test_seed_demo_process.py::test_role_accounts_see_own_scope_and_cannot_write` (4 role).

### US-030 · [BA][DEV] Skaner kodu QR na bramie
- **Rozmiar:** S · **Źródło:** PO, 2026-10-16 („wdrażaj wszystko”, pomysł 4) · **Wymagania:** brak spisanego (moduł bramy #60 sprzed procesu; Z-005) · **Priorytet:** Should
- **Stan:** wdrożone w PR #28. Założenie Z-021 do potwierdzenia.
- **Jako** ochrona przy bramie **chcę** zeskanować telefonem kod QR z karty rozładunku (albo wpisać numer kontenera)
  i jednym przyciskiem wpuścić auto, **aby** nie szukać go na liście przy kolejce aut.
- **Kryteria akceptacji** (testy: `frontend/src/pages/gate/GateScanner.dom.test.tsx`, `gateScan.test.ts`)
  1. Kod QR z karty rozładunku albo wpisany numer (spacje, myślniki, małe litery bez znaczenia) → karta auta
     z numerem rejestracyjnym, kierowcą, magazynem i przyciskiem „Przyjechał — wpuść” (ten sam zapis co dotąd).
  2. Kontener spoza dzisiejszej listy bramy → ostrzeżenie „nie wpuszczaj bez sprawdzenia z logistyką”, bez przycisku.
  3. Auto już wpuszczone → godzina wpuszczenia zamiast przycisku.
  4. Przeglądarka bez odczytu kodów (np. iPhone) albo brak zgody na aparat → jasna podpowiedź: zwykły aparat
     albo wpisanie numeru.
  5. Aparat gaśnie od razu po odczycie lub zamknięciu.
- **[SEC]:** obraz z aparatu zostaje w telefonie (odczyt w przeglądarce, bez wysyłki); wyszukiwanie tylko na liście
  z API bramy (zakres użytkownika, `scope_containers`); wpuszczenie przez istniejący `POST /api/gate/{id}/checkin`.
  Aparat dozwolony już wcześniej tylko dla własnej domeny (`Permissions-Policy: camera=(self)`). Brak nowych zależności.

## Should

### US-011 · [SEC] Strażnik izolacji danych dla nowych tras
- **Rozmiar:** M · **Źródło:** R-01 · **Wymagania:** FR-022…FR-024, SR-005
- Test statyczny: każda trasa `/api/...` z parametrem `{..._id}` używa `get_scoped`/`scope_*`/
  `check_container_access` albo jest na jawnej liście wyjątków z uzasadnieniem. ADR: czy spójność spółki
  wymuszać też w bazie (CHECK/FK/RLS).
- **Stan:** wdrożone w PR #32. `tests/test_isolation_guard.py`: 226 tras z identyfikatorem,
  34 wyjątki z powodem (słowniki wspólne, konta admina, baza wiedzy, statki, własne sesje). Decyzja o bazie:
  ADR-0006 (proponowana: bez RLS, klucze złożone punktowo dla nowych tabel).

### US-012 · [SEC][BA] RODO: rejestr czynności, podstawy, powierzenia
- **Rozmiar:** M · **Źródło:** R-09 · **Wymagania:** SR-011 · **Zależy od:** odpowiedzi PO (Z-009).
- `RODO.md` z wersji 0.1 do 1.0: administrator, podstawy prawne potwierdzone, umowy powierzenia, ocena DPIA.

### US-013 · [OPS] Kopia zapasowa poza serwer i ćwiczenie odtworzenia
- **Rozmiar:** S · **Źródło:** R-10 · **Wymagania:** NFR-002, SR-014
- Kopia `age` wysyłana na drugie miejsce (np. S3/B2) po każdym backupie; odtworzenie przećwiczone wg RUNBOOK
  raz na kwartał z wpisem w rejestrze.
- **Stan:** kod gotowy (PR #28, „rób 3a” PO 2026-10-16). Kryteria: zaszyfrowane pliki z każdego uruchomienia idą
  do magazynu S3 (`BACKUP_OFFSITE_*`); bez klucza age odmowa wysyłki; błąd wysyłki = błąd skryptu i brak
  heartbeatu; klucze poza argumentami procesu. Obraz dostał `age` i `curl` (wcześniej ich brakowało:
  szyfrowanie i heartbeat nie działały). **Do zrobienia przez PO:** magazyn, klucz tylko do zapisu, 4 zmienne
  w Coolify, pierwsze próbne odtworzenie (`BACKUPY.md`).

### US-014 · [BA] Mierniki sukcesu liczone z danych aplikacji
- **Rozmiar:** S · **Źródło:** `WIZJA.md` M-1…M-7 · **Zależy od:** Z-004.
- Raport (skrypt albo ekran admina) z M-2…M-6 na podstawie `audit_log`, `users.last_seen`, tokenów awizacji.
- Pomysł 6 PO (2026-10-16): **panel mierników dla kierownika logistyki** jako ekran w aplikacji — odpowiedź na
  „ile to oszczędza”. Pomysły 8–10 z tej samej listy to US-009, US-003 i US-016.

### US-015 · [DEV] Jedna wersja Pythona i Node w README, CI i obrazie
- **Rozmiar:** S · **Źródło:** `AUDYT.md` §2.6 pkt 4 · **Wymagania:** NFR-011
- Decyzja: Python 3.12 albo 3.14 wszędzie (lock kompilowany dla wybranej), Node jedna wersja LTS; test
  w CI, że obraz i lock są zgodne.
- **Stan:** wdrożone w PR #31. Decyzja [DEV]: wersje produkcji — **Python 3.14, Node 26**
  (obraz już na nich działał, a CI testowało 3.12 i 24). CI i README przełączone; lock zostaje „universal” od 3.12
  (lokalnie da się pracować na 3.12+). Sprawdzone przed zmianą na 3.14 / 26: backend 2223 testów, mypy bez nowych
  błędów, frontend 1013 testów i build, e2e demo 6/6. Strażnik: `backend/tests/test_runtime_versions.py`.

### US-016 · [BA][DEV] Dane dla Portugalii: prefiks telefonu i kraj magazynu
- **Rozmiar:** S · **Źródło:** P-05, P-06 · **Wymagania:** FR-017
- **Stan:** wdrożone w PR #29. Założenie Z-022 do potwierdzenia.
- **Jako** logistyk **chcę**, żeby SMS do kierowcy portugalskiego dochodził, a magazyn w Portugalii miał
  portugalskie święta, **aby** dostawy do PT nie wymagały ręcznych poprawek.
- **Kryteria akceptacji** (test: `backend/tests/test_phones_portugal.py`)
  1. Numer kierowcy bez kierunkowego (9 cyfr) dostaje kierunkowy kraju magazynu: PL +48, PT +351 —
     w formularzu kierowców z awizacji i przy SMS-ie z panelu kierowcy; brak magazynu = +48 jak dotąd.
  2. Numer podany z „+” albo „00” zostaje bez zmian; numer nierozpoznany → 422 z przykładem PL i PT.
  3. Magazyn tworzony w locie z kolejki dostaje kraj pozostałych magazynów spółki, gdy wszystkie są
     w jednym kraju; inaczej PL. Formularz magazynu w Słownikach miał już wybór kraju (bez zmian).
- **[SEC]:** bez nowych tras i danych; numer w audycie dalej maskowany (RODO).

### US-017 · [BA][DEV] „Wyślij plan do spedycji” wysyła wiadomość
- **Rozmiar:** S · **Źródło:** P-09 · **Wymagania:** FR-015, FR-020
- Zmiana statusu planu na WYSLANE wysyła mail etapu 1 (albo jawnie informuje, że mail nie jest skonfigurowany).
- **Ustalenia PO (2026-10-16):** funkcja nie miała przycisku w aplikacji. Przycisk „Wyślij plan” w kolejce dla
  zaznaczonych kontenerów; plan idzie **wcześniej niż awizacja i zawiera same daty**; spedytor odpowiada,
  **logując się do aplikacji** (zakładka Spedycja), bez nowych linków publicznych.
- **Kryteria akceptacji** (testy `backend/tests/test_plan_mail.py`, `BulkActionBar.plan.dom.test.tsx`)
  - Gdy plan wysłany dla kilku kontenerów jednego spedytora i spółki → jeden mail z datami, numerami i linkiem
    do zakładki Spedycja, bez danych dostawcy; wpis w historii kontenera.
  - Gdy spedytor nie ma adresu albo poczta nie działa → wynik mówi to wprost; status planu i tak zapisany.
  - Gdy plan już potwierdzony → bez maila („już potwierdzone”).
- **Stan:** wdrożone w PR #28.

### US-018 · [DEV] Testy brakujących ekranów o wysokim ryzyku
- **Rozmiar:** M · **Źródło:** TEST-007 (`docs/testy/E2E.md`)
- Testy RTL dla `ImportModal`, `ClearQueueModal`, resetu hasła w `AuthPages`.
- **Stan:** wdrożone w PR #30. `AuthPages.dom.test.tsx` (7), `ClearQueueModal.dom.test.tsx` (3),
  `ImportModal.dom.test.tsx` (4); lista stron bez testu w `docs/testy/E2E.md` odświeżona (21 → 16).

### US-031 · [DEV][SEC] Testy ekranów wysyłki na zewnątrz i włączania 2FA
- **Rozmiar:** S · **Źródło:** TEST-007 (`docs/testy/E2E.md`), kontynuacja US-018 · **Wymagania:** FR-015, SR (2FA, SEC-006)
- **Jako** właściciel aplikacji **chcę**, żeby ekrany wysyłające maile do spedytorów i magazynów oraz ekran
  wymuszonego 2FA miały testy, **aby** regresja nie wysłała błędnych danych do firm zewnętrznych ani nie
  przepuściła administratora bez 2FA.
- **Kryteria akceptacji**
  1. Wysyłka do awizacji: podgląd po spedytorze (także „bez spedytora”), wysyłane dokładnie zaznaczone kontenery
     z uwagą i opcją magazynu; wynik pokazuje brak adresu; błąd nie zamyka okna (`AvizoSendModal.dom.test.tsx`).
  2. Kolejka dnia: magazyny tylko tej spółki, wysyłka dopiero po potwierdzeniu, anulowanie nic nie wysyła
     (`QueueEmailModal.dom.test.tsx`).
  3. Propozycja terminu: bez daty nie wyśle; kontener, data, godzina, uwaga trafiają do serwera; odmowa widoczna
     (`AvizoProposeForm.dom.test.tsx`).
  4. Wymuszone 2FA: kod przycięty wysłany z sekretem, kody zapasowe przed przejściem do panelu, błędny kod
     nie przepuszcza, wylogowanie dostępne (`Enroll2FAPage.dom.test.tsx`).
- **[SEC]:** tylko testy, bez zmian w kodzie aplikacji i bez nowych tras.
- **Stan:** wdrożone w PR #36. Lista stron bez testu: 16 → 12.

### US-019 · [SEC] 2FA obowiązkowe dla administratorów na produkcji
- **Rozmiar:** XS (konfiguracja) · **Źródło:** E-01 · **Zależy od:** decyzji PO (Z-008).
- `REQUIRE_2FA_ADMIN=true` w Coolify po tym, jak każdy admin włączy 2FA; procedura w RUNBOOK.

## Wizytówka automatyzacji procesów (prośba PO 2026-10-17)

PO: projekt ma być flagowym portfolio na stanowiska automatyzacji procesów, analizy biznesowej i pracy
z *citizen developerami*. 20 punktów z listy PO („wdróż wszystko”), po jednym temacie na PR. Wiele automatów
już działa — część historyjek to pokazanie ich i zmierzenie, nie budowa od zera. Założenia: Z-023…Z-025.

### US-032 · [BA][DEV] Ekran „Automatyzacje” — katalog automatów (pomysł 1)
- **Rozmiar:** M · **Wymagania:** FR-015, NFR (obserwowalność, OBS-009) · **Założenie:** Z-023
- **Jako** kierownik logistyki (i rekruter w demo) **chcę** jednej listy wszystkiego, co aplikacja robi sama,
  **aby** widzieć wyzwalacz, akcję i efekt każdego automatu bez czytania kodu.
- **Kryteria akceptacji** (testy `backend/tests/test_automations.py`, `AutomationsPage.dom.test.tsx`)
  1. Każda funkcja pętli tła z `jobs.build_jobs` ma wpis w katalogu (nowy automat bez wpisu = czerwony test);
     do tego obiegi z n8n: poczta → poczekalnia, draft SAD z poczty, zdarzenia wysyłane do n8n.
  2. Każdy wpis: nazwa, wyzwalacz, akcja (PL/EN/PT), kategoria, częstotliwość, ostatni przebieg, liczba przebiegów,
     błędów i efektów (utworzonych powiadomień) z 7 dni.
  3. Obiegi z poczty liczone tylko dla spółek użytkownika; treść błędów nie wychodzi poza dziennik admina.
  4. Ekran widzą admin i logistyka (konto demo to logistyka); partnerzy dostają 403.
- **[SEC]:** tylko odczyt; liczniki pętli tła są systemowe (bez danych spółek), obiegi z poczty w zakresie
  `scope_company` / `scope_containers`. Wpis w `tests/permissions.yaml`.
- **Stan:** wdrożone w PR #37.

### US-033 · [OPS][DEV] Pilnowanie automatów (pomysł 17)
- **Rozmiar:** S · **Wymagania:** OBS-009 · razem z US-032
- Stan automatu: **błąd** (ostatni przebieg nieudany), **spóźniony** (brak udanego przebiegu dłużej niż interwał
  + 1 h), **wyłączony** (pętla nie powstaje w tej konfiguracji), **brak przebiegów**; licznik „wymaga uwagi”.
- **Stan:** wdrożone w PR #37 (te same testy co US-032).

### US-034 · [BA][DEV] Licznik oszczędności per automat (pomysł 3)
- **Rozmiar:** M · **Rozszerza:** panel „Ile to oszczędza” (Z-020) · **Założenie:** Z-024
- **Jako** kierownik logistyki **chcę** widzieć, ile godzin pracy ręcznej zastąpiły automaty, **aby** odpowiedzieć
  na pytanie „ile to oszczędza” liczbą z danych, a nie szacunkiem z głowy.
- **Kryteria akceptacji** (testy `test_automations.py` — część US-034, `AutomationsPage.dom.test.tsx`)
  1. Każdy automat ma minuty pracy ręcznej na jeden efekt (wartości startowe = założenia Z-024); oszczędność =
     efekty z 7 dni × minuty (obiegi z poczty: liczba maili × minuty). Automaty porządkowe mają 0.
  2. Ekran pokazuje łączny zaoszczędzony czas w godzinach i oszczędność w każdym wierszu, z założeniem napisanym wprost.
  3. Admin zmienia minuty w oknie „Założenia minut” (0–240); nieznany automat albo wartość spoza zakresu = 422;
     każda zmiana trafia do dziennika zmian; logistyka dostaje 403.
- **[SEC]:** zapis tylko admin (`PUT /api/automations/minutes`, wpis w `tests/permissions.yaml`), ustawienie globalne
  bez danych spółek, audyt każdej zmiany.
- **Stan:** wdrożone w PR #38.

### US-035 · [DEV][SEC] Zdarzenia do n8n / Power Automate / Make widoczne i testowalne (pomysł 9)
- **Rozmiar:** S · Webhook z podpisem HMAC już istniał (`notifications.send_automation_event`).
- **Jako** citizen developer **chcę** wiedzieć, czy zdarzenia z aplikacji docierają do mojego workflow, i móc
  wysłać próbne, **aby** zbudować automatyzację bez proszenia IT o logi.
- **Kryteria akceptacji** (testy `test_automations.py` — część US-035, `test_automation.py`, `AutomationsPage.dom.test.tsx`)
  1. Zdarzenie ma `id` (deduplikacja), `version`, `source`; podpis HMAC liczony z wysłanych bajtów.
  2. Wynik każdej wysyłki (kod HTTP spoza 2xx i błąd sieci = błąd) zapisany w dzienniku zadań; ekran Automatyzacje
     liczy zdarzenia i błędy z 7 dni; nieudana wysyłka zapala dzwonek admina.
  3. Admin wysyła „zdarzenie testowe” z ekranu i widzi kod odpowiedzi; bez skonfigurowanego adresu → 409; odpowiedź
     nie zawiera adresu webhooka; każde wysłanie w dzienniku zmian (kto, kiedy, wynik); logistyka → 403.
  4. Panel Integracje pokazuje kanał n8n, podpis (włączony/brak) i ostatnią wysyłkę. Format w `docs/ZDARZENIA-N8N.md`.
- **[SEC]:** adres webhooka (bywa sekretem) nie wraca do przeglądarki; treść zdarzeń bez danych osobowych kierowców
  (GDPR-001, bez zmian); zdarzenie testowe tylko admin.
- **Stan:** wdrożone w PR #39.

### US-036 · [BA][DEV][SEC] Kreator reguł bez kodu (pomysł 8)
- **Rozmiar:** L · **Założenie:** Z-026
- **Jako** kierownik logistyki **chcę** sam ustawiać alerty „gdy warunek przez N dni → powiadom”, **aby** nie czekać
  na programistę przy każdej nowej potrzebie (praca w duchu *citizen developer*).
- **Kryteria akceptacji** (testy `backend/tests/test_automation_rules.py`, `AutomationRulesPanel.dom.test.tsx`)
  1. Zamknięty katalog 4 warunków z parametrami (dni 0–60, etap): ETA minęło N dni; awizacja w ciągu N dni, a kontener
     przed wybranym etapem; awizacja w ciągu N dni bez danych kierowcy; plan wysłany N dni temu bez potwierdzenia.
     Tylko otwarte, niedostarczone kontenery.
  2. Podgląd: ile kontenerów spełnia regułę dziś i które (do 10) — w zakresie spółek użytkownika.
  3. Pętla tła co godzinę: włączona reguła → powiadomienie (dzwonek, e-mail, Teams, n8n) do obserwujących kontener
     albo adminów; jedno na regułę, kontener i dzień; reguła wyłączona nic nie wysyła.
  4. Zapis całej listy tylko admin (najwyżej 20 reguł; zły warunek, brak etapu, dni > 60 → 422); każda dodana,
     zmieniona i usunięta reguła w dzienniku zmian; logistyka widzi reguły i podgląd, bez edycji.
  5. Automat „Reguły własne” na ekranie Automatyzacje (liczniki, stan, oszczędność 5 min/powiadomienie — Z-024).
- **[SEC]:** warunki to stała lista w kodzie — bez wolnego tekstu wykonywanego jako zapytanie; parametry walidowane
  (pydantic); podgląd przez `scope_containers`; bezpiecznik 200 kontenerów na regułę na przebieg; reguły w
  ustawieniach aplikacji (bez nowej tabeli i migracji); uszkodzony wpis pomijany, pozostałe działają.
- **Stan:** wdrożone w PR #39.

### US-037 · [DEV] Jakość odczytu faktur przez AI i trafność w czasie (pomysł 14)
- **Rozmiar:** M
- **Jako** kierownik logistyki **chcę** widzieć, jaką część pozycji faktur automat dopasowuje sam i jak trafne są
  podpowiedzi modelu, **aby** ufać automatowi tam, gdzie się sprawdza, a resztę zostawić człowiekowi.
- **Kryteria akceptacji** (testy `backend/tests/test_ai_quality.py`, `AiQualityPanel.dom.test.tsx`)
  1. Tydzień po tygodniu (8 tygodni): ile pozycji dopasowały reguły, model ML, człowiek, a ile czeka na decyzję.
  2. Odsetek pozycji dopasowanych automatycznie (reguły + ML) i trafność podpowiedzi modelu (ostateczny materiał =
     podpowiedź; poprawka operatora po automacie = pudło).
  3. Trafność w trzech przedziałach pewności: < 70% i 70%–próg (tylko podpowiedź dla człowieka), ≥ próg (automat
     ustawia sam; próg `ML_AUTO_APPLY_THRESHOLD`) — czy „90% pewności” rzeczywiście trafia.
  4. Tylko paczki faktur kontenerów w zakresie użytkownika; admin i logistyka; pozycje pominięte nie liczą się.
- **[SEC]:** tylko odczyt zliczeń (bez treści faktur), zakres przez `scope_containers`; wpis w `tests/permissions.yaml`.
- **Stan:** wdrożone w PR #40. Kolory wykresu z palety pulpitu, kolejność serii sprawdzona walidatorem
  palety (daltonizm, jasny i ciemny motyw).

### US-038 · [BA][DEV] Analiza przebiegu procesu z historii zmian (pomysł 16)
- **Rozmiar:** M
- **Jako** kierownik logistyki **chcę** widzieć, ile kontenery zwykle stoją w każdym etapie i które stoją dłużej
  niż zwykle, **aby** reagować na wąskie gardła bez ręcznego raportu w Excelu.
- **Kryteria akceptacji** (testy `backend/tests/test_process_mining.py`, `ProcessFlowPanel.dom.test.tsx`)
  1. Czas w etapie liczony z historii zmian statusu (`audit_log`): od wejścia do wyjścia z etapu; pierwszy etap
     od utworzenia kontenera. Dla każdego etapu: liczba pobytów, mediana i 90. percentyl (dni) — pobyty
     zakończone w oknie (domyślnie 90 dni, 14–365). Etap końcowy „zrealizowany” pomijany.
  2. Cofnięcia statusu (powrót do wcześniejszego etapu) liczone osobno i jako odsetek zmian — miara poprawek.
  3. Najczęstsze przejścia między etapami (do 8).
  4. „Do sprawdzenia”: kontenery w obecnym etapie dłużej niż 90. percentyl tego etapu, z linkiem do karty;
     liczone dopiero przy ≥ 5 zakończonych pobytach etapu (mniej to szum) — Z-027.
  5. Tylko kontenery w zakresie użytkownika; admin i logistyka.
- **[SEC]:** tylko odczyt zliczeń i numerów kontenerów już widocznych dla użytkownika; zakres przez
  `scope_containers`; bez danych osobowych z dziennika (kto zmienił — nie jest zwracane); wpis w `tests/permissions.yaml`.
- **Stan:** wdrożone w PR #42.

### US-039 · [DEV] Asystent widoczny w demo (pomysł 15)
- **Rozmiar:** S
- **Jako** rekruter oglądający demo **chcę** zadać asystentowi pytanie i dostać odpowiedź, **aby** zobaczyć, jak
  działa, choć na serwerze demo nie ma modelu AI.
- **Kryteria akceptacji** (testy `backend/tests/test_assistant.py`, `frontend/src/assistant.dom.test.tsx`)
  1. Bez modelu AI (albo po jego awarii) asystent odpowiada zdaniami z szablonu złożonymi z faktów z bazy
     (etap, statek, ETA, awizacja, odprawa, magazyn; materiał: nazwa, JM, CN).
  2. Odpowiedź z szablonu jest wprost oznaczona („na tym serwerze nie działa model AI”, `answer_source="template"`);
     odpowiedź modelu ma `answer_source="ai"`. Brak faktów → brak odpowiedzi (jak dotąd).
  3. Pod polem pytania do 3 przykładowych pytań z danych widocznych dla użytkownika (kontenery w zakresie spółki,
     materiał tylko dla ról z kartoteką); klik wysyła pytanie.
- **[SEC]:** szablon używa tylko faktów już przefiltrowanych (`scope_containers`, `hidden_fields`); przykłady przez
  `scope_containers`; nowa trasa `GET /api/assistant/examples` w `tests/permissions.yaml`. Z-028.
- **Stan:** wdrożone w PR #45.

### US-040 · [BA][DEV] „Symuluj dzień” w demo (pomysł 6)
- **Rozmiar:** M
- **Jako** rekruter w demo **chcę** jednym przyciskiem zobaczyć obieg automatów od maila do zaoszczędzonego czasu,
  **aby** zrozumieć, co aplikacja robi sama, bez czytania dokumentacji.
- **Kryteria akceptacji** (testy `backend/tests/test_demo_simulation.py`, `SimulateDayPanel.dom.test.tsx`)
  1. Przycisk „Symuluj dzień” na ekranie Automatyzacje (konto demo) pokazuje 5 kroków na kontenerze z danych demo:
     mail od spedytora → numer kontenera odczytany z treści (cyfra kontrolna), faktura (reguły / ML / człowiek /
     do decyzji), reguły z kreatora (ile kontenerów dziś), zdarzenie do n8n z podpisem HMAC, zaoszczędzone minuty.
  2. Każdy krok woła prawdziwą funkcję aplikacji; link prowadzi do karty kontenera.
  3. **Bez zapisu i wysyłki** — konto demo zostaje tylko do odczytu (Z-029); liczba wpisów w dzienniku, przebiegów
     i powiadomień po symulacji bez zmian.
  4. Tylko kontenery w zakresie użytkownika; brak kontenerów → komunikat.
- **[SEC]:** trasa `GET /api/automations/simulate-day` (Editors, `scope_containers`), bez wyjątku w blokadzie zapisu
  konta demo; podpis liczony sekretem pokazowym, prawdziwy sekret nie opuszcza serwera.
- **Stan:** wdrożone w PR #47.

### US-041 · [DEV][SEC] Akceptacja z poziomu Teams (pomysł 18)
- **Rozmiar:** S
- **Jako** logistyk **chcę** z karty w Teams jednym kliknięciem przejść do kontenera, którego dotyczy powiadomienie,
  **aby** zareagować od razu, bez szukania go w aplikacji.
- **Kryteria akceptacji** (testy `test_teams_mail_status.py`, `test_notifications_w4.py`)
  1. Powiadomienie dotyczące kontenera wysłane do Teams ma przycisk „Otwórz w aplikacji” (Adaptive Card,
     `Action.OpenUrl`) prowadzący do karty kontenera (`PUBLIC_BASE_URL/kontenery/{id}`).
  2. Powiadomienie bez kontenera albo instancja bez `PUBLIC_BASE_URL` — karta bez przycisku (jak dotąd).
  3. Przycisk niczego nie zatwierdza sam: decyzję podejmuje zalogowany użytkownik z własnymi uprawnieniami.
- **[SEC]:** w karcie tylko link (bez tokenu, bez akcji z czatu) — kanał Teams widzi więcej osób niż uprawnionych
  do kontenera, więc wszystko za logowaniem; adres z konfiguracji, nie z danych użytkownika.
- **Stan:** wdrożone w PR #49.

### US-042 · [DEV] Konektor Power Automate (pomysł 10)
- **Rozmiar:** S · Plik konektora (OpenAPI 2.0) dla odczytu kolejki i zdarzeń + przykładowy przepływ.
- **Stan:** decyzja PO 2026-10-18 — „tylko instrukcje” na eksporcie do Excela, bez nowego dostępu do API;
  wdrożone w PR #51 — `docs/MICROSOFT-365.md` (test `test_m365_docs.py`: kolumny eksportu = instrukcja).

### US-043 · [BA] Szablon Excela z Power Query (pomysł 11)
- **Rozmiar:** S · Excel pobierający kolejkę z API tokenem tylko do odczytu; instrukcja krok po kroku.
- **Stan:** decyzja PO 2026-10-18 — „tylko instrukcje” na eksporcie do Excela, bez nowego dostępu do API;
  wdrożone w PR #51 — `docs/MICROSOFT-365.md` (test `test_m365_docs.py`: kolumny eksportu = instrukcja).

### US-044 · [BA] Raport Power BI na danych aplikacji (pomysł 12)
- **Rozmiar:** M · Model danych i zapytania Power Query (M) + instrukcja zbudowania raportu.
- **Stan:** decyzja PO 2026-10-18 — „tylko instrukcje” na eksporcie do Excela, bez nowego dostępu do API;
  wdrożone w PR #51 — `docs/MICROSOFT-365.md` (test `test_m365_docs.py`: kolumny eksportu = instrukcja).

### US-045 · [BA] Poradnik „Własna automatyzacja w 15 minut” (pomysł 13)
- **Rozmiar:** S · n8n + token serwisowy, krok po kroku, z gotowym workflow do zaimportowania.
- **Stan:** wdrożone w PR #50 — `docs/WLASNA-AUTOMATYZACJA-15-MIN.md`, `deploy/n8n/zdarzenie-do-teams.json`
  (test `backend/tests/test_n8n_workflows.py`: połączenia między node'ami, podpis HMAC przed akcją).

### US-046 · [BA] Mapa procesu „przed i po” (pomysł 2)
- **Rozmiar:** S · Rysunek z `docs/bpmn/timporye-proces.bpmn`, kroki przejęte przez automaty zaznaczone.
- **Stan:** wdrożone w PR #48 — `docs/dla-rekrutera/OBIEG-DOKUMENTU-PRZED-PO.md`.

### US-047 · [BA] Studium przypadku na jedną stronę (pomysł 4)
- **Rozmiar:** XS · Problem → miara → rozwiązanie → wynik; do CV i LinkedIn.
- **Stan:** wdrożone w PR #48 — `docs/dla-rekrutera/STUDIUM-PRZYPADKU.md`.

### US-048 · [BA] README po angielsku (pomysł 7)
- **Rozmiar:** S · `README.en.md` z sekcją „Automations in numbers”.
- **Stan:** wdrożone w PR #48 — `README.en.md`.

### US-049 · [BA] „Jak wybieram, co automatyzować” (pomysł 19)
- **Rozmiar:** S · Macierz liczba spraw × czas × ryzyko błędu na pomysłach z `docs/pomysly-automatyzacje.md`.
- **Stan:** wdrożone w PR #48 — `docs/dla-rekrutera/MACIERZ-AUTOMATYZACJI.md`.

### US-050 · [BA] Mierniki przed i po wdrożeniu (pomysł 20)
- **Rozmiar:** S · **Założenie:** Z-025 · Czas zaplanowania dostawy, liczba maili, liczba błędów — wartości
  „przed” od PO albo jawne założenia.
- **Stan:** wdrożone w PR #48 — `docs/dla-rekrutera/MIERNIKI-PRZED-PO.md`.

### US-051 · [DEV] Nagranie obiegu z poczty (pomysł 5)
- **Rozmiar:** S · Wideo z testu przeglądarkowego: mail → n8n → poczekalnia → „Potwierdź”.

### US-052 · [DEV] Demo z danymi na ekranie „Automatyzacje” (top 15 PO, pkt 1)
- **Rozmiar:** S
- **Jako** rekruter w demo **chcę** zobaczyć działające automaty, reguły i jakość odczytu faktur, **aby** nie trafić
  na pusty ekran („Brak faktur”, brak reguł, automaty „bez przebiegów”).
- **Kryteria akceptacji** (test `backend/tests/test_seed_demo_automation.py`)
  1. Dziennik zadań z 7 dni: każdy włączony automat ma przebiegi i stan „działa”, część z efektem; jedna dawna awaria
     śledzenia (licznik błędów 1, stan dalej „działa”); zdarzenia do n8n.
  2. 3 przykładowe reguły z kreatora (US-036).
  3. Faktury z 8 tygodni: reguły / model ML / człowiek / do decyzji, trafność rośnie z pewnością modelu.
- **[SEC]:** tylko skrypt `seed_demo` (instancja demo, osłony `check_guards`); dane zmyślone, pliki PDF pokazowe.
- **Stan:** wdrożone w PR #46.

### US-053 · [DEV] Strażnik automatów (druga lista PO, pkt 7)
- **Rozmiar:** S
- **Jako** administrator **chcę** dostać powiadomienie, gdy automat przestaje działać po cichu, **aby** nie dowiedzieć
  się o tym dopiero od użytkownika („dlaczego nie dostałem alertu o karze?”).
- **Kryteria akceptacji** (test `backend/tests/test_automation_watchdog.py`)
  1. Co godzinę: automat z harmonogramu w stanie „spóźniony” (brak udanego przebiegu dłużej niż interwał + 1 h)
     → dzwonek adminów z datą ostatniego udanego przebiegu.
  2. Jedno powiadomienie na automat na dobę polską; automaty w normie nie wysyłają nic.
  3. Strażnik sam jest w katalogu automatów (widać, czy działa).
- **[SEC]:** tylko odczyt dziennika zadań; odbiorcy = aktywni admini.
- **Stan:** wdrożone w PR #53.

### US-054 · [DEV] Tygodniowy raport automatów (druga lista PO, pkt 9)
- **Rozmiar:** S
- **Jako** kierownik logistyki **chcę** w poniedziałek rano dostać krótkie podsumowanie pracy automatów, **aby** bez
  wchodzenia na ekran wiedzieć, ile czasu zaoszczędziły i czy coś wymaga uwagi.
- **Kryteria akceptacji** (test `backend/tests/test_automation_report.py`)
  1. Poniedziałek 8:00–9:00 (czas PL): admin i logistyka dostają jedno powiadomienie (dzwonek + e-mail wg matrycy).
  2. Treść: zaoszczędzone godziny (z założeniem minut), przebiegi i efekty, automaty w stanie błąd/spóźniony,
     trzy automaty, które oszczędziły najwięcej — liczby z katalogu w zakresie danego użytkownika.
  3. Poza oknem i drugi raz tego samego dnia — nic.
- **[SEC]:** raport per użytkownik z jego zakresem (obiegi z poczty liczone przez `scope_containers`); bez kanałów
  wspólnych (Teams/n8n), żeby liczby jednej spółki nie trafiły do innych.
- **Stan:** wdrożone w PR #54.

### US-055 · [DEV] Język startowy z przeglądarki (druga lista PO, pkt 2)
- **Rozmiar:** XS
- **Jako** rekruter z zagranicy **chcę** zobaczyć aplikację od razu po angielsku, **aby** nie szukać przełącznika języka.
- **Kryteria akceptacji** (test `frontend/src/i18n.detect.test.ts`)
  1. Pierwsza wizyta: pierwszy obsługiwany język przeglądarki (pl / en / pt, także z regionem, np. `pt-BR`).
  2. Żaden obsługiwany → angielski. Zapamiętany wybór użytkownika zawsze wygrywa.
  3. Testy (vitest, Playwright) ustawiają polską przeglądarkę — sprawdzają polskie teksty jak dotąd.
- **[SEC]:** bez zmian (tylko wybór słownika w przeglądarce).
- **Stan:** wdrożone w PR #55.

### US-056 · [DEV] Test przeglądarkowy ekranu Automatyzacje w demo (druga lista PO, pkt 3)
- **Rozmiar:** XS
- **Jako** właściciel portfolio **chcę**, żeby CI sprawdzało ekran Automatyzacje w demo, **aby** pokaz dla rekrutera
  nie zepsuł się po cichu.
- **Kryteria akceptacji** (test `frontend/e2e/demo/recruiter.spec.ts`, komputer i telefon)
  1. Katalog ma ponad 20 automatów, żaden w stanie „błąd”; widać zaoszczędzony czas.
  2. Panele reguł, odczytu faktur (bez „Brak faktur”) i przebiegu procesu mają dane z seeda demo.
  3. „Symuluj dzień” pokazuje 5 kroków z odczytanym numerem kontenera; strona nie przewija się w bok, przyciski
     mają nazwy.
  4. Przeglądarka po angielsku → demo od razu po angielsku (US-055).
- **Stan:** wdrożone w PR #56.

### US-057 · [DEV] Lighthouse w CI (druga lista PO, pkt 14)
- **Rozmiar:** S
- **Jako** rekruter techniczny **chcę** widzieć zmierzoną jakość strony, **aby** nie oceniać jej „na oko”.
- **Kryteria akceptacji** (workflow `.github/workflows/lighthouse.yml`, progi `frontend/scripts/lighthouse-assert.mjs`)
  1. Każdy PR zmieniający frontend mierzy stronę logowania (backend serwuje zbudowany panel — jak produkcja).
  2. Progi: dostępność ≥ 95, dobre praktyki ≥ 95, SEO ≥ 90, szybkość ≥ 70 (zapas na zmienność maszyn CI);
     poniżej progu — czerwone CI. Tabela wyników w podsumowaniu joba, raport HTML w artefaktach, odznaka w README.
  3. Poprawki znalezione pomiarem: przyciski języka w stopce logowania ≥ 28 px (dotyk), opis strony, ikona,
     `robots.txt` (bez indeksowania `/api/`).
- **Stan:** wdrożone w PR #58. Pomiar lokalny: szybkość 88, dostępność 100, dobre praktyki 96, SEO 100.

### US-058 · [DEV] Nowe zrzuty w README i realistyczna historia demo (druga lista PO, pkt 1)
- **Rozmiar:** S
- **Jako** rekruter na GitHubie **chcę** zobaczyć w README najmocniejsze ekrany (Automatyzacje, „Symuluj dzień”,
  odczyt faktur AI, przebieg procesu), **aby** ocenić projekt bez uruchamiania demo.
- **Kryteria akceptacji**
  1. Cztery nowe zrzuty w `README.md` i `README.en.md`, generowane testem ścieżki rekrutera (`PW_SHOT`), więc
     odświeżenie to jedna komenda (`docs/screenshots/README.md`).
  2. Dane demo realistyczne (test `backend/tests/test_seed_demo_automation.py`): kontenery w obiegu weszły w obecny
     etap niedawno, „utworzono” = początek historii — panel przebiegu pokazuje kilka kontenerów „dłużej niż zwykle”,
     nie 120; model ML przy pewności ≥ 90% trafia w ok. 90%.
- **Stan:** wdrożone w PR #59.

### US-059 · [DEV][SEC] Włącz / wyłącz automat jednym przełącznikiem (druga lista PO, pkt 6)
- **Rozmiar:** S · **Założenie:** Z-030
- **Jako** administrator **chcę** wyłączyć automat, który w danej chwili przeszkadza (np. prognoza przy przebudowie
  magazynu), **aby** nie zmieniać konfiguracji wdrożenia ani nie prosić programisty.
- **Kryteria akceptacji** (testy `backend/tests/test_automation_switch.py`, `AutomationsPage.dom.test.tsx`)
  1. Przy automacie z harmonogramu admin widzi „Wyłącz” / „Włącz”; inne role nie widzą przycisku, API → 403.
  2. Wyłączony automat: pętla zadań go pomija (bez wpisu w dzienniku), katalog pokazuje „Wyłączony” z dopiskiem
     „przez administratora”; włączenie przywraca pracę.
  3. Każda zmiana w dzienniku zmian (było → jest, kto).
  4. Automatów chroniących dane i bezpieczeństwo (usuwanie danych kierowców, retencja, osierocone pliki, test kopii,
     strażnik) nie da się wyłączyć — brak przycisku, API → 422. Obiegów z n8n też nie (wyłącza się je w n8n).
- **[SEC]:** tylko admin; lista chroniona w kodzie (`automation_switch.LOCKED`), nie w ustawieniach.
- **Stan:** wdrożone w PR #60.

### US-060 · [DEV] Pomyłki modelu do przeglądu (druga lista PO, pkt 8)
- **Rozmiar:** S
- **Jako** kierownik logistyki **chcę** widzieć pozycje faktur, w których człowiek poprawił podpowiedź modelu,
  **aby** poprawić regułę albo kartotekę tam, gdzie model myli się najczęściej.
- **Kryteria akceptacji** (testy `test_ai_quality.py`, `AiMistakesTable.dom.test.tsx`)
  1. Panel „Odczyt faktur” pokazuje listę: kontener (link) i faktura, pozycja, podpowiedź modelu, wybór człowieka,
     pewność; najpierw pomyłki z pewnością od progu (oznaczone „automat” — tam automat ustawiłby błąd sam).
  2. Trafienia i pozycje bez decyzji nie trafiają na listę; tylko kontenery w zakresie użytkownika.
- **[SEC]:** odczyt, `scope_containers`; wpis w `tests/permissions.yaml`.
- **Stan:** wdrożone w PR #61. Przegląd bez osobnego „odhaczania”: każda poprawka i tak uczy model.

### US-061 · [DEV] Wykres przepływu procesu (druga lista PO, pkt 4)
- **Rozmiar:** S
- **Jako** kierownik logistyki **chcę** zobaczyć przepływ kontenerów między etapami na jednym obrazku, **aby** od
  razu widzieć, gdzie proces się zwęża i gdzie wraca (poprawki).
- **Kryteria akceptacji** (testy `ProcessFlowChart.dom.test.tsx`, `test_process_mining.py`, `test_seed_demo_automation.py`)
  1. Panel „Przebieg procesu”: etapy w kolejności procesu, pasmo na każde przejście (grubość ∝ liczba kontenerów),
     przejścia w przód nad osią, cofnięcia statusu pod osią innym kolorem; legenda i liczby przy pasmach.
  2. Dostępny opis bez wykresu (opis obrazka z liczbami) i lista „Najczęstsze przejścia” jako widok tabelaryczny;
     podpowiedź po najechaniu; na telefonie wykres przewija się w swoim polu, strona nie.
  3. API zwraca wszystkie przejścia; demo ma kilka realistycznych cofnięć (odprawa → port → odprawa).
- **Stan:** wdrożone w PR #62.

### US-062 · [DEV] Co jeśli statek się spóźni (druga lista PO, pkt 10)
- **Rozmiar:** S
- **Jako** planista logistyki **chcę** sprawdzić, co stanie się z magazynem, gdy statek spóźni się N dni, **aby**
  zawczasu przesunąć awizacje albo uprzedzić magazyn.
- **Kryteria akceptacji** (testy `test_what_if.py`, `WhatIfPanel.dom.test.tsx`)
  1. Ekran Automatyzacje: wybór statku (z zaplanowanymi awizacjami) i opóźnienia 1–21 dni → podsumowanie (ile
     kontenerów, nowe i znikające przekroczenia limitu) oraz tabela dni, w których zmienia się obciążenie magazynu.
  2. Lista przesuniętych kontenerów (link do kontenera, data przed → po) — tylko kontenery w zakresie użytkownika.
  3. Nic nie jest zapisywane; plan awizacji zostaje bez zmian (Z-031).
- **[SEC]:** odczyt (GET), `scope_containers`; obciążenie innych spółek tylko jako liczba; wpis w `tests/permissions.yaml`.
- **Stan:** wdrożone w PR #63.

### US-063 · [DEV] Kreator reguł z wyborem kanałów (druga lista PO, pkt 5)
- **Rozmiar:** S
- **Jako** administrator **chcę** dla każdej reguły wybrać, dokąd idzie alert — dzwonek, e-mail, karta w Teams,
  zdarzenie do n8n — **aby** np. regułę dla zespołu wysyłać tylko na kanał Teams, a regułę dla integracji tylko do n8n.
- **Kryteria akceptacji** (testy `test_automation_rules.py`, `AutomationRulesPanel.dom.test.tsx`)
  1. Przy regule pola wyboru kanałów; co najmniej jeden zostaje zaznaczony; opis reguły pokazuje wybrane kanały.
  2. Stare reguły bez wyboru działają jak dotąd (wszystkie kanały); matryca kanałów per rola dalej obowiązuje.
  3. Reguła bez dzwonka i e-maila zostawia przeczytany wpis — jedno powiadomienie na kontener i dzień nadal pilnowane.
  4. Demo: jedna przykładowa reguła tylko na e-mail i Teams.
- **[SEC]:** zmiana nadal tylko przez admina z audytem; zamknięta lista kanałów (bez wolnych adresów URL i e-mail).
- **Stan:** wdrożone w PR #64.

### US-064 · [DEV] Zero znanych błędów typów w modułach automatów (druga lista PO, pkt 13)
- **Rozmiar:** M
- **Jako** zespół **chcemy**, żeby moduły uruchamiane przez automaty (alerty, raporty, faktury w tle, kopia,
  lider pętli, monitoring, prognoza pogody) przechodziły mypy bez wyjątków, **aby** błąd typu nie wychodził
  dopiero w nocnym przebiegu.
- **Kryteria akceptacji**
  1. Lista znanych błędów mypy bez wpisów z tych modułów (189 → 145); CI blokuje nowe.
  2. Zachowanie bez zmian — poza błędem wykrytym przy okazji: weryfikacja kopii na PostgreSQL podawała do `psql`
     skompresowany plik (gzip) zamiast SQL, więc na produkcji kończyłaby się błędem; teraz dostaje rozpakowany SQL
     (test `test_verify_feeds_psql_plain_sql`).
- **Stan:** wdrożone w PR #65.

### US-026 · [DEV] Awaria integracji = czytelny komunikat, nie „błąd serwera” (trzecia lista PO, pkt 10)
- **Rozmiar:** S
- **Jako** użytkownik **chcę**, żeby awaria systemu zewnętrznego (SharePoint, paletyzacja, AIS, pogoda, kursy NBP)
  dawała zrozumiały komunikat albo „niedostępne”, **aby** reszta ekranu działała, a błąd było widać w panelu integracji.
- **Kryteria akceptacji** (test `test_integration_errors.py`)
  1. T-08 SharePoint: odpowiedź Graph w innym formacie → opis błędu w panelu integracji (bez KeyError).
  2. T-09 paletyzacja: nie-JSON albo zły typ → „Serwis paletyzacji niedostępny.” zamiast 500.
  3. T-10 AIS: ramka innego kształtu niż słownik jest pomijana, połączenie trwa.
  4. T-11 pogoda: kod błędu open-meteo → ścieżka błędu (krótki cache), nie pusta „prognoza” na 30 min.
  5. T-12 NBP: przy awarii ostatnie kursy najwyżej 5 dni po pobraniu (Z-033); starsze → bez przeliczenia.
- **[SEC]:** zamyka ryzyko R-19.
- **Stan:** wdrożone w PR #71.

### US-065 · [DEV] „Nie przypominaj” — osobiste wyciszenie alertów kontenera (trzecia lista PO, pkt 3)
- **Rozmiar:** S
- **Jako** logistyk **chcę** jednym kliknięciem w dzwonku wyciszyć alerty o kontenerze, który już załatwiam,
  **aby** nie dostawać tego samego przypomnienia codziennie.
- **Kryteria akceptacji** (testy `test_alert_mutes.py`, `notificationsBell.dom.test.tsx`)
  1. Przy powiadomieniu o kontenerze: „Nie przypominaj” → 1 / 3 / 7 dni; widać „Wyciszone do …” i „Cofnij”.
  2. Wyciszenie dotyczy tylko tej osoby i tego kontenera; inni odbiorcy dostają alert; wzmianki (@) przychodzą zawsze.
  3. Po terminie alerty wracają same; kontener spoza zakresu → 404.
- **[SEC]:** `get_scoped` przy wyciszeniu, lista tylko w zakresie (`scope_containers`), wpis w audycie; zapis
  w ustawieniach (bez migracji bazy).
- **Stan:** zrealizowane, czeka na merge.

### US-066 · [DEV][SEC] Historia zmian reguł i „przywróć” (trzecia lista PO, pkt 4)
- **Rozmiar:** S
- **Jako** administrator **chcę** widzieć, kto i kiedy zmienił regułę z kreatora, i jednym kliknięciem cofnąć
  zmianę, **aby** błędna edycja nie wysyłała alertów do niewłaściwych osób.
- **Kryteria akceptacji** (testy `test_automation_rules_history.py`, `AutomationRulesHistory.dom.test.tsx`)
  1. Panel reguł → „Historia zmian reguł”: data, osoba, dodano / zmieniono (które pola) / usunięto.
  2. „Przywróć stan sprzed tej zmiany” (admin, z potwierdzeniem) dotyczy jednej reguły; reszta listy bez zmian.
  3. Przywrócenie też trafia do historii („przywrócono stan sprzed zmiany #…”).
- **[SEC]:** historia z dziennika zmian (bez nowej tabeli); przywraca tylko admin; logistyka tylko czyta.
- **Stan:** zrealizowane, czeka na merge.

## Could

- **US-020** [DEV] Jedna reguła „ETA + N” i przeliczanie propozycji po zmianie ETA (P-02, P-03; D2).
- **US-021** [DEV] Spłata długu modelu danych: UNIQUE w `AvizoItem`/`DeliveryConfirmation`, CHECK dla statusów
  tekstowych, decyzja o dwóch statusach odprawy (`04-model-danych.md` §„Znane niespójności”).
- **US-022** [DEV] Ponawianie maili SMTP i rejestrowanie błędów zdarzeń n8n (P-11, P-12).
- **US-023** [BA] Wymagania FR-1xx dla modułów pobocznych — tylko dla modułów, które PO uzna za *Must* (Z-005).
- **US-024** [DEV] Archiwizacja `docs/pomysly-automatyzacje*.md` (340 KB) poza główną mapą dokumentacji.
- **US-025** [SEC] Pełna weryfikacja ASVS L2 wymaganie po wymaganiu (`CHECKLISTA_ASVS.md` to ocena wstępna).

## Won't (na teraz)

- Skalowanie poziome (Redis dla limiterów) — kontrakt jednej instancji wystarcza dla skali 200 kontenerów/mies.
- CodeQL — koszt minut Actions; Semgrep w US-007 pokrywa potrzebę SAST semantycznego.
- Tracking kontenerów u armatora — decyzja D10 (powrót w kolejnym etapie).
- „Pola obowiązkowe per spółka” z wywiadu — do decyzji PO (Z-018).
