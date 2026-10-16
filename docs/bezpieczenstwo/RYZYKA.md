# Rejestr ryzyk i wyjątków

2026-10-16, [SEC]. Ryzyka z `docs/AUDYT.md` §3.4–3.5 i modelu zagrożeń. Prawo weta SEC: historyjka
z ryzykiem **wysokim** lub **krytycznym** nie wchodzi do `main` bez poprawki albo świadomej akceptacji PO
zapisanej tutaj (kolumna „Decyzja PO”). Przegląd rejestru: przy każdym PR z kodem i co kwartał.

Waga = wypadkowa prawdopodobieństwa (P) i skutku (S): **K** krytyczna · **W** wysoka · **Ś** średnia · **N** niska.
Status: otwarte · w realizacji · zaakceptowane (wyjątek E-xx) · zamknięte (data, PR).

## Ryzyka

| ID | Ryzyko | P | S | Waga | Status | Decyzja PO | Właściciel | Historyjka | Przegląd |
|---|---|---|---|---|---|---|---|---|---|
| R-01 | Izolacja spółek i partnerów wyłącznie w `deps.py`; baza nie wymusza spójności `company_id` — jedno pominięcie w nowej trasie = wyciek między firmami | niskie | krytyczny | W | otwarte | brak | SEC | US-011 | 2026-11-15 |
| R-02 | Ciche nadpisanie przy równoczesnej edycji (brak wersjonowania rekordów) — utrata zmian bez śladu | wysokie | wysoki | W | otwarte | brak | DEV | US-003 | 2026-11-15 |
| R-03 | Załączniki kontenerów weryfikowane tylko po rozszerzeniu; pliki krążą między firmami; brak AV | średnie | wysoki | Ś | otwarte | brak | SEC | US-004 | 2026-11-15 |
| R-04 | Produkcja bez `DATABASE_URL` startuje na SQLite (pusta baza bez kopii) | niskie | wysoki | Ś | w realizacji (PR #18, merge po Z-007) | brak (Z-007) | SEC | US-001 | 2026-11-15 |
| R-05 | `SECRET_KEY` podpisuje JWT i (domyślnie) szyfruje dane w bazie; rotacja jednego psuje drugie | niskie | wysoki | Ś | otwarte | brak (Z-007) | SEC | US-002 | 2026-11-15 |
| R-06 | Publiczne trasy nierówno chronione (DLT bez limitu i kontroli Origin, zakres dat slotów); limiter API w pamięci | średnie | średni | Ś | otwarte | brak | SEC | US-005 | 2026-11-15 |
| R-07 | Parsery plików od partnerów w procesie API (XML stdlib, ZIP z deklarowanego rozmiaru, PDF/OCR) — DoS | średnie | średni | Ś | otwarte | brak | SEC | US-006 | 2026-11-15 |
| R-08 | Łańcuch dostaw: Trivy nie bramkuje, brak Semgrep, rozjazd wersji pre-commit/CI; `dependabot.yml` dopiero od PR #18 | niskie | średni | Ś | w realizacji | brak | SEC | US-007 | 2026-11-15 |
| R-09 | RODO bez dokumentacji: brak rejestru czynności, podstaw prawnych, analizy powierzeń; scrubbing Sentry nie łapie imion | średnie | wysoki | Ś | otwarte | czeka (Z-009) | SEC/BA | US-012 | 2026-11-15 |
| R-10 | Ciągłość: jedna instancja, kopia raz w tygodniu na tym samym serwerze, brak procedury incydentu/odtworzenia, brak stagingu | niskie | wysoki | Ś | otwarte (RPO zaakceptowane: E-02) | E-02 | OPS | US-013 | 2026-11-15 |
| R-11 | 2FA administratorów nieobowiązkowe | niskie | wysoki | Ś | zaakceptowane | E-01 | PO | US-019 | 2027-01-15 |
| R-12 | Konto demo publiczne, współdzielone, hasło w README | średnie | niski | N | zaakceptowane | E-05 | PO | — | 2027-01-15 |
| R-13 | `csv_safe` nie neutralizuje `\t` i `\r` (B-002) | niskie | niski | N | otwarte | brak | DEV | US-008 | 2026-11-15 |
| R-14 | Token n8n statyczny; CIDR i termin ważności opcjonalne | niskie | średni | N | otwarte | brak | OPS | RUNBOOK (ustawić na prod) | 2026-11-15 |
| R-15 | `dangerouslySetInnerHTML` dla statycznego markupu `LandingPage` | niskie | niski | N | zaakceptowane | E-03 | DEV | — | 2027-01-15 |
| R-16 | Surowe f-stringi SQL ze stałymi identyfikatorami (`backup_verify.py`, `db_bootstrap.py`) | niskie | niski | N | zaakceptowane | E-03 | DEV | — | 2027-01-15 |
| R-17 | `ALLOWED_HOSTS` puste domyślnie (filtr Hosta wyłączony); `PUBLIC_BASE_URL` ogranicza skutek | niskie | niski | N | otwarte | brak | OPS | RUNBOOK | 2026-11-15 |
| R-18 | Poczta → poczekalnia bez listy zaufanych nadawców (T-04) | niskie | niski | N | otwarte | brak | BA | US-023 (poczekalnia) | 2026-11-15 |
| R-19 | Integracje zewnętrzne: nieoczekiwana odpowiedź = 500 (T-08…T-12) | średnie | niski | N | otwarte | brak | DEV | US-026 | 2026-11-15 |
| R-20 | Rozjazd wersji Python (3.12 CI / 3.14 obraz) i Node (22 / 24 / 26) | niskie | średni | N | otwarte | brak | DEV | US-015 | 2026-11-15 |

## Wyjątki zaakceptowane

Wyjątek = świadoma decyzja, by ryzyka nie usuwać. Każdy ma uzasadnienie, osobę akceptującą i datę przeglądu.
Po dacie przeglądu wyjątek bez odnowienia wraca do statusu „otwarte”.

| ID | Wyjątek | Uzasadnienie | Akceptuje | Data | Przegląd | Warunki |
|---|---|---|---|---|---|---|
| E-01 | `REQUIRE_2FA_ADMIN=false` | decyzja właściciela 2026-09-29; 2FA dobrowolne działa; admini bez telefonu służbowego | właściciel (do potwierdzenia jako PO, Z-008) | 2026-09-29 | 2027-01-15 | rekomendacja `true` na produkcji (US-019); wyjątek nie dotyczy kont z `view_all_companies` po wejściu partnerów |
| E-02 | Backup raz w tygodniu (RPO ≤ 7 dni), kopie lokalne | decyzja właściciela 2026-09-28 (`REGULY-PROCESU.md`) | właściciel | 2026-09-28 | 2026-12-31 | po wyjściu z Excela ponowna decyzja; kopia off-site (US-013) niezależnie od RPO |
| E-03 | Adnotacje `nosec` (14) i `dangerouslySetInnerHTML` dla statycznego markupu | każda adnotacja ma uzasadnienie w linii; markup nie zawiera danych użytkownika | SEC | 2026-10-16 | 2027-01-15 | nowa adnotacja = przegląd SEC w PR |
| E-04 | Globalny limiter API w pamięci procesu (per instancja, zerowany restartem) | kontrakt jednej instancji; limiter logowań jest w bazie | SEC | 2026-10-16 | 2027-01-15 | przy > 1 instancji — limiter w bazie/Redis |
| E-05 | Publiczna instancja demo ze współdzielonym kontem | portfolio; dane syntetyczne; tylko odczyt wymuszony serwerowo; reset nocny | PO (Z-010) | 2026-10-16 | 2027-01-15 | nigdy dane rzeczywiste; osobny serwer/baza od produkcji |
| E-06 | `ALLOW_INSECURE_HTTP=true` dla instancji bez certyfikatu | wdrożenie w sieci wewnętrznej przed HTTPS (SEC-003) | właściciel | 2026-09 | 2026-12-31 | tylko sieć wewnętrzna; demo i produkcja z HTTPS |
| E-07 | CSRF: żądanie bez `Origin` i `Referer` przechodzi; brak prefiksu `__Host-` | klienci nie-przeglądarkowi (n8n, smoke); przeglądarka zawsze dokłada `Origin` do zapisu | SEC | 2026-10-16 | 2027-01-15 | przy osobnym hoście dla n8n — `__Host-` |
| E-08 | `ALLOWED_HOSTS` puste domyślnie | `PUBLIC_BASE_URL` wymagany na prod chroni linki; filtr wymaga znajomości domeny operatora | SEC | 2026-10-16 | 2026-12-31 | RUNBOOK: ustawić na produkcji |
| E-09 | Poczta przychodząca bez listy zaufanych nadawców | wpis trafia do poczekalni, nie do kontenera; człowiek przypisuje | BA | 2026-10-16 | 2027-01-15 | przy automatycznym przypisywaniu — lista nadawców |
| E-10 | `AUTOMATION_ALLOWED_CIDRS` i `AUTOMATION_TOKEN_EXPIRES` opcjonalne | mechanizmy istnieją; brak informacji o konfiguracji produkcji | SEC | 2026-10-16 | 2026-12-31 | RUNBOOK: ustawić oba na produkcji |

## Ryzyka zamknięte

| ID | Ryzyko | Zamknięte | Jak |
|---|---|---|---|
| B-001 | Raport błędów importu SAP bez ochrony przed formułami | przed 2026-10-13 (repo prywatne) | `exports.append_row` w `imports_master.py` |
| B-003 | Import PAZ i analityki bez limitu rozmiaru | przed 2026-10-13 (repo prywatne) | `read_upload_capped` |
