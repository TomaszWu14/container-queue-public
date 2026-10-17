# Wymagania — wersja 0.1

2026-10-16, [BA] (sekcja SR z [SEC]). Identyfikatory: **FR-nnn** funkcjonalne, **NFR-nnn** niefunkcjonalne,
**SR-nnn** bezpieczeństwa. Kryteria akceptacji wymagań rdzenia są w [`../05-wymagania.md`](../05-wymagania.md)
(format Dane / Gdy / Wtedy, miejsce w kodzie, test) — ten plik ich nie powiela (Z-012), tylko nadaje
identyfikatory i dodaje to, czego `05` nie ma: NFR, SR, moduły poboczne, otwarte punkty.
Priorytety MoSCoW: wszystko, co wdrożone, jest *Must* (utrzymujemy); nowe — wg `HISTORYJKI.md`.

## 1. Wymagania funkcjonalne rdzenia (wdrożone)

| ID | `05` | Wymaganie (skrót) | Priorytet | Status |
|---|---|---|---|---|
| FR-001 | W-01 | Numer kontenera tylko zgodny z ISO 6346; normalizacja spacji i wielkości liter | Must | wdrożone |
| FR-002 | W-02 | Numer unikalny w spółce wśród kontenerów niezrealizowanych | Must | wdrożone |
| FR-003 | W-03 | 10 statusów; cofnięcie o 1 krok z notatką, o więcej — tylko admin | Must | wdrożone |
| FR-004 | W-04 | Magazyn ustawia wyłącznie DOSTARCZONY; nieawizowany — z notatką | Must | wdrożone |
| FR-005 | W-05 | Status kontenera wynika ze statusu odprawy, tylko do przodu | Must | wdrożone |
| FR-006 | W-06 | Każda zmiana pola w historii: kto, kiedy, było → jest, notatka; dane kierowcy maskowane | Must | wdrożone; wersjonowanie rekordu — US-003 |
| FR-007 | W-07 | Status odprawy zmienia agencja; logistyka awaryjnie; spedytor nigdy; REWIZJA z notatką | Must | wdrożone; brak testu 403 dla spedytora |
| FR-008 | W-08 | Cofnięcie odprawy z ODPRAWIONY/ZWOLNIONY/ROZLICZONY tylko logistyka, z notatką | Must | wdrożone |
| FR-009 | W-09 | Wysyłka dokumentów do agencji ostrzega o brakach (409), „wyślij mimo to” z wpisem w audycie ([specyfikacja](spec/WYSYLKA-DOKUMENTOW-DO-AGENCJI.md)) | Must | wdrożone |
| FR-010 | W-10 | Braki dokumentów nie blokują statusu; ostrzeżenie i wpis w historii | Must | wdrożone |
| FR-011 | W-11 | Wymagane dokumenty zależą od etapu; profil dostawcy zawęża zestaw | Must | wdrożone |
| FR-012 | W-12 | PDF z numerem innego kontenera odrzucony (409); uszkodzony 422; skan przyjęty z ostrzeżeniem | Must | wdrożone |
| FR-013 | W-13 | SAD-PZ → ODPRAWIONY, SAD-PW → ZWOLNIONY; plik od spedytora nie zmienia statusu | Must | wdrożone |
| FR-014 | W-14 | Propozycja daty dostawy: ETA + 4 dni w stanie PROPOZYCJA | Must | wdrożone; rozjazd P-02/P-03 |
| FR-015 | W-15 | Uzgodniona data nie zmienia się sama po zmianie ETA; ręczna zmiana cofa do PROPOZYCJA | Must | wdrożone |
| FR-016 | W-16 | Limit dzienny magazynu ostrzega, nie blokuje; tranzyty i propozycje nie liczą się | Must | wdrożone |
| FR-017 | W-17 | Kalendarz dni wolnych kraju magazynu (PL/PT) i wyjątki per magazyn | Must | wdrożone; P-06 |
| FR-018 | W-18 | Sloty rozładunku z pojemnością | Must | wdrożone |
| FR-019 | W-19 | Awizacja przez jednorazowe linki (7 / 5 dni), 409 po użyciu, 410 po wygaśnięciu, SHA-256 w bazie | Must | wdrożone |
| FR-020 | W-20 | Odpowiedź spedytora zmienia plan dopiero po decyzji logistyki | Must | wdrożone; P-01 (US-009) |
| FR-021 | W-21 | Publiczny formularz: 30 żądań/min na IP → 429; obcy Origin odrzucony | Must | wdrożone dla awizacji; MAG-1 — US-005 |
| FR-022 | W-22 | Spółka widzi tylko swoje kontenery; cudzy rekord = 404 | Must | wdrożone |
| FR-023 | W-23 | Partner widzi tylko kontenery mu zlecone; konto bez przypisania nie widzi nic | Must | wdrożone |
| FR-024 | W-24 | Role widzą tylko potrzebne pola; po ukrytym polu nie da się szukać | Must | wdrożone |
| FR-025 | W-25 | Import z Excela nie cofa danych z aplikacji | Must | wdrożone |
| FR-026 | W-26 | Konflikt Excel/aplikacja rozstrzyga nowsza zmiana | Must | wdrożone |
| FR-027 | W-27 | Dane kierowców anonimizowane 90 dni po zamknięciu, także kopie | Must | wdrożone |
| FR-028 | W-28 | Alert ≤ 3 dni przed końcem dni wolnych demurrage, raz dziennie | Must | wdrożone |

