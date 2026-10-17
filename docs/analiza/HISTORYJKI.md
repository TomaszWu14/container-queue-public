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
- **Jako** administrator **chcę**, aby link wywołań palet (DLT) i wolne sloty awizacji miały ten sam limit
  żądań, kontrolę pochodzenia i walidację parametrów co formularz awizacji, **aby** żadna publiczna trasa nie
  była słabszym ogniwem.
- **Kryteria akceptacji**
  - Dane: > 30 żądań/min z jednego IP na `/api/dlt/{token}` → Gdy kolejne → Wtedy 429 z `Retry-After`.
  - Dane: żądanie POST z obcym `Origin` → Gdy wysyłka → Wtedy 403.
  - Dane: `GET /api/avizo/{token}/slots` z datą poza zakresem ważności linku ± 30 dni → Gdy żądanie → Wtedy 422.
- **Test:** `test_public_routes_guard.py`, `test_dlt_confirm.py`, `test_avizo_slots.py`.
- **Stan:** zrealizowane (PR po #29); czeka na merge. Ochrona w jednym miejscu: `app/public_guards.py`
  (awizacja i DLT); link DLT dostał też nagłówki `no-referrer` / `noindex`.

### US-006 · [SEC] Bezpieczne parsowanie XML i archiwów ZIP
- **Rozmiar:** S · **Źródło:** R-07, T-06 · **Wymagania:** SR-006
- **Jako** administrator **chcę**, aby XML (SAD) parsował `defusedxml`, a limit ZIP liczył się z faktycznie
  rozpakowanych bajtów, **aby** spreparowany plik nie zatrzymał całej aplikacji.
- **Kryteria akceptacji**
  - Dane: XML z DTD/encjami zewnętrznymi albo „billion laughs” → Gdy import SAD → Wtedy 422, proces żyje.
  - Dane: ZIP deklarujący 1 MB, rozpakowujący się do 2 GB → Gdy upload archiwum → Wtedy 413 po przekroczeniu
    `MAX_UPLOAD_MB` w trakcie rozpakowywania; współczynnik kompresji > 100 odrzucony.
- **Test:** `test_imports_malicious.py`, `test_sad_xml.py`, `test_archive_upload.py`.
- **Stan:** zrealizowane (PR po #29); czeka na merge. Rozpoznanie: XML był już chroniony odrzuceniem DTD
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
- **Stan (2026-10-17):** częściowo — PR po #32. Trivy: bramka na PR (fs, HIGH/CRITICAL z poprawką) i w cotygodniowym
  skanie obrazu; `.trivyignore` z formatem wyjątków; obraz panelu z jawnym `USER 101` (jedyne znalezisko Trivy).
  pre-commit: Bandit 1.9.4, gitleaks 8.30.1, ruff 0.17.0 jak CI (test `test_runtime_versions.py`). **Semgrep** na razie
  raport (SARIF) — reguł p/owasp-top-ten nie da się pobrać w środowisku pracy, więc bramka po przejrzeniu pierwszego
  raportu z CI.

### US-008 · [SEC] `csv_safe` neutralizuje tabulator i powrót karetki
- **Rozmiar:** XS · **Źródło:** B-002 · **Wymagania:** SR-006
- Dane: wartość `\t=1+1` albo `\r=cmd` w eksporcie CSV → Gdy pobranie → Wtedy pole poprzedzone apostrofem,
  jak dla `= + - @`. **Test:** parametryzowany test `csv_safe` na wszystkie prefiksy OWASP.

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
    w loginie (logistyka, spedytor, agencja celna, magazyn DLT), to samo hasło `DEMO_PASSWORD`.
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
  8. Wywołania DLT (linki publiczne dla partnera): ukryte, API 403. Linki awizacji nie są odczytywalne
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
- **Stan:** zrealizowane (PR po #31); czeka na merge. `tests/test_isolation_guard.py`: 226 tras z identyfikatorem,
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
- **Stan:** zrealizowane (PR po #30); czeka na merge. Decyzja [DEV]: wersje produkcji — **Python 3.14, Node 26**
  (obraz już na nich działał, a CI testowało 3.12 i 24). CI i README przełączone; lock zostaje „universal” od 3.12
  (lokalnie da się pracować na 3.12+). Sprawdzone przed zmianą na 3.14 / 26: backend 2223 testów, mypy bez nowych
  błędów, frontend 1013 testów i build, e2e demo 6/6. Strażnik: `backend/tests/test_runtime_versions.py`.

### US-016 · [BA][DEV] Dane dla Portugalii: prefiks telefonu i kraj magazynu
- **Rozmiar:** S · **Źródło:** P-05, P-06 · **Wymagania:** FR-017
- **Stan:** zrealizowane (PR #29); czeka na merge. Założenie Z-022 do potwierdzenia.
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
- **Stan:** zrealizowane (PR po #30); czeka na merge. `AuthPages.dom.test.tsx` (7), `ClearQueueModal.dom.test.tsx` (3),
  `ImportModal.dom.test.tsx` (4); lista stron bez testu w `docs/testy/E2E.md` odświeżona (21 → 16).

### US-019 · [SEC] 2FA obowiązkowe dla administratorów na produkcji
- **Rozmiar:** XS (konfiguracja) · **Źródło:** E-01 · **Zależy od:** decyzji PO (Z-008).
- `REQUIRE_2FA_ADMIN=true` w Coolify po tym, jak każdy admin włączy 2FA; procedura w RUNBOOK.

## Could

- **US-020** [DEV] Jedna reguła „ETA + N” i przeliczanie propozycji po zmianie ETA (P-02, P-03; D2).
- **US-021** [DEV] Spłata długu modelu danych: UNIQUE w `AvizoItem`/`DeliveryConfirmation`, CHECK dla statusów
  tekstowych, decyzja o dwóch statusach odprawy (`04-model-danych.md` §„Znane niespójności”).
- **US-022** [DEV] Ponawianie maili SMTP i rejestrowanie błędów zdarzeń n8n (P-11, P-12).
- **US-023** [BA] Wymagania FR-1xx dla modułów pobocznych — tylko dla modułów, które PO uzna za *Must* (Z-005).
- **US-024** [DEV] Archiwizacja `docs/pomysly-automatyzacje*.md` (340 KB) poza główną mapą dokumentacji.
- **US-025** [SEC] Pełna weryfikacja ASVS L2 wymaganie po wymaganiu (`CHECKLISTA_ASVS.md` to ocena wstępna).
- **US-026** [DEV] Obsługa nieoczekiwanych odpowiedzi integracji (T-08…T-12): 502/503 z komunikatem zamiast 500.

## Won't (na teraz)

- Skalowanie poziome (Redis dla limiterów) — kontrakt jednej instancji wystarcza dla skali 200 kontenerów/mies.
- CodeQL — koszt minut Actions; Semgrep w US-007 pokrywa potrzebę SAST semantycznego.
- Tracking kontenerów u armatora — decyzja D10 (powrót w kolejnym etapie).
- „Pola obowiązkowe per spółka” z wywiadu — do decyzji PO (Z-018).
