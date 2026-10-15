# Audyt repozytorium — stan na 2026-10-15

**Commit:** `3373194` (`main`) · **Perspektywy:** [BA] analityk biznesowy, [DEV] developer, [SEC] bezpieczeństwo ·
**Adresat:** Product Owner (PO) · **Status dokumentu:** wersja 1, otwarcie procesu zespołowego (krok 1 z „Start pracy”).

**Metoda.** Lektura repozytorium (kod, testy, CI, 113 plików w `docs/`), uruchomienie narzędzi jakości
i bezpieczeństwa na świeżym klonie (załącznik A) oraz sprawdzenie w kodzie każdego twierdzenia z istniejących
dokumentów, które audyt cytuje. Kodu nie zmieniano. Tam, gdzie dokument i kod się różnią, wygrywa kod —
rozbieżności zebrano w §4.

**Jak czytać.** §0 to streszczenie dla PO. §1–§3 to trzy perspektywy. §5 porównuje repozytorium ze strukturą
docelową procesu zespołowego. §6 to kandydaci do backlogu, §7 — pierwsza seria pytań do PO. Dalsze kroki
(szkielet struktury, backlog) ruszają **po odpowiedziach PO**; do tego czasu nic z §6 nie jest zaplanowane.

---

## 0. Streszczenie dla PO

**[BA]**
1. Aplikacja zastępuje arkusz kolejki kontenerów dla grupy spółek importujących (ok. 200 kontenerów/mies.,
   4 spółki, 2 magazyny, 3 spedytorów, agencja celna) i jest w fazie testów z użytkownikami.
2. Rdzeń procesu ma dobrą dokumentację analityczną (`docs/01–07`): 28 wymagań z kryteriami i testami, 12 decyzji,
   rejestr reguł. Brakuje: wymagań niefunkcjonalnych, backlogu z priorytetami, słownika, wymagań dla 10 modułów
   pobocznych i pomiaru mierników sukcesu (30 h/tydzień).
3. 14 znanych problemów użytkowych (P-01…P-14) czeka na decyzję, w tym fałszywy komunikat sukcesu przy
   odpowiedzi spedytora (P-01).

**[DEV]**
4. Jakość techniczna jest wysoka i **zautomatyzowana**: lint, typy z baseline, pokrycie ≥ 92 %, limit 500 linii/plik,
   macierz uprawnień rola × trasa, migracje testowane na PostgreSQL. Dziś wszystko zielone: 2112 testów backendu,
   964 frontendu, 0 błędów lintu/typów.
5. Dług techniczny jest **znany i spisany** (39 niespójności modelu, 191 znanych błędów mypy, kontrakt „jedna
   instancja”), ale nie ma planu jego spłaty ani właściciela.