## 2. Moduły poboczne (wdrożone, bez wymagań z identyfikatorami)

Założenie Z-005: *Could* — bez nowych prac i bez spisywania wymagań, dopóki PO nie zdecyduje inaczej (US-023).
Rezerwacja zakresów ID: FR-100 wyceny i zlecenia transportu · FR-120 śledzenie statków (AIS) · FR-140
powiadomienia i digesty · FR-160 faktury, SAD, poczekalnia dokumentów · FR-180 reklamacje · FR-200 wywołania
palet i Power BI · FR-220 kartoteka dostawców i master data · FR-240 analityka · FR-260 baza wiedzy i asystent ·
FR-280 administracja (konta, 2FA, podgląd jako rola, logi, monitor).

Wyjątek: **powiadomienia** (FR-140) są *Must* (Z-005) — alerty demurrage (FR-028), awizacji (FR-019/020)
i odprawy należą do rdzenia; pozostałe kanały (Teams, SMS, digest) do spisania w US-023.

## 3. Wymagania niefunkcjonalne

| ID | Obszar | Wymaganie | Stan obecny / miara | Cel | Status |
|---|---|---|---|---|---|
| NFR-001 | Dostępność | Aplikacja działa jako jedna instancja z automatycznym restartem po zawieszeniu (HEALTHCHECK + strażnik) | brak pomiaru dostępności | do ustalenia z PO (propozycja: 99 % w godz. 6–22) | częściowo |
| NFR-002 | Ciągłość | Kopia bazy i załączników raz w tygodniu, szyfrowana, z cotygodniową weryfikacją odtworzenia; RPO ≤ 7 dni | kopie lokalne; brak off-site; RTO nieokreślone | RTO do ustalenia; kopia off-site (US-013) | częściowo |
| NFR-003 | Wydajność | Lista kolejki miesiąca (ok. 200 kontenerów) ładuje się bez odczuwalnego czekania; odpowiedzi JSON kompresowane | gzip od 1 kB; brak pomiaru p95 | propozycja: p95 < 2 s dla `/api/containers` | brak pomiaru |
| NFR-004 | Skalowalność | 1 proces; > 1 worker tylko na PostgreSQL (lider pętli tła na advisory lock) | `docs/JEDNA-INSTANCJA.md` | świadome ograniczenie (Won't) | wdrożone |
| NFR-005 | Bezpieczeństwo | Poziom OWASP ASVS L2 (Z-017); wymagania SR niżej | `../bezpieczenstwo/CHECKLISTA_ASVS.md` | L2 potwierdzone (US-025) | częściowo |
| NFR-006 | Ochrona danych | Retencje: kierowcy 90 dni, log logowań 90, tokeny 30, SMS 90, błędy JS 30, powiadomienia 90; eksport i anonimizacja danych osoby | `retention.py`, `data_subject.py` | `RODO.md` 1.0 (US-012) | wdrożone / dokumentacja 0.1 |
| NFR-007 | Użyteczność | Panel w PL/EN/PT; ekrany magazynu, reklamacji i formularz awizacji działają na telefonie/tablecie; komunikaty błędów mówią, co zrobić | audyty UX; P-01 | bez fałszywych komunikatów sukcesu (US-009) | wdrożone z wyjątkami |
| NFR-008 | Dostępność cyfrowa | Elementy interaktywne mają etykiety; przyciski dostępne z klawiatury | testy `a11y.buttons`, `a11y.labels` | audyt WCAG 2.1 AA — do decyzji | częściowo |
| NFR-009 | Utrzymywalność | Limit 500 linii/plik; lint i typy w CI (baseline tylko maleje); pokrycie ≥ 92 % linii backendu; 1 PR = 1 temat | `scripts/check_file_lengths.py`, `pyproject.toml` | utrzymać | wdrożone |
| NFR-010 | Obserwowalność | `/api/health` i `/api/health/deep`; `X-Request-ID`; metryki zadań tła w `job_runs`; Sentry opcjonalnie ze scrubbingiem | wdrożone | — | wdrożone |
| NFR-011 | Przenośność | Ten sam model na SQLite (dev/testy) i PostgreSQL 16 (prod); jeden obraz Docker; konfiguracja wyłącznie przez env; produkcja wymaga PostgreSQL | 3 wersje Pythona i Node w README/CI/obrazie; prod bez `DATABASE_URL` startuje na SQLite | US-001, US-015 | częściowo |
| NFR-012 | Zgodność | ISO 6346; święta PL/PT; czas Europe/Warsaw dla digestów i SMS | wdrożone | — | wdrożone |
| NFR-013 | Audytowalność | Każda zmiana z autorem i powodem; nieudane logowania z IP przez 90 dni; zmiany z n8n podpisane kontem serwisowym | wdrożone | wersjonowanie rekordów (US-003) | wdrożone |

## 4. Wymagania bezpieczeństwa (minimum z procesu zespołowego, §6)

| ID | Wymaganie | Stan (dowód w `docs/AUDYT.md` §3.1) | Status |
|---|---|---|---|
| SR-001 | Hasła bcrypt (≥ 12 rund na produkcji); polityka: min. 12 znaków, litera i cyfra | `security.py`, `validate_settings` | wdrożone |
| SR-002 | Limit prób logowania: para IP+login, suma na IP, konto z progresywną przerwą; stan odporny na restart | `rate_limit.py` (baza) | wdrożone |
| SR-003 | Sesje: cookie `HttpOnly`, `SameSite=Lax`, `Secure` za HTTPS; access 2 h; refresh 14 dni z rotacją i wykryciem ponownego użycia | `security.py` | wdrożone |
| SR-004 | 2FA dostępne dla każdej roli; dla administratorów wymuszane | TOTP + kody zapasowe; wymuszenie flagą, domyślnie wyłączone (E-01) | częściowo |
| SR-005 | Autoryzacja po stronie serwera dla każdej trasy; izolacja per zasób w jednym miejscu; test „brak dostępu” dla każdej roli i obcej spółki | `deps.py`, `tests/permissions.yaml`, `test_routes_require_auth.py` | wdrożone; strażnik nowych tras — US-011 |
| SR-006 | Walidacja wejścia (Pydantic), ORM bez surowego SQL z danymi użytkownika, escapowanie wyjścia (Jinja2 autoescape, React), CSRF, neutralizacja formuł w eksportach | `csrf.py`, `exports.py`, `html_templates.py` | wdrożone; `\t`/`\r` — US-008; XML/ZIP — US-006 |
| SR-007 | Upload: limit rozmiaru, weryfikacja typu po zawartości, nazwa na dysku z losowym składnikiem, katalog poza publicznym | `MAX_UPLOAD_MB`; sygnatury dla zdjęć; `stored_name = <id>_<token_hex>_<nazwa>`; `/data/uploads` | częściowo (załączniki — US-004) |
| SR-008 | Nagłówki: CSP, HSTS (za HTTPS), `X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options`, `Permissions-Policy`, COOP | `main.py`, `nginx.conf`, test zgodności | wdrożone |
| SR-009 | Sekrety tylko w zmiennych środowiskowych; `.env.example` bez wartości; produkcja odmawia startu z domyślnymi i słabymi sekretami | `validate_settings`, `test_env_example.py` | wdrożone; `DATABASE_URL`/`DATA_ENCRYPTION_KEY` — US-001/002 |
| SR-010 | Logi bez haseł, tokenów i zbędnych danych osobowych; audit log operacji wrażliwych | `redaction.py`, `audit.py`, `applog.py` | wdrożone |
| SR-011 | RODO: minimalizacja, retencja i usuwanie, eksport danych osoby, rejestr czynności | mechanizmy w kodzie; rejestr w `RODO.md` 0.1 | częściowo (US-012) |
| SR-012 | LLM: treść użytkownika jako dane, nie instrukcje; minimalizacja danych do modelu; limity | fakty z bazy po izolacji roli + stały prompt systemowy; model lokalny (Ollama, adres wewnętrzny); 10 pytań/min, 1 równoległe, timeout | wdrożone |
| SR-013 | Łańcuch dostaw: zależności z hashami, akcje i obrazy przypięte, skany sekretów/SAST/SCA/obrazu w CI jako bramki | hashe, SHA, gitleaks + Bandit bramkują; Trivy nie bramkuje, brak Semgrep | częściowo (US-007) |
| SR-014 | Kopie zapasowe szyfrowane, weryfikowane, z udokumentowanym odtworzeniem i kopią poza serwer | `age`, `verify_backup.py`, `BACKUPY.md`; brak off-site | częściowo (US-013) |

## 5. Otwarte punkty (decyzja PO)

| # | Punkt | Źródło | Propozycja |
|---|---|---|---|
| O-1 | „Pola obowiązkowe konfigurowane per spółka” | `SPECYFIKACJA.md` §2 | Z-018: nie realizować bez potwierdzenia |
| O-2 | Dwie reguły „ETA + N” (4 i 3 dni) | P-02 | jedna wartość w ustawieniach admina (US-020) |
| O-3 | Retencja dokumentów handlowych i celnych po ZREALIZOWANY | `KLASYFIKACJA_DANYCH.md` | pytanie do księgowości (5 lat?) |
| O-4 | Cele liczbowe NFR-001 i NFR-003 | ten plik | PO ustala; pomiar w US-014 |
| O-5 | Które moduły poboczne są *Must* | Z-005 | PO wskazuje; wtedy US-023 |