6. Repozytorium publiczne to oczyszczona kopia prywatnego: brakuje 5 plików workflow/konfiguracji, do których
   odwołują się dokumenty, a odwołania do PR-ów (#796, #885…) prowadzą donikąd. Nie ma CHANGELOG-u, wersja `0.1.0`
   nigdy nie była podnoszona.

**[SEC]**
7. Skany na dziś: Bandit 0, pip-audit 0, npm audit 0, gitleaks 0 (pełna historia). Kontrole aplikacji spełniają
   minimum z §6 procesu (nagłówki, CSRF, limity, bcrypt, 2FA, retencje, audyt).
8. Najwyższe ryzyka (§3.4): izolacja spółek wyłącznie w kodzie (R-01), ciche nadpisanie przy równoczesnej
   edycji (R-02), załączniki sprawdzane tylko po rozszerzeniu (R-03), produkcja bez `DATABASE_URL` startuje na
   SQLite (R-04), jeden sekret do JWT i szyfrowania (R-05). RODO: mechanizmy są, dokumentacja (rejestr czynności,
   podstawy, klasyfikacja) — nie.

**Decyzje, których potrzebujemy od PO:** §7 (5 pytań).

---

## 1. [BA] Co aplikacja robi i czego brakuje w wymaganiach

### 1.1 Produkt

System planowania dostaw kontenerów importowych: jeden wspólny stan kontenera — od zamówienia, przez statek
i odprawę celną, po rozładunek — z historią każdej zmiany i separacją danych między spółkami oraz partnerami.
Zastąpił arkusz Excel rozsyłany mailem, który kosztował 4 osoby ok. 30 h tygodniowo (`docs/01-problem-i-zakres.md`).
Wdrożenie: Docker + Coolify, jedna instancja; panel w trzech językach (PL/EN/PT). Publiczna instancja demo
tylko do odczytu (konto `demo`).

### 1.2 Interesariusze i role

| Interesariusz | Rola w systemie | Zakres widoczności (z `deps.py`) |
|---|---|---|
| Logistyka spółki / grupy | `logistics` (+ flaga „wszystkie spółki”) | własna spółka; opcjonalnie lista magazynów |
| Magazyn (własny, zewnętrzny DLT) | `warehouse` | tylko swój magazyn; potwierdza wyłącznie rozładunek |
| Spedytor | `forwarder` albo jednorazowy link | tylko kontenery mu zlecone; bez danych odprawy |
| Agencja celna | `customs` | tylko kontenery z zleconą odprawą |
| Zakupy | `purchasing` | własna spółka |
| Sprzedaż | `sales` | tylko odczyt, bez kosztów |
| Administrator | `admin` | wszystko; konta, słowniki, audyt |
| Kierowca | brak konta | dane osobowe w awizacji (RODO) |
| Automatyzacje (n8n) | konto serwisowe z tokenem | rola konta serwisowego (nie admin) |

### 1.3 Zakres

- **Rdzeń (udokumentowany w 01–07):** kolejka, cykl kontenera (10 statusów), odprawa (9 statusów), dokumenty
  dostawy, plan i awizacja (dwuetapowe linki), rozładunek, separacja danych, historia zmian, import z Excela.
- **Moduły poboczne (zaimplementowane, opisane tylko technicznie w `TECHNICZNE.md`):** wyceny transportu (RFQ)
  i zlecenia, śledzenie statków (AIS), powiadomienia (e-mail/Teams/SMS), faktury i import SAD, reklamacje,
  wywołania palet (DLT, Power BI), kartoteka dostawców, analityka, baza wiedzy, asystent (lokalny LLM),
  poczekalnia dokumentów.
- **Świadomie poza zakresem:** zapis do SAP, tracking u armatora (planowany powrót), twarde blokady statusów,
  publiczne linki dla klienta/kierowcy (usunięte 2026-10-07).

### 1.4 Stan wymagań — co jest

| Artefakt | Zawartość | Ocena |
|---|---|---|
| `docs/05-wymagania.md` | 28 wymagań W-01…W-28 rdzenia: kryterium (Dane/Gdy/Wtedy), miejsce w kodzie, test | dobra baza; odtworzone z kodu, nie z potrzeb |
| `docs/SPECYFIKACJA.md` | zapis wywiadu (50 pytań, 02.07.2026) | źródło pierwotne; częściowo nieaktualne (§3 sloty) |
| `docs/REGULY-PROCESU.md` | ~40 reguł biznesowych z datą decyzji i odwołaniem do audytu | wzorowy rejestr reguł |
| `docs/06-decyzje.md` | 12 decyzji D1–D12 w formacie kontekst/opcje/wybór/skutki | de facto ADR-y w jednym pliku |
| `docs/02-proces.md`, `bpmn/`, `mapa-procesow-*` | AS-IS/TO-BE, aktorzy, diagramy Mermaid i BPMN | jest; starsze mapy niezgodne z kodem (07) |
| `docs/superpowers/` | 38 specyfikacji i 34 plany funkcji | archiwum uzasadnień |
| `tests/permissions.yaml`, `tests/ui-permissions.yaml` | macierz rola × trasa (API) i rola × ekran (UI) | wykonywalne wymagania autoryzacji |

### 1.5 Czego brakuje w wymaganiach

1. **Wymagania niefunkcjonalne** nie istnieją jako lista: wydajność (kolejka ~1 MB JSON, gzip), dostępność
   (jedna instancja, RPO 7 dni z decyzji o backupie), użyteczność (audyty UX), RODO (retencje) — wszystko jest
   rozproszone po `config.py`, `REGULY-PROCESU.md`, `JEDNA-INSTANCJA.md`.
2. **Moduły poboczne bez wymagań z identyfikatorami** (faktury/SAD, reklamacje, wyceny, palety, analityka,
   baza wiedzy, asystent). Ich reguły żyją w komentarzach kodu i specyfikacjach `superpowers/`.
3. **Backlog**: brak historyjek z priorytetami (MoSCoW). W repozytorium publicznym 0 issues; `07-ograniczenia.md`
   §„Co dalej” wymienia 3 punkty bez priorytetu.
4. **Słownik pojęć**: terminy (awizacja, demurrage, tranzyt, DLT, draft SAD, PAZ, REF, kafelek dokumentu) nie mają
   jednego miejsca; część ma po 2 nazwy (np. „otwarty w kolejce” vs „fizycznie zakończony” — BIZ-004).
5. **Macierz śledzenia** jest tylko dla rdzenia i tylko do poziomu testu (wymaganie → kod → test); brak kolumn
   historyjka i PR. Odwołania do PR-ów w dokumentach wskazują prywatne repozytorium.
6. **Wymaganie z wywiadu nierealizowane:** „pola obowiązkowe konfigurowane per spółka” (SPECYFIKACJA §2) — brak
   konfiguracji, wymagany tylko numer kontenera. Wymaga decyzji PO: realizować czy wykreślić.
7. **Luki w kryteriach akceptacji zgłoszone przez samą dokumentację:** W-07 — brak testu na 403 dla spedytora
   zmieniającego status odprawy.

### 1.6 Znane problemy z perspektywy użytkownika

Z `docs/07-ograniczenia.md` (zweryfikowane w kodzie, nadal aktualne). Najbardziej dotkliwe:

| # | Problem | Skutek dla użytkownika |
|---|---|---|
| P-01 | Odpowiedź na awizację w aplikacji pokazuje sukces przy błędzie 409 | spedytor myśli, że odpowiedział; nic nie zapisano |
| P-13 / B-004 | Edycje równoległe bez kontroli wersji | ostatni zapis nadpisuje poprzedni bez ostrzeżenia |
| P-05 | 9-cyfrowy numer kierowcy zawsze z prefiksem +48 | SMS do kierowcy portugalskiego nie dochodzi |
| P-06 | Nowe magazyny zawsze z krajem PL | magazyn w Portugalii dostaje polskie święta |
| P-09 | „Wyślij plan do spedycji” nie wysyła maila, tylko zmienia status | spedytor dowiaduje się dopiero z aplikacji |
| P-02/P-03 | Dwie reguły „ETA + N” (4 i 3 dni); zmiana ETA nie przelicza propozycji | dwie różne daty dla tej samej sytuacji |
| P-12 | Maile SMTP bez ponawiania; bez serwera pomijane po cichu | utracone powiadomienia |

UX: audyt heurystyczny (`UX_AUDIT.md`, zamrożony, większość wdrożona) i `audyt-nielsen-kolejka.md`;
21 modułów stron bez testu (`docs/testy/E2E.md`), w tym import Excela i operacja masowa czyszczenia kolejki.

### 1.7 Mierniki sukcesu

Zdefiniowane w `01`: 30 h/tydzień na arkusz, 214 kontenerów w migracji. **Nie ma pomiaru po wdrożeniu**
(czas pracy, liczba kontenerów w aplikacji vs w Excelu, liczba użytkowników aktywnych, błędy numerów ISO
zatrzymane walidacją). Rejestr `job_runs`/`audit_log` pozwoliłby je policzyć — to pytanie do PO (§7).

---

## 2. [DEV] Jakość kodu, testy, architektura, dług techniczny

### 2.1 Rozmiar i struktura

| Obszar | Wartość |
|---|---|
| Backend `app/` | 39 970 linii Python w 247 plikach; 81 modułów routerów, ok. 450 tras HTTP |
| Backend testy | 34 342 linii w 348 plikach; 2112 testów (pytest, SQLite per worker) |
| Migracje Alembic | 121 plików, 5 810 linii; 106 tabel |
| Frontend `src/` | 40 284 linii TS/TSX (bez testów); 96 plików stron; 98 plików i18n per funkcja |
| Frontend testy | 14 745 linii w 238 plikach; 964 testów (vitest) + 16 E2E (Playwright) |
| Dokumentacja | 113 plików Markdown w `docs/` (+ README, SECURITY, BUGS-FOUND, UX_AUDIT, CLAUDE) |
| Historia (repo publiczne) | 18 commitów, 1 autor, 2026-10-08 → 2026-10-13; 17 PR-ów (docs/demo) |

Stos: Python 3.12 + FastAPI + SQLAlchemy 2 + Alembic + PostgreSQL 16 (SQLite lokalnie i w testach);
React 19 + TypeScript 7 + Vite 8 + Tailwind 4; Docker (jeden obraz: API serwuje zbudowany panel) + Coolify.
Opis: `docs/ARCHITEKTURA.md` (diagram Mermaid, integracje), `docs/04-model-danych.md` (ERD rdzenia).

### 2.2 Architektura — cechy istotne dla dalszych prac

- **Monolit z jednym procesem.** Pętle tła (kilkanaście zadań: alerty, digesty, SMS, AIS, retencje, backup
  verify) działają w procesie API; przy `WEB_CONCURRENCY>1` jeden lider na advisory locku PostgreSQL. Limiter
  żądań API i część stanu są w pamięci procesu (`docs/JEDNA-INSTANCJA.md`). Skalowanie poziome wymaga Redis
  lub równoważnika — świadomie odłożone.
- **Izolacja danych w jednym miejscu** (`deps.py`: `scope_*`, `get_scoped`, `check_container_access`) — decyzja D9.
  Baza nie wymusza spójności `company_id` między tabelami. To zarazem największa zaleta (testowalność) i największe
  ryzyko (§3.4 R-01).
- **Ciężkie przetwarzanie w procesie API:** OCR (Tesseract), ekstrakcja PDF (pdfminer/pdfplumber), ML
  (scikit-learn), pakowanie 3D. Część przeniesiona do tła (`invoice_ocr_in_background`), limity pamięci
  w compose (`APP_MEM_LIMIT`), `oom_score_adj`.
- **Integracje włączane konfiguracją** (puste zmienne = wyłączone): M365 Graph, SharePoint, SMSAPI, AIS, Ollama,
  n8n, Power BI, Teams, Sentry, NBP, Open-Meteo. Ok. 120 zmiennych w `config.py`, każda udokumentowana
  (`ZMIENNE-SRODOWISKOWE.md`, test `test_env_docs.py` pilnuje kompletności).
- **Wersjonowanie:** `0.1.0` w `main.py` i `package.json` od początku; identyfikacja wdrożenia przez SHA commita
  (`APP_VERSION`). Brak tagów, wydań i CHANGELOG-u.

### 2.3 Bramki jakości — stan i wynik dzisiejszego uruchomienia

| Bramka | Konfiguracja | Wynik 2026-10-15 |
|---|---|---|
| ruff | `E F W I B UP BLE C90 PIE`, złożoność ≤ 20, wyjątki uzasadnione w `pyproject.toml` | 0 błędów |
| mypy | baseline znanych błędów (może tylko maleć), `scripts/mypy_baseline.py` | 0 nowych, 191 znanych (78× `arg-type`) |
| Limit 500 linii/plik | `scripts/check_file_lengths.py`, 2 pliki w `BASELINE` | OK |
| Pokrycie backendu | `fail_under = 92` (linie), tylko w CI | nie mierzono lokalnie (w CI 92,6 % na 2026-09-28) |
| pytest | `-n auto`, SQLite per worker, 20 min timeout | 2112 passed, 2 skipped, 2:17 na 4 rdzeniach |
| ESLint | typescript-eslint + react-hooks, osobny pakiet `tools/eslint` | 0 błędów, 12 ostrzeżeń w 5 plikach z listy `LEGACY_WARN` |
| TypeScript | `tsc -b --noEmit` (TS 7) | 0 błędów |
| vitest | 238 plików | 964 passed, 3:07 |
| Macierz uprawnień | `test_permissions_matrix.py` vs `tests/permissions.yaml` | przechodzi |
| Trasy bez logowania | `test_routes_require_auth.py` (lista `PUBLIC` jawna) | przechodzi |
| Zgodność env ↔ docs | `test_env_docs.py`, `test_env_example.py` | przechodzi |
| Lock zależności | `test_dependency_lock.py`, `--require-hashes` | przechodzi |

### 2.4 Testy — ocena

**Mocne strony:** reguły procesu mają testy wskazane w `05-wymagania.md`; testy bezpieczeństwa istnieją jako
klasa (`test_idor_*`, `test_isolation`, `test_csrf`, `test_security_headers`, `test_login_limiter_db`,
`test_upload_limits`, `test_gdpr_*`, `test_w14_security`); strażnicy spójności (trasy, env, lock, długość
plików, snapshot świąt, ścieżki `/api` z frontu); migracje od zera na PostgreSQL 16 z kontrolą dryfu enumów
i schematu (`db_drift_baseline.txt` pusty od 2026-09-28).

**Luki:**
1. E2E (Playwright, 16 testów, 2 role) nie biegnie w CI publicznego repo — `e2e.yml` nie istnieje tutaj,
   `docs/testy/E2E.md` opisuje bieg nocny na runnerze self-hosted prywatnego repo.
2. 21 modułów stron bez testu jednostkowego (lista w `docs/testy/E2E.md`), w tym `ImportModal`,
   `ClearQueueModal`, reset hasła.
3. Brak testów współbieżności (B-004) i testów obciążeniowych (R11 z `ETAP-0-PLAN.md`).
4. Pokrycie liczone tylko liniowo i tylko w CI; brak progu dla frontendu.
5. Plan systemu testów regresji (`docs/testy/ETAP-0-PLAN.md`, 6 etapów) — nie wiadomo, które etapy wykonano:
   testy potwierdzające z `BUGS-FOUND.md` (`test_exports_formula_injection.py`, `test_imports_malicious.py`,
   `test_concurrency.py`, `test_config_failfast.py`) nie istnieją, a sam rejestr nie był aktualizowany po naprawach (§4).

### 2.5 CI/CD

| Workflow | Co robi | Kiedy | Uwagi |
|---|---|---|---|
| `ci-backend.yml` | długość plików, ruff, mypy baseline, pytest z pokryciem | PR do `main` ruszający backend; push do `main` | drafty pomijane (oszczędność minut) |
| `ci-frontend.yml` | długość plików, ESLint, vitest, build, test ścieżek `/api` | PR ruszający frontend | j.w. |
| `ci-migrations.yml` | `alembic upgrade head` na PG 16, dryf enumów i schematu, `downgrade -1` | PR ruszający modele/migracje | wzorowe |
| `ci-infra.yml` | pip-audit, npm audit (`--audit-level=high`), `docker build` | PR ruszający zależności/Dockerfile; co tydzień | — |
| `security.yml` | gitleaks (commity PR-a; co tydzień cała historia), Bandit; Trivy fs + SBOM + skan obrazu | każdy PR; co tydzień | Trivy nie bramkuje (`--exit-code 0`) |

Dobre praktyki: akcje przypięte do SHA, obrazy bazowe przypięte digestem, `pip --require-hashes`, `permissions:
contents: read`, concurrency z osobną grupą dla draftów. **Brakuje w tym repozytorium:** `automerge.yml` (bramka
„CI OK”), `dependabot.yml`, `e2e.yml`, `claude*.yml` — wszystkie cytowane w `SECURITY.md`, `docs/testy/E2E.md`,
`docs/CLAUDE-GITHUB.md`, `CLAUDE.md`. Wdrożenie: ręczny Redeploy w Coolify (merge niczego nie wdraża),
`scripts/smoke.sh` po wdrożeniu. Brak środowiska staging (instancja demo pełni rolę pokazową, nie testową).

### 2.6 Dług techniczny (uporządkowany wg kosztu utrzymania)

1. **Model danych** — 39 niespójności (`04-model-danych.md` §„Znane niespójności”, pokazanych 9): dwa statusy
   odprawy (`customs_status` + słownikowy `customs_case_status_id`), stan dokumentów w 3 polach, powiązanie
   zamówienie ↔ kontener na 4 sposoby, dwa modele zlecenia transportu, brak UNIQUE w `AvizoItem`/
   `DeliveryConfirmation`, statusy tekstowe bez CHECK, pole `proposed_delivery_date` nieużywane (D1).
2. **Brak kontroli wersji rekordów** (optimistic locking) — B-004/P-13; dotyka każdej edycji.
3. **Znane błędy typów:** 191 w baseline mypy; 5 plików frontendu z regułami hooków tylko ostrzegającymi.
4. **Niezgodność wersji środowisk:** CI Python 3.12, obraz `python:3.14-slim`, README „3.12–3.14”, lock
   kompilowany dla 3.12; Node: README 22.12+, CI 24, obraz `node:26`. Lokalnie na 3.13 `py3dbp`/
   `red-black-tree-mod` nie budują się z sdist (audyt użył 3.12). Jedna wersja = mniej niespodzianek.
5. **Dokumentacja dwuwarstwowa:** świeże `01–07` + starsze opisy modułów, część niezgodna z kodem (lista w `07`);
   `CLAUDE.md`/`ONBOARDING-DEV.md` odsyłają do nieistniejącego `graphify-out/`.
6. **Jedna instancja i stan w pamięci** (limiter API, wynik ostatniej integracji) — kontrakt opisany, bez planu
   wyjścia.
7. **Obsługa integracji zewnętrznych:** T-08…T-12 (SharePoint, serwis paletyzacji, AIS, pogoda, NBP) — odpowiedź
   w nieoczekiwanym formacie kończy się 500.
8. **Pliki `pomysly-automatyzacje*.md`** (340 KB) w `docs/` — szum dla czytelnika; kandydat do archiwum.

### 2.7 Dokumentacja — ocena

Pod względem objętości i struktury wyróżnia się na tle typowego projektu: mapa (`docs/README.md`), dokumenty
analityczne z odwołaniami do linii kodu, rejestr reguł z datami, katalog zmiennych z testem kompletności,
onboarding „w 30 minut”. Słabości: rozbieżności z kodem (§4), duplikaty (README ↔ TECHNICZNE ↔ ONBOARDING),
brak CHANGELOG/CONTRIBUTING, brak statycznego opisu API (OpenAPI tylko poza produkcją).

---

## 3. [SEC] Najważniejsze ryzyka

### 3.1 Kontrole istniejące (zweryfikowane w kodzie, nie tylko w dokumentach)

| Obszar (ASVS/OWASP) | Kontrola | Gdzie |
|---|---|---|
| Uwierzytelnianie | bcrypt (12 rund na prod, fail-fast poniżej), polityka haseł (12 znaków, litera+cyfra), JWT HS256 w cookie `HttpOnly`+`SameSite=Lax` (+`Secure` przy HTTPS), access 2 h, refresh 14 dni z rotacją i wykryciem ponownego użycia, `session_version` unieważnia sesje, 2FA TOTP + kody zapasowe (hash), stały czas odpowiedzi dla nieistniejącego loginu | `security.py`, `routers/auth.py` |
| Brute force | limity per IP+login, per IP, per konto z progresywną przerwą — **stan w bazie** (`login_failures`), lista zablokowanych IP, globalny limit API/IP (w pamięci) | `rate_limit.py` |
| Autoryzacja | RBAC 7 ról + izolacja per zasób w jednym module; 404 zamiast 403 dla cudzych rekordów; macierz rola × trasa w testach; tryb „podgląd jako rola” tylko GET; konto serwisowe n8n nie może być adminem | `deps.py`, `tests/permissions.yaml`, `automation_policy.py` |
| CSRF | zapis z cookie wymaga `X-Requested-With` albo `Origin`/`Referer` = adres aplikacji | `csrf.py`, `frontend/src/csrf.ts` |
| Nagłówki | CSP (`default-src 'self'`, jeden inline skrypt po hashu), `X-Frame-Options: DENY`, `nosniff`, `Referrer-Policy`, `Permissions-Policy`, COOP; HSTS za HTTPS; `no-referrer` + `noindex` dla linków z tokenem; te same w nginx (test zgodności) | `main.py`, `frontend/nginx.conf` |
| Walidacja wejścia | Pydantic v2 na API; ISO 6346; ORM bez surowego SQL z danymi użytkownika (f-stringi tylko ze stałymi identyfikatorami, `nosec` z uzasadnieniem); Jinja2 z autoescape dla maili i pism; neutralizacja formuł w XLSX (`append_row`) i CSV | `schemas/`, `exports.py`, `html_templates.py` |
| Pliki | limit `MAX_UPLOAD_MB` na wszystkich trasach (ok. 50 wywołań `read_upload_capped`), sygnatury bajtów dla zdjęć/awatarów, lista rozszerzeń dla załączników, limit stron PDF, limit plików w ZIP, upload poza katalogiem publicznym (`/data/uploads`) | `routers/forwarding_files.py`, `archive_upload.py` |
| Linki publiczne | tylko awizacja i wywołania palet; token 16+ znaków, w bazie SHA-256, jednorazowy, ważność 7/5 dni i twardy limit 90 dni; maskowanie tokenów w logach i Sentry | `avizo_workflow.py`, `public_links.py`, `redaction.py` |
| Sekrety i konfiguracja | tylko env; `.env.example` bez wartości (test); fail-fast na prod: domyślne sekrety, `SECRET_KEY` < 32, brak `PUBLIC_BASE_URL`, `SECURE_COOKIES=false` (chyba że jawne `ALLOW_INSECURE_HTTP`); `/docs` wyłączone na prod; XFF tylko od zaufanych proxy | `main.py::validate_settings`, `config.py` |
| Logowanie i audyt | `audit_log` każdej zmiany pola (kto/kiedy/było/jest), logowania z IP, maskowanie danych kierowcy w audycie, `X-Request-ID`, Sentry ze scrubbingiem PII | `audit.py`, `applog.py`, `redaction.py` |
| RODO | retencje: dane kierowców 90 dni (+ kopie w powiadomieniach i SMS), log logowań 90 dni, tokeny 30 dni, SMS 90 dni, błędy JS 30 dni, powiadomienia 90 dni; eksport danych osoby (art. 15) i anonimizacja (art. 17); usunięcie konta = anonimizacja | `retention.py`, `data_subject.py`, `avizo_workflow.py` |
| AI/LLM | model lokalny (Ollama) tylko pod adresem wewnętrznym, odpowiedź budowana z faktów z bazy po izolacji roli, pola ukryte dla roli nie trafiają do promptu, limit pytań/min, metryki bez treści | `llm.py`, `routers/assistant.py` |
| Kontenery | użytkownik nie-root (uid 1000), obrazy bazowe przypięte digestem, `init: true`, limity RAM/CPU, HEALTHCHECK ze strażnikiem zawieszenia, rotacja logów Dockera, brak `/proc` hosta | `Dockerfile.coolify`, `docker-compose.coolify.yml` |
| Łańcuch dostaw | `pip --require-hashes`, akcje GitHub po SHA, gitleaks + Bandit bramkują PR, pip-audit/npm audit przy zmianie zależności, Trivy + SBOM co tydzień | `.github/workflows/`, `backend/requirements*.txt` |
| Kopie zapasowe | `pg_dump` + archiwum załączników, retencja GFS, szyfrowanie `age`, cotygodniowa weryfikacja odtworzenia | `backend/scripts/backup.sh`, `verify_backup.py` |

### 3.2 Wyniki narzędzi uruchomionych dziś

| Narzędzie | Zakres | Wynik |
|---|---|---|
| Bandit 1.9.4 (`-c pyproject.toml`) | `backend/app` | 0 ustaleń; 14 adnotacji `nosec`, każda z uzasadnieniem w linii |
| pip-audit 2.x | `requirements.txt`, `requirements-dev.txt` | 0 znanych podatności |
| npm audit (`--audit-level=high`) | `frontend/package-lock.json` | 0 podatności |
| gitleaks 8.30.1 | cała historia repo publicznego (9,7 MB) | 0 wycieków |
| ruff / mypy / tsc / ESLint | jak w §2.3 | 0 błędów |
| Trivy, Semgrep, CodeQL | — | **nie uruchomiono** (Trivy i Semgrep: brak w środowisku audytu — w CI Trivy działa co tydzień; CodeQL: nieskonfigurowany) |

### 3.3 Klasyfikacja danych (wstępna, do `KLASYFIKACJA_DANYCH.md`)

| Klasa | Dane | Gdzie |
|---|---|---|
| **Dane osobowe** | użytkownicy (login, e-mail, imię, IP logowań, sekret TOTP), **kierowcy** (imię, telefon, nr dokumentu, nr auta/naczepy — bez konta, przekazywane przez spedytora), kontakty w słownikach (spedytorzy, agencje, dostawcy) | `users`, `containers.driver_*`, `sms_messages`, `audit_log`, słowniki |
| **Poufne (handlowe)** | ceny i wyceny transportu, faktury (CIPL) i ich pozycje, draft SAD, zamówienia SAP (EKKO), dane klientów i wartości towaru, stany magazynowe DLT | `quotes`, `invoices`, `sad_drafts`, `sap_orders`, `pallet_*` |
| **Wewnętrzne** | kolejka kontenerów, statusy, dokumenty transportowe (CMR, PL, BL), reguły planowania, historia zmian | `containers`, `attachments`, `audit_log` |
| **Sekrety** | `SECRET_KEY`, `DATA_ENCRYPTION_KEY`, hasła DB/SMTP, tokeny M365/SMSAPI/AIS/n8n, klucz `age` | wyłącznie env Coolify; cache MSAL w bazie szyfrowany Fernet |
| **Publiczne** | formularz awizacji i wywołania palet (po tokenie), instancja demo z danymi syntetycznymi | `/avizo/*`, `/dlt/*`, demo |

### 3.4 TOP 10 ryzyk

Waga: **W** wysoka / **Ś** średnia / **N** niska (jak w `BUGS-FOUND.md`). P = prawdopodobieństwo, S = skutek.

| # | Ryzyko | Waga | P / S | Dowód | Rekomendacja (do decyzji PO) |
|---|---|---|---|---|---|
| R-01 | **Izolacja spółek i partnerów wyłącznie w warstwie aplikacji.** `deps.py` to pojedynczy punkt krytyczny (cut-vertex); baza nie wymusza zgodności `company_id` między tabelami. Jedno pominięcie `get_scoped`/`scope_*` w nowej z ~450 tras = wyciek danych między spółkami lub do partnera (konkurencyjne spedycje widzą się nawzajem). | W | niskie / krytyczny | D9; `04` niespójność 9; testy IDOR i macierz istnieją, ale pilnują tras już znanych | strażnik statyczny „każda trasa z `{id}` używa `get_scoped`”; rozważyć CHECK/FK spójności spółki albo RLS w PostgreSQL (ADR); wymóg testu „obca spółka → 404” w DoD każdej nowej trasy |
| R-02 | **Ciche nadpisanie przy równoczesnej edycji** (lost update): PATCH kontenera, statusu, odprawy i zleceń bez `version`/`If-Match`/porównania `updated_at`. Przy kilku logistykach w fazie testów — prawdopodobne; skutek: błędny termin dostawy bez śladu w historii, kto go cofnął. | W | wysokie / wysoki | B-004, P-13 (zweryfikowane: brak `version_id_col`) | kolumna wersji + 409 z komunikatem „ktoś zmienił w międzyczasie”; test współbieżności; UI odświeża kartę |
| R-03 | **Załączniki kontenerów sprawdzane tylko po rozszerzeniu** (16 typów, w tym `zip`, `xml`, `msg`, `eml`, `doc`); pliki krążą między firmami (spedytor → logistyka → agencja). Złośliwy plik z poprawnym rozszerzeniem przechodzi; brak skanu AV. | Ś | średnie / wysoki | T-05; `SECURITY.md` „znane ograniczenia”; zdjęcia mają sniffing, załączniki nie | sygnatury bajtów dla PDF/obrazów/Office/ZIP (jak dla zdjęć), opcjonalnie ClamAV; wpis w rejestrze ryzyk, jeśli AV odłożone (pobieranie już idzie jako `attachment` — `FileResponse(filename=…)`) |
| R-04 | **Produkcja bez `DATABASE_URL` startuje na SQLite** (`config.py` domyślnie `sqlite:///./timporye.db`, `validate_settings` tego nie sprawdza). Błąd konfiguracji w Coolify = pusta baza plikowa w kontenerze, bez backupu; użytkownicy widzą „pustą kolejkę”, a nowe wpisy giną przy redeployu. | Ś | niskie / wysoki | B-005 (zweryfikowane 2026-10-15: nadal otwarte) | fail-fast: na prod wymagany `postgresql://`; 1 test |
| R-05 | **Jeden sekret do dwóch celów:** `SECRET_KEY` podpisuje JWT i (bez `DATA_ENCRYPTION_KEY`) szyfruje dane w bazie (cache MSAL z refresh tokenem M365). Rotacja klucza JWT po incydencie unieważnia dane, a prod nie wymaga osobnego klucza. | Ś | niskie / wysoki | SEC-017; `crypto.py`; `validate_settings` nie wymaga `DATA_ENCRYPTION_KEY` | na prod wymagać `DATA_ENCRYPTION_KEY`; procedura rotacji obu kluczy w RUNBOOK |
| R-06 | **Publiczne formularze nierówno chronione:** link wywołań palet (DLT) bez własnego limitu żądań i kontroli pochodzenia (awizacja je ma), parametr daty wolnych slotów bez zakresu, globalny limiter API w pamięci procesu (znika po restarcie, per instancja). Skutek: enumeracja/zalew, koszty SMS/maili. | Ś | średnie / średni | T-01, T-02, T-03; `rate_limit.ApiRateLimiter` | wspólny limiter dla wszystkich tras publicznych (ten sam co `routers/avizo.py`), walidacja zakresu dat; limiter w bazie lub Redis przy >1 instancji |
| R-07 | **Powierzchnia parserów plików od partnerów w procesie API:** PDF (pdfminer, pdfplumber, pypdf), XLSX (openpyxl), XML (stdlib `ElementTree` z własnym odrzucaniem DTD zamiast `defusedxml`), ZIP (limit z deklarowanego rozmiaru — T-06), `.msg`/`.eml` (extract-msg), HEIC, OCR. Spreparowany plik = DoS (CPU/RAM całej aplikacji) lub błąd parsera. | Ś | średnie / średni | T-06; `invoices/sad_xml.py` (`nosec B405`); OCR częściowo w tle, limit stron PDF | `defusedxml`; ZIP: limit liczony z faktycznie rozpakowanych bajtów i współczynnika kompresji; timeouty/limity pamięci dla parsowania (osobny proces lub worker); testy plików złośliwych (planowany w `ETAP-0-PLAN.md` `test_imports_malicious.py` nie powstał) |
| R-08 | **Łańcuch dostaw i CI — luki w bramkach:** Trivy tylko raportuje (`--exit-code 0`), brak SAST semantycznego (Semgrep/CodeQL), brak `dependabot.yml` w tym repo mimo deklaracji w `SECURITY.md`, wersje narzędzi pre-commit ≠ CI (Bandit 1.8.0 vs 1.9.4, gitleaks 8.21.2 vs 8.30.1), obraz nieskanowany przy PR, brak podpisu obrazu. | Ś | niskie / średni | `.github/workflows/`, `.pre-commit-config.yaml` | Trivy HIGH/CRITICAL jako bramka (z listą wyjątków), Semgrep OWASP w `security.yml`, `dependabot.yml`, wyrównanie wersji; decyzja co do CodeQL (koszt minut) |
| R-09 | **RODO — mechanizmy bez dokumentacji i podstaw:** przetwarzane są dane kierowców (osób trzecich, bez konta), IP i loginy, treści SMS z linkami; brak rejestru czynności przetwarzania, podstaw prawnych, analizy powierzeń (SMSAPI, Sentry, M365, hosting), DPIA; scrubbing Sentry regexowy (imiona w wolnym tekście nie są wyłapywane). Skutek: niezgodność formalna, trudność obsługi żądania osoby. | Ś | średnie / wysoki | `REGULY-PROCESU.md` (wiersze RODO), `data_subject.py`, `redaction.py` | `RODO.md`: administrator, podstawy, retencje (już są), powierzenia, procedura żądań; klasyfikacja danych (§3.3); zasada „bez imion w komunikatach błędów” jako test |
| R-10 | **Ciągłość działania:** jedna instancja, backup raz w tygodniu (RPO do 7 dni — świadoma decyzja właściciela 2026-09-28), kopie **na tym samym serwerze** (kopia poza serwer „zalecana”, niewdrożona), brak udokumentowanej procedury incydentu/odtworzenia krok po kroku, brak stagingu. | Ś | niskie / wysoki | `docs/BACKUPY.md`, `REGULY-PROCESU.md` „Kopie zapasowe (zmiana)”, `BEZPIECZENSTWO.md` §4 (1 zdanie) | kopia off-site (np. rclone do S3/Backblaze, szyfrowana `age` już jest), RUNBOOK z odtworzeniem i incydentem, ćwiczenie odtworzenia raz na kwartał; decyzja PO o RPO |

### 3.5 Pozostałe obserwacje (niższa waga)

- **2FA administratorów nieobowiązkowe** (`REQUIRE_2FA_ADMIN=false`, decyzja właściciela 2026-09-29). Minimum
  z §6 procesu mówi „opcjonalnie”, ale dla kont z dostępem do wszystkich spółek rekomendujemy `true` na produkcji.
- **Konto demo publiczne** z hasłem w README i auto-logowaniem `/demo`: tylko odczyt wymuszony po stronie
  serwera (403), dane syntetyczne, nocny reset. Ryzyko: współdzielone konto, wyłączona weryfikacja backupu
  (`VERIFY_BACKUP_WEEKDAY=-1`) — akceptowalne, o ile instancja demo nigdy nie dostanie danych rzeczywistych.
- **CSRF:** żądanie bez `Origin` i `Referer` przechodzi (udokumentowane: klient spoza przeglądarki); bez
  prefiksu `__Host-` dla cookies (wymaga HTTPS); n8n za tą samą bramą = ten sam origin (opisane w `BEZPIECZENSTWO.md`).
- **`csv_safe` nie neutralizuje `\t` i `\r`** na początku pola (B-002, OWASP) — niska waga, prosta poprawka.
- **Token automatyzacji n8n** statyczny i długoterminowy; mitigacje są (brak roli admin, CIDR, termin ważności,
  rotacja z poprzednim tokenem) — upewnić się, że `AUTOMATION_ALLOWED_CIDRS` i `AUTOMATION_TOKEN_EXPIRES` są
  ustawione na produkcji.
- **`dangerouslySetInnerHTML`** w `LandingPage.tsx` dla statycznego markupu — udokumentować jako wyjątek z datą
  przeglądu.
- **Surowe f-stringi SQL** w `backup_verify.py` i `db_bootstrap.py` — stałe identyfikatory z kodu, `nosec`
  uzasadnione; nie przyjmują danych użytkownika.
- **`ALLOWED_HOSTS` puste domyślnie** — filtr Hosta wyłączony, dopóki nie ustawi go operator; `PUBLIC_BASE_URL`
  (wymagany) ogranicza skutek do CSRF-origin i linków.
- **Poczta przychodząca do poczekalni bez listy zaufanych nadawców** (T-04) — każdy e-mail trafiający na
  skrzynkę może utworzyć wpis.

---

## 4. Rozbieżności: dokumentacja ↔ kod ↔ repozytorium publiczne

| Dokument | Twierdzenie | Stan w kodzie / repo (2026-10-15) |
|---|---|---|
| `BUGS-FOUND.md` B-001 | raport błędów SAP bez ochrony przed formułami — PODEJRZENIE | **naprawione**: `imports_master.py` używa `exports.append_row` |
| `BUGS-FOUND.md` B-003 | PAZ i analityka bez limitu rozmiaru — PODEJRZENIE | **naprawione**: oba używają `read_upload_capped` |
| `BUGS-FOUND.md` B-002, B-004, B-005 | PODEJRZENIE | nadal otwarte (zweryfikowane) |
| `SECURITY.md` | joby na runnerze self-hosted; `automerge.yml` z listą REQUIRED; Dependabot w `.github/dependabot.yml` | workflowy używają `ubuntu-latest`; `automerge.yml` i `dependabot.yml` nie istnieją w tym repo |
| `CLAUDE.md`, `ONBOARDING-DEV.md` | graf wiedzy `graphify-out/wiki/index.md` | katalog nie istnieje |
| `docs/testy/E2E.md` | `e2e.yml` co noc | plik nie istnieje w tym repo |
| `docs/CLAUDE-GITHUB.md` | `claude.yml`, `claude-conflicts.yml` | pliki nie istnieją w tym repo |
| `README.md` | ok. 2100 testów, ok. 20 min | 2112 testów; 2:17 równolegle na 4 rdzeniach (sekwencyjnie dłużej) |
| `README.md`, CI, `Dockerfile.coolify` | Python 3.12–3.14 / 3.12 / 3.14; Node 22.12+ / 24 / 26 | trzy różne wersje każdego środowiska |
| `docs/ARCHITEKTURA.md` (stan 2026-09-28) | „HTTP :81 bez TLS”, 2 runnery self-hosted | demo za HTTPS (`SECURE_COOKIES`), runnery GitHub |
| `docs/SPECYFIKACJA.md` §3 | awizacja bez slotów | sloty z pojemnością (`slots.py`) — już odnotowane w `07` |
| `docs/06-decyzje.md`, komentarze w kodzie | odwołania do PR-ów #637, #796, #846, #885… | prywatne repozytorium; w publicznym 17 PR-ów o innych numerach |

---

## 5. Repozytorium a struktura docelowa procesu zespołowego

Zasada: **nie dublować** — istniejące dokumenty są dobre; nowe pliki mają być cienkie i linkować, albo istniejące
mają zostać przeniesione (decyzja PO, §7 pyt. 5).

| Plik docelowy | Stan | Co już istnieje / co trzeba dopisać |
|---|---|---|
| `README.md` | jest (pod rekrutera) | dopisać status projektu i linki do nowych dokumentów |
| `CONTRIBUTING.md` | **brak** | treść rozproszona: `CLAUDE.md`, `ONBOARDING-DEV.md` §5, nagłówek `REGULY-PROCESU.md`; dopisać Definition of Ready/Done z §4 procesu |
| `SECURITY.md` | jest | zaktualizować (runner, Dependabot, automerge); dodać politykę i kontakt |
| `CHANGELOG.md` | **brak** | zacząć od `0.1.0` (stan obecny) w Keep a Changelog |
| `.github/ISSUE_TEMPLATE/{user_story,bug,security_issue}.md` | **brak** | — |
| `.github/pull_request_template.md` | **brak** | checklisty BA/DEV/SEC |
| `.github/CODEOWNERS` | **brak** | opisowo: `backend/app/deps.py`, `security.py`, `csrf.py`, `.github/` → SEC; `docs/analiza/` → BA |
| `.github/workflows/ci.yml` | jest jako 5 workflowów | zostawić podział; dodać bramkę Trivy, Semgrep, `dependabot.yml` (R-08) |
| `docs/analiza/WIZJA.md` | częściowo | `01-problem-i-zakres.md` (problem, cel, interesariusze); brak mierników sukcesu |
| `docs/analiza/INTERESARIUSZE.md` | częściowo | tabela w `01`; brak wpływu/oczekiwań/kanału kontaktu |
| `docs/analiza/PROCESY.md` | jest | `02-proces.md` + `bpmn/` + mapy (starsze niezgodne z kodem) |
| `docs/analiza/WYMAGANIA.md` | częściowo | `05-wymagania.md` = 28 FR rdzenia; brak NFR i modułów pobocznych |
| `docs/analiza/HISTORYJKI.md` | **brak** | backlog MoSCoW; kandydaci w §6 |
| `docs/analiza/SLOWNIK.md` | **brak** | pojęcia z `REGULY-PROCESU.md`, `enums.py`, i18n |
| `docs/analiza/ZALOZENIA.md` | **brak** | — |
| `docs/analiza/SLEDZENIE.md` | częściowo | `05` ma wymaganie → kod → test; dodać historyjkę i PR |
| `docs/architektura/ARCHITEKTURA.md` | jest | `docs/ARCHITEKTURA.md` (Mermaid, poziom kontekst/kontenery); odświeżyć stan |
| `docs/architektura/MODEL_DANYCH.md` | jest | `04-model-danych.md` (ERD Mermaid, 18 encji z 106 tabel) |
| `docs/architektura/API.md` | **brak** | OpenAPI generowane, wyłączone na prod; potrzebny opis statyczny lub eksport `openapi.json` w CI |
| `docs/architektura/adr/` | częściowo | `06-decyzje.md` (12 decyzji w jednym pliku, format zgodny z ADR); nowe decyzje jako osobne pliki |
| `docs/bezpieczenstwo/KLASYFIKACJA_DANYCH.md` | **brak** | szkic w §3.3 |
| `docs/bezpieczenstwo/THREAT_MODEL.md` | **brak** | elementy w `BEZPIECZENSTWO.md`; STRIDE per przepływ do napisania |
| `docs/bezpieczenstwo/RYZYKA.md` | **brak** | §3.4 jako start; mapa ryzyk testowych w `ETAP-0-PLAN.md` §3; „znane ograniczenia” w `SECURITY.md` |
| `docs/bezpieczenstwo/RODO.md` | częściowo | retencje i prawa osób są w kodzie i `REGULY-PROCESU.md`; brak podstaw, rejestru, powierzeń |
| `docs/bezpieczenstwo/CHECKLISTA_ASVS.md` | **brak** | poziom do ustalenia (propozycja: ASVS L2 dla aplikacji z danymi osobowymi partnerów) |
| `docs/testy/STRATEGIA_TESTOW.md` | częściowo | `docs/testy/E2E.md`, `ETAP-0-PLAN.md`; brak piramidy, progów, zasad dla nowych funkcji |
| `docs/operacje/RUNBOOK.md` | częściowo | `DEPLOY_COOLIFY.md`, `BACKUPY.md`, `JEDNA-INSTANCJA.md`, `scripts/smoke.sh`; brak incydentu i odtworzenia krok po kroku |

---

## 6. Kandydaci do backlogu (do priorytetyzacji z PO, **jeszcze nie zaplanowane**)

Pilne poprawki bezpieczeństwa i integralności z audytu (proponowane jako pierwsze historyjki):

1. **SEC** R-04: fail-fast na prod bez PostgreSQL (`DATABASE_URL`) — mały, 1 test.
2. **SEC** R-05: wymagany `DATA_ENCRYPTION_KEY` na prod + procedura rotacji — mały; **uwaga:** wdrożenie bez
   ustawionej zmiennej zatrzyma start aplikacji (wymaga koordynacji z PO przed redeployem).
3. **SEC/DEV** R-02: kontrola wersji przy edycji kontenera/statusu/odprawy/zleceń (409 przy konflikcie) — średni.
4. **SEC** R-03: sygnatury bajtów dla załączników — mały/średni.
5. **SEC** R-06: wspólny limiter i walidacja dla tras publicznych (DLT jak awizacja) — mały.
6. **SEC** R-07: `defusedxml`, limit ZIP z faktycznych bajtów — mały.
7. **SEC** R-08: Trivy jako bramka, Semgrep OWASP, `dependabot.yml`, wyrównanie wersji pre-commit — mały (CI).
8. **SEC** B-002: `csv_safe` dla `\t`/`\r` — trywialny.
9. **BA/UX** P-01: fałszywy sukces przy odpowiedzi spedytora — mały, wysoki wpływ na zaufanie użytkownika.
10. **DEV** aktualizacja `BUGS-FOUND.md`, `SECURITY.md`, usunięcie odwołań do nieistniejących plików — docs.

Dalsze (po decyzjach): R-01 (strażnik statyczny + ADR o spójności w bazie), R-09 (`RODO.md`), R-10 (kopia
off-site, RUNBOOK), P-05/P-06/P-09, dług modelu danych (§2.6 pkt 1), jedna wersja Python/Node.

---

## 7. [BA] Pytania do Product Ownera — seria 1

Bez odpowiedzi nie ruszamy kroku 3 („szkielet struktury”). Jeśli PO nie odpowie, BA przyjmie w nawiasie
podane **bezpieczne minimum** i zapisze je w `docs/analiza/ZALOZENIA.md` jako „do potwierdzenia”.

1. **Cel na najbliższe 4–8 tygodni.** Co jest ważniejsze: (a) zakończenie testów z użytkownikami i wyjście
   z Excela na produkcji, czy (b) repozytorium jako portfolio (proces, dokumenty, demo)? Które repozytorium jest
   dziś źródłem prawdy dla pracy — to publiczne czy prywatne, z którego pochodzi kopia? *(Minimum: (b) proces
   i dokumenty w tym repo, bez ingerencji w produkcję.)*
2. **Użytkownicy i skala dziś.** Ile osób i w jakich rolach realnie korzysta z aplikacji w fazie testów, które
   spółki/magazyny/partnerzy są „na żywo”, i kto (1–2 osoby) może być dla BA głosem użytkownika? Czy mierzymy
   już cokolwiek (czas, liczba kontenerów w aplikacji vs w Excelu)? *(Minimum: 4 osoby logistyki + 1 magazyn,
   bez partnerów zewnętrznych; mierniki do zdefiniowania.)*
3. **Priorytety bólu.** Z listy §1.6 i §3.4: które trzy rzeczy bolą użytkowników najbardziej teraz? Które moduły
   poboczne są *must have* (faktury/SAD, reklamacje, wyceny, palety, śledzenie, asystent AI), a które można
   zamrozić, żeby nie pisać dla nich wymagań i testów? *(Minimum: rdzeń + powiadomienia = must; reszta = could,
   bez nowych prac.)*
4. **Bezpieczeństwo i RODO — cztery decyzje.** (a) Zgoda na fail-fast na produkcji dla `DATABASE_URL`
   i `DATA_ENCRYPTION_KEY` (ryzyko: zatrzymany start przy następnym redeployu, jeśli zmienne nie będą ustawione)?
   (b) `REQUIRE_2FA_ADMIN=true` na produkcji? (c) Kto jest administratorem danych (która spółka) i czy jest osoba
   kontaktowa IT/RODO — potrzebne do `RODO.md`? (d) Instancja demo zostaje publiczna na stałe? *(Minimum:
   (a) tak, z ostrzeżeniem w CHANGELOG; (b) rekomendacja, bez zmiany; (c) „do potwierdzenia”; (d) tak.)*
5. **Konwencje procesu.** (a) Język commitów: angielski (jak w procesie) czy polski (jak dotychczasowa historia)?
   (b) Nowa struktura `docs/analiza|architektura|bezpieczenstwo|testy|operacje`: tworzymy jako cienkie
   indeksy linkujące do `01–07`, czy przenosimy istniejące pliki (zmiana ścieżek w README i linkach)?
   (c) Próg pokrycia 92 % zostaje; czy ustalamy próg dla frontendu? (d) Merge wyłącznie po Twojej akceptacji
   (koniec auto-merge’a po „CI OK”)? *(Minimum: (a) angielski; (b) indeksy, bez przenoszenia; (c) 92 %, frontend
   bez progu; (d) tak.)*

---

## Załącznik A. Metoda i narzędzia

Środowisko: świeży klon, Linux, Python 3.12 (venv `uv`, lock z `--require-hashes`), Node 22.22, 4 rdzenie.

```bash
# backend
cd backend
ruff check .                                    # 0 błędów
python scripts/mypy_baseline.py                 # 0 nowych, 191 znanych
bandit -r app -c pyproject.toml                 # 0 ustaleń
pip-audit -r requirements.txt --no-deps         # 0
pip-audit -r requirements-dev.txt --no-deps     # 0
python -m pytest tests/ -q -n 4                 # 2112 passed, 2 skipped, 2:17
# frontend
cd frontend
npm ci && npm run typecheck                     # 0 błędów
npm run lint:setup && npm run lint              # 0 błędów, 12 ostrzeżeń (LEGACY_WARN)
npm run test                                    # 964 passed (238 plików), 3:07
npm audit --audit-level=high                    # 0
# repo
python3 scripts/check_file_lengths.py           # OK
gitleaks git --redact --no-banner .             # cała historia, 0 wycieków
```

Nie uruchomiono: Trivy (brak binarki w środowisku audytu; w CI co tydzień), Semgrep, CodeQL (nieskonfigurowane),
E2E Playwright (wymaga uruchomionej aplikacji; nie było celem audytu), pomiar pokrycia (tylko w CI).

Ustalenia z istniejących audytów cytowane po identyfikatorach z repozytorium: `P-xx`, `T-xx` (`07-ograniczenia.md`),
`B-xxx` (`BUGS-FOUND.md`), `SEC-/ACL-/GDPR-/BUILD-/OBS-xxx` (komentarze w kodzie i `REGULY-PROCESU.md`).
