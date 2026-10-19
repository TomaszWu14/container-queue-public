# Weryfikacja OWASP ASVS 4.0.3 — poziom L2, wymaganie po wymaganiu

2026-10-19, [SEC]. Historyjka: **US-025**. Wersja standardu: **ASVS 4.0.3**. Poziom docelowy: **L2**
(Z-017, uzasadnienie w `CHECKLISTA_ASVS.md`).

- **Zakres:** kod w repozytorium (`backend/app`, `frontend/src`, `Dockerfile*`, `docker-compose*.yml`,
  `.github/workflows`) i dokumentacja w `docs/`. Poza zakresem: konfiguracja serwera, proxy Coolify (TLS),
  DNS, ustawienia repozytorium GitHub i wartości zmiennych na produkcji — tam status ❓.
- **Metoda:** każde wymaganie L1 i L2 z ASVS 4.0.3 (wymagania wyłącznie L3 pominięte, podobnie wymagania
  oznaczone w standardzie jako usunięte) sprawdzone w kodzie i testach w tej gałęzi. Dowód = ścieżka pliku
  z funkcją albo nazwa testu, które zostały otwarte i potwierdzone. Twierdzenia z `CHECKLISTA_ASVS.md`
  sprawdzone ponownie, bez przenoszenia ich na wiarę.
- **Legenda:** ✅ spełnione · ⚠️ częściowo · ❌ niespełnione · n/d nie dotyczy (z powodem) ·
  ❓ nie zweryfikowano (wymaga dostępu do wdrożenia lub infrastruktury).
- Testy backendu leżą w `backend/tests/`; w kolumnie „Dowód” podana jest sama nazwa pliku testu.
- Wymagania sparafrazowane krótko — pełna treść w standardzie ASVS 4.0.3.

## Co się zmieniło względem oceny wstępnej (2026-10-16)

Sprawdzone w kodzie — te luki z `CHECKLISTA_ASVS.md` są już **zamknięte**:

- `DATABASE_URL` bez PostgreSQL blokuje start produkcji — `backend/app/settings_check.py` `validate_settings`,
  `test_config_failfast.py` (US-001).
- Trivy i Semgrep blokują PR — `.github/workflows/security.yml` (joby `trivy-pr`, `semgrep`, `--exit-code 1`,
  `--error`) (US-007).
- `csv_safe` neutralizuje `\t` i `\r` — `backend/app/exports.py` `csv_safe`, `test_exports.py` (US-008).
- XML z DTD odrzucany przed parserem, ZIP z limitem sumy i współczynnika kompresji — `backend/app/invoices/sad_xml.py`
  `_has_dtd`, `backend/app/routers/archive_upload.py`, `test_imports_malicious.py` (US-006).
- Załączniki sprawdzane po zawartości — `backend/app/file_signatures.py` `content_matches` (US-004; bez .doc/.xls/.msg/.eml).
- Ekran aktywnych sesji użytkownika (ASVS 3.3.4) — `backend/app/routers/auth.py` `my_sessions`,
  `frontend/src/pages/ProfilePage.tsx`.
- Osobny `DATA_ENCRYPTION_KEY` istnieje (`backend/app/crypto.py`, `test_crypto_data_key.py`), ale **nie jest
  wymagany** na produkcji — US-002 otwarta.

Nadal otwarte (sprawdzone): `REQUIRE_2FA_ADMIN` domyślnie `false` (`backend/app/config.py`, E-01), brak prefiksu
`__Host-` (`backend/app/security.py` `ACCESS_COOKIE`, E-07), `ALLOWED_HOSTS` puste w
`docker-compose.coolify.yml` (E-08; w `docker-compose.demo.yml` ustawione).

Nowe ustalenia (nie było ich w ocenie wstępnej): sekret TOTP w bazie otwartym tekstem, kody zapasowe 2FA
o entropii 40 bitów bez soli, brak limitu czasu sesji (refresh przesuwany co 14 dni), bcrypt obcina hasło do
72 bajtów, brak `Cache-Control: no-store` w odpowiedziach API, szablon wysyłki dokumentów przez `str.format_map`.

---

## V1 Architektura, projekt i model zagrożeń

Wszystkie wymagania V1 są na poziomie L2 (1.11.3 — L3, pominięte).

| ID | Wymaganie (krótko, własnymi słowami) | Status | Dowód | Uwagi / działanie |
|---|---|---|---|---|
| 1.1.1 | Bezpieczny cykl wytwarzania na każdym etapie | ✅ | `CONTRIBUTING.md` („Proces dla każdej funkcji”, kroki 2 i 5 [SEC]); `.github/pull_request_template.md` („Przegląd bezpieczeństwa [SEC]”) | — |
| 1.1.2 | Modelowanie zagrożeń przy zmianach projektu | ⚠️ | `docs/bezpieczenstwo/THREAT_MODEL.md` (STRIDE, 13 przepływów); `CONTRIBUTING.md` krok 2 | model 0.1 od 2026-10-16; nowsze przepływy (mail „nowe urządzenie” US-075, przegląd dostępów US-076) nie mają wierszy STRIDE — dopisać |
| 1.1.3 | Historyjki zawierają ograniczenia bezpieczeństwa | ✅ | `.github/ISSUE_TEMPLATE/user_story.md` (sekcja „Bezpieczeństwo [SEC]”); `docs/analiza/HISTORYJKI.md` (pola „[SEC]:”, np. US-002) | — |
| 1.1.4 | Udokumentowane granice zaufania, komponenty i przepływy | ✅ | `THREAT_MODEL.md` (diagram, „Granice zaufania”) | — |
| 1.1.5 | Architektura i usługi zdalne opisane i przeanalizowane | ✅ | `docs/architektura/ARCHITEKTURA.md`; `THREAT_MODEL.md` F8–F10 | — |
| 1.1.6 | Kontrole bezpieczeństwa scentralizowane i proste | ✅ | `backend/app/deps.py` (`_enforce_scope`, `get_scoped`); `backend/app/security.py` (`get_current_user`, `require_roles`); `backend/app/csrf.py`; `backend/app/public_guards.py` | — |
| 1.1.7 | Wytyczne bezpiecznego kodowania dostępne dla zespołu | ✅ | `.github/pull_request_template.md` (checklista SEC); `SECURITY.md` | — |
| 1.2.1 | Komponenty na osobnych kontach o minimalnych uprawnieniach | ✅ | `Dockerfile.coolify` i `backend/Dockerfile` (`USER timporye`); `test_nginx_nieroot.py` | konta na hoście — ❓ |
| 1.2.2 | Komunikacja między komponentami uwierzytelniona | ⚠️ | n8n → API: `backend/app/security.py` `automation_user`; API → n8n: `backend/app/automation_events.py` (HMAC `X-Timporye-Signature`); baza: hasło w `DATABASE_URL` (`docker-compose.coolify.yml`) | Ollama bez uwierzytelniania (tylko adres wewnętrzny, `backend/app/settings_check.py` `_warn_ollama_url`); podpis HMAC opcjonalny (tylko ostrzeżenie) |
| 1.2.3 | Jeden sprawdzony mechanizm uwierzytelniania | ✅ | `backend/app/security.py` `get_current_user` (JWT HS256 albo token automatu — jedno miejsce) | — |
| 1.2.4 | Wszystkie ścieżki uwierzytelniania tej samej siły | ⚠️ | `security.py` `get_current_user`; `backend/app/automation_policy.py` | token n8n statyczny, CIDR i termin ważności opcjonalne (E-10) |
| 1.4.1 | Kontrola dostępu w zaufanym punkcie (serwer) | ✅ | `backend/app/deps.py`; `security.py` `require_roles`; `test_routes_require_auth.py` | — |
| 1.4.4 | Jeden sprawdzony mechanizm kontroli dostępu | ✅ | `deps.py` `_enforce_scope`/`get_scoped`; `docs/architektura/adr/0006-izolacja-spolek-w-kodzie-i-strazniku.md`; `test_isolation_guard.py` | brak wymuszenia w bazie (R-01) |
| 1.4.5 | Dostęp wg atrybutów danych, nie tylko roli | ✅ | `deps.py` `check_container_access` (forwarder_id, customs_agency_id, warehouse_id, allowed_warehouse_ids), `forwarder_may_see` | — |
| 1.5.1 | Wymagania dla wejścia i wyjścia wg typu, treści i przepisów | ⚠️ | `docs/bezpieczenstwo/KLASYFIKACJA_DANYCH.md`; schematy w `backend/app/schemas/` | limit długości ma mniejszość pól tekstowych (97 wystąpień `max_length` w `backend/app/schemas`) — T-15 |
| 1.5.2 | Brak serializacji obiektów z niezaufanymi klientami | ✅ | JSON przez Pydantic; joblib tylko dla własnych modeli z podpisem HMAC — `backend/app/invoices/ml.py` `_read_verified`, `test_ml_model_integrity.py` | — |
| 1.5.3 | Walidacja wejścia w zaufanej warstwie usług | ✅ | schematy Pydantic (`backend/app/schemas/`), FastAPI 422 | — |
| 1.5.4 | Kodowanie wyjścia blisko interpretera | ✅ | `backend/app/html_templates.py` (Jinja2 `select_autoescape`); `backend/app/exports.py` `append_row`/`csv_safe`; React | — |
| 1.6.1 | Polityka zarządzania kluczami | ⚠️ | `docs/operacje/RUNBOOK.md` §8 „Rotacja kluczy” | brak inwentarza kluczy z właścicielem i terminem; brak narzędzia przeszyfrowania (US-002) |
| 1.6.2 | Materiał kluczy chroniony przez używające go komponenty | ⚠️ | klucze tylko w env (`backend/app/config.py`); `.env.example` bez wartości (`test_env_example.py`) | brak sejfu (6.4.1); sekret TOTP w bazie jawnie (2.8.2) |
| 1.6.3 | Klucze i hasła wymienialne, z procesem przeszyfrowania | ⚠️ | `backend/app/crypto.py` (`MultiFernet` czyta stary klucz); `test_crypto_data_key.py`; RUNBOOK §8 | `DATA_ENCRYPTION_KEY` niewymagany na prod, brak narzędzia przeszyfrowania (US-002, R-05) |
| 1.6.4 | Klucze symetryczne nie trafiają do klienta | ✅ | sekrety wyłącznie w `backend/app/config.py`; panel nie dostaje kluczy (`frontend/src/api.ts` — cookies HttpOnly) | — |
| 1.7.1 | Wspólny format i podejście do logowania | ✅ | `backend/app/logfile.py` `LOG_FORMAT` (z `rid`); `backend/app/applog.py`; `backend/app/audit.py` `record` | — |
| 1.7.2 | Logi wysyłane bezpiecznie do zdalnego systemu | ⚠️ | błędy do Sentry — `backend/app/redaction.py` `init_sentry`; plik `LOG_FILE` lokalnie (`logfile.py`) | log żądań i audyt tylko w bazie na tym samym serwerze — brak zdalnej kopii logów |
| 1.8.1 | Dane wrażliwe zidentyfikowane i sklasyfikowane | ✅ | `KLASYFIKACJA_DANYCH.md` (klasy P/W/F/O/S, inwentarz) | — |
| 1.8.2 | Każda klasa ma wymagania ochrony | ⚠️ | `KLASYFIKACJA_DANYCH.md` („Klasy i zasady postępowania”) | zasada „S: w bazie tylko hash albo Fernet” nie jest spełniona dla sekretu TOTP (2.8.2) |
| 1.9.1 | Szyfrowanie komunikacji między komponentami | ❌ | `docker-compose.coolify.yml` (`DATABASE_URL` bez `sslmode`, sieć Dockera) | API↔PostgreSQL i API↔Ollama otwartym tekstem na jednym hoście; zewnętrzne usługi po HTTPS. Działanie: wyjątek „jeden host” w `RYZYKA.md` albo TLS do bazy |
| 1.9.2 | Komponenty weryfikują drugą stronę połączenia | ⚠️ | httpx weryfikuje certyfikaty domyślnie (`backend/app/teams.py` `post`, `backend/app/sms.py`); `powerbi_ssl_verify` w `config.py` | w sieci Dockera brak weryfikacji; `POWERBI_SSL_VERIFY=false` możliwe (dev) |
| 1.10.1 | Kontrola wersji z procedurą zmian i śledzeniem | ✅ | `.github/CODEOWNERS`; `.github/pull_request_template.md`; `CONTRIBUTING.md` (commity z ID historyjki) | ochrona gałęzi `main` w ustawieniach repo — ❓ |
| 1.11.1 | Komponenty opisane wg funkcji biznesowych | ✅ | `docs/architektura/ARCHITEKTURA.md`; `docs/architektura/API-TRASY.md` | — |
| 1.11.2 | Przepływy wysokiej wartości bez niesynchronizowanego stanu | ⚠️ | `security.py` `consume_refresh_token` (atomowy UPDATE); `test_container_lost_update.py` (409, ADR-0003) | limiter API i obecność w pamięci procesu (E-04); kontrakt jednej instancji `docs/JEDNA-INSTANCJA.md` |
| 1.12.2 | Pliki użytkowników serwowane jako pobranie | ✅ | `backend/app/routers/forwarding_files.py` `download_attachment` (`application/octet-stream`, attachment) | podgląd PDF `inline` w `backend/app/routers/document_tiles.py` `invoice_job_pdf` — pod CSP i `nosniff` |
| 1.14.1 | Segregacja komponentów o różnym poziomie zaufania | ⚠️ | `docker-compose.coolify.yml` (osobne usługi `db`, `app`); Ollama tylko wewnętrznie | parsery PDF/OCR i ML w procesie API (R-07) |
| 1.14.2 | Wdrożenie z weryfikacją integralności (podpisy, digesty) | ⚠️ | `Dockerfile.coolify` (obrazy bazowe po `sha256`); `test_dependency_lock.py`; gitleaks i Trivy z sumą sha256 (`.github/workflows/security.yml`) | `postgres:16-alpine` i `nginx:1.27-alpine` w `docker-compose.coolify.yml` bez digestu; sam deploy Coolify — ❓ |
| 1.14.3 | Pipeline ostrzega o podatnych komponentach | ✅ | `.github/workflows/ci-infra.yml` (pip-audit, npm audit); `security.yml` (Trivy); `.github/dependabot.yml` | — |
| 1.14.4 | Pipeline automatycznie buduje i weryfikuje wdrożenie | ✅ | `.github/workflows/ci-infra.yml` (build obrazu); `security.yml` job `trivy` (skan obrazu, bramka) | — |
| 1.14.5 | Wdrożenie izolowane (kontenery, sieć) | ✅ | `docker-compose.coolify.yml` (`expose` zamiast `ports`, `mem_limit`); `test_compose_limity.py` | — |
| 1.14.6 | Brak przestarzałych technologii klienckich | ✅ | `frontend/index.html` (tylko moduł Vite); CSP `script-src 'self'` w `backend/app/main.py` `SecurityHeadersMiddleware` | — |

## V2 Uwierzytelnianie

Pominięte (L3): 2.2.4–2.2.7, 2.8.7.

| ID | Wymaganie (krótko, własnymi słowami) | Status | Dowód | Uwagi / działanie |
|---|---|---|---|---|
| 2.1.1 | Hasło min. 12 znaków | ✅ | `backend/app/security.py` `validate_password_policy`; `password_min_length=12` w `backend/app/config.py` | — |
| 2.1.2 | Hasła 64+ znaków dozwolone, ponad 128 odrzucane | ⚠️ | `backend/app/schemas/auth.py` (`max_length=200` w `ChangePasswordIn`, `ResetPasswordIn`) | górna granica 200 zamiast 128; ustawić 128 |
| 2.1.3 | Hasło nie jest obcinane | ❌ | `security.py` `_bcrypt_bytes` (`[:72]` bajtów) | bcrypt bierze 72 bajty — dłuższe hasło obcięte po cichu. Działanie: wstępny skrót (HMAC-SHA256 → base64) przed bcrypt z migracją przy logowaniu albo argon2id |
| 2.1.4 | Dowolne znaki Unicode w haśle | ✅ | `security.py` `_bcrypt_bytes` (UTF-8), brak filtra znaków w `validate_password_policy` | — |
| 2.1.5 | Użytkownik może zmienić hasło | ✅ | `backend/app/routers/auth.py` `change_password` | — |
| 2.1.6 | Zmiana wymaga obecnego i nowego hasła | ✅ | `auth.py` `change_password` (`current_password`, wyjątek tylko dla hasła tymczasowego) | — |
| 2.1.7 | Sprawdzanie haseł z wycieków | ❌ | brak (przeszukane `backend/app`, `frontend/src`) | lista najczęstszych/wyciekłych haseł offline w `validate_password_policy` |
| 2.1.8 | Miernik siły hasła | ✅ | `frontend/src/PasswordInput.tsx` + `passwordStrength.ts` przy ustawianiu i zmianie hasła (`AuthPages.tsx`), `PasswordInput.dom.test.tsx` (US-090) | tylko podpowiedź — o przyjęciu decyduje serwer |
| 2.1.9 | Brak reguł składu hasła | ❌ | `security.py` `validate_password_policy` (wymóg litery i cyfry) | usunąć wymóg litery i cyfry, zostawić długość + listę zakazanych |
| 2.1.10 | Brak okresowej wymiany i historii haseł | ✅ | brak terminu ważności hasła w `backend/app/config.py` i modelu `User` | — |
| 2.1.11 | Wklejanie i menedżery haseł dozwolone | ✅ | `frontend/src/pages/LoginPage.tsx` (`autoComplete="current-password"`, brak blokady wklejania) | — |
| 2.1.12 | Możliwość podejrzenia wpisywanego hasła | ✅ | przycisk „pokaż / ukryj” w `PasswordInput.tsx` (logowanie, ustawienie i zmiana hasła), `aria-pressed` (US-090) | — |
| 2.2.1 | Ochrona przed automatyzacją (credential stuffing, brute force) | ✅ | `backend/app/rate_limit.py` `LoginRateLimiter` (IP, IP+login, konto); `auth.py` `login`; `test_login_limiter_db.py`, `test_login_limiter.py` | — |
| 2.2.2 | SMS/e-mail tylko jako słabszy czynnik | ✅ | SMS i e-mail nie są czynnikiem logowania; e-mail tylko do linku resetu (`auth.py` `forgot_password`) | — |
| 2.2.3 | Powiadomienie po zmianie danych uwierzytelniania | ⚠️ | `backend/app/login_devices.py` `check_login` (mail „nowe urządzenie”), `test_login_devices.py` | brak maila po zmianie hasła, resecie przez admina, włączeniu/wyłączeniu 2FA |
| 2.3.1 | Hasła startowe losowe, wygasające, jednorazowe | ⚠️ | `backend/app/routers/admin.py` `_generate_temp_password` (`secrets.token_urlsafe(9)`), `must_change_password`; `test_must_change_password.py` | hasło tymczasowe nie wygasa — dodać termin (np. 72 h) |
| 2.3.2 | Obsługa kluczy sprzętowych (FIDO/U2F) | ❌ | brak WebAuthn w `backend/app` | WebAuthn dla adminów (razem z US-019) |
| 2.3.3 | Instrukcje odnowienia uwierzytelniaczy z terminem | n/d | brak uwierzytelniaczy z terminem ważności | — |
| 2.4.1 | Hasła przechowywane solonym, jednokierunkowym KDF | ✅ | `security.py` `hash_password` (bcrypt) | — |
| 2.4.2 | Sól min. 32 bity | ✅ | `bcrypt.gensalt` w `hash_password` (sól 128 bitów) | — |
| 2.4.3 | PBKDF2 z odpowiednią liczbą iteracji | n/d | PBKDF2 nie jest używany (bcrypt) | — |
| 2.4.4 | bcrypt z odpowiednim kosztem | ✅ | `config.py` `bcrypt_rounds=12`; `backend/app/settings_check.py` (prod < 12 = odmowa startu) | — |
| 2.4.5 | Dodatkowa iteracja z tajną solą (pieprz) | ❌ | `security.py` `hash_password` (bez pieprzu) | razem z 2.1.3: HMAC z kluczem z env przed bcrypt |
| 2.5.1 | Sekret aktywacji/odzyskania nie wysyłany jawnym tekstem | ⚠️ | reset: link z tokenem (`auth.py` `forgot_password`); zaproszenie: `admin.py` `create_user` zwraca hasło tymczasowe, admin wysyła je mailem z Outlooka | hasło tymczasowe w treści maila; zastąpić linkiem jednorazowym jak przy resecie |
| 2.5.2 | Brak podpowiedzi i pytań „bezpieczeństwa” | ✅ | brak takich pól w `backend/app/schemas/auth.py` i modelu `User` | — |
| 2.5.3 | Odzyskiwanie nie ujawnia obecnego hasła | ✅ | `auth.py` `reset_password` (tylko nowe hasło) | — |
| 2.5.4 | Brak kont domyślnych i współdzielonych | ⚠️ | `settings_check.py` `INSECURE_DEFAULTS` (`admin123` blokuje prod); konto n8n bez logowania hasłem (`auth.py` `login`, `test_automation_hardening.py`) | współdzielone konta demo — tylko instancja demo (E-05) |
| 2.5.5 | Powiadomienie o zmianie czynnika uwierzytelniania | ⚠️ | jak 2.2.3 (`login_devices.py`) | dodać mail przy zmianie hasła i 2FA |
| 2.5.6 | Bezpieczny reset zapomnianego hasła | ✅ | `security.py` `create_password_reset_token`/`consume_password_reset_token` (32 B, SHA-256 w bazie, TTL 30 min, jednorazowy); `auth.py` `forgot_password` (zawsze 202); `test_hardening.py` `test_password_reset_flow` | — |
| 2.5.7 | Utrata 2FA: odzyskanie z weryfikacją tożsamości | ⚠️ | `backend/app/routers/system.py` `disable_2fa` (tylko inny admin, audyt) | brak opisanej procedury potwierdzenia tożsamości (RUNBOOK) |
| 2.6.1 | Kody zapasowe jednorazowe | ✅ | `auth.py` `_consume_backup_code` (hash usuwany z listy) | — |
| 2.6.2 | Kody zapasowe z min. 112 bitami albo solone | ✅ | `security.py` `generate_backup_codes` (12 znaków, 60 bitów), `hash_backup_code` (scrypt z 16-bajtową solą na kod), `test_backup_codes.py` (US-088) | kody wydane przed US-088 (SHA-256 bez soli) działają do ponownego wygenerowania w profilu |
| 2.6.3 | Kody zapasowe odporne na atak offline | ✅ | jak 2.6.2: 60 bitów + scrypt (N=2^14) na kod | jak 2.6.2 — stare kody do ponownego wygenerowania |
| 2.7.1 | SMS/telefon nie jako domyślny kanał OOB | n/d | brak uwierzytelniania poza pasmem (OOB) | — |
| 2.7.2 | Kody OOB wygasają po 10 min | n/d | jw. | — |
| 2.7.3 | Kody OOB jednorazowe | n/d | jw. | — |
| 2.7.4 | Kanał OOB bezpieczny | n/d | jw. | — |
| 2.7.5 | Weryfikator OOB trzyma tylko skrót | n/d | jw. | — |
| 2.7.6 | Kod OOB min. 20 bitów entropii | n/d | jw. | — |
| 2.8.1 | Kody TOTP mają określony czas życia | ✅ | `security.py` `totp_matched_step` (krok 30 s, okno ±1); `test_w14_security.py` | — |
| 2.8.2 | Klucze TOTP chronione | ❌ | `backend/app/models/dictionaries.py` `totp_secret` (String(64), jawnie) | szyfrować `crypto.encrypt` (Fernet, `DATA_ENCRYPTION_KEY`) |
| 2.8.3 | Zatwierdzone algorytmy OTP | ✅ | `security.py` `hotp`/`totp` (RFC 6238, HMAC-SHA1); `test_w14_security.py` `test_totp_rfc6238_vectors` | — |
| 2.8.4 | Kod TOTP użyty tylko raz | ✅ | `auth.py` `verify_2fa` (`totp_last_step`, odrzuca stary krok) | — |
| 2.8.5 | Ponowne użycie kodu zapisane i zgłoszone | ⚠️ | `auth.py` `verify_2fa` (audyt `login_failed` „błędny kod 2FA”) | brak powiadomienia właściciela konta |
| 2.8.6 | Fizyczny generator OTP da się unieważnić | n/d | brak sprzętowych generatorów OTP | — |
| 2.9.1 | Klucze kryptograficzne w weryfikacji chronione | n/d | brak uwierzytelniania urządzeniem kryptograficznym | — |
| 2.9.2 | Nonce wyzwania min. 64 bity | n/d | jw. | — |
| 2.9.3 | Zatwierdzone algorytmy dla urządzeń kryptograficznych | n/d | jw. | — |
| 2.10.1 | Sekrety między usługami nie są stałymi hasłami | ⚠️ | `backend/app/automation_policy.py` (`token_matches` z poprzednim tokenem, termin, CIDR) | token n8n statyczny; termin i CIDR opcjonalne (E-10, R-14) |
| 2.10.2 | Brak domyślnych poświadczeń usług | ✅ | `settings_check.py` `validate_settings` (domyślne sekrety i token n8n < 32 znaki = odmowa startu prod) | — |
| 2.10.3 | Hasła usług chronione przed odzyskaniem offline | ⚠️ | cache MSAL szyfrowany (`backend/app/powerbi.py` → `crypto.encrypt`) | pozostałe sekrety usług jawnie w env/Coolify (zob. 6.4.1) |
| 2.10.4 | Sekrety poza kodem źródłowym | ✅ | `backend/app/config.py` (z env); gitleaks w `.github/workflows/security.yml`; `test_env_example.py` | — |

## V3 Zarządzanie sesją

Pominięte (L3): 3.6.1, 3.6.2.

| ID | Wymaganie (krótko, własnymi słowami) | Status | Dowód | Uwagi / działanie |
|---|---|---|---|---|
| 3.1.1 | Token sesji nigdy w URL | ✅ | `security.py` `get_current_user` (cookie albo `Authorization`) | tokeny linków publicznych to nie sesja — zob. 13.1.3 |
| 3.2.1 | Nowy token przy uwierzytelnieniu | ✅ | `auth.py` `login`, `verify_2fa` (`create_access_token`, `issue_refresh_token`) | — |
| 3.2.2 | Token sesji min. 64 bity entropii | ✅ | JWT HS256 z kluczem ≥ 32 znaki (`settings_check.py`); JTI refresh `secrets.token_hex(32)` (`security.py` `issue_refresh_token`) | — |
| 3.2.3 | Token w przeglądarce przechowywany bezpiecznie | ✅ | cookies HttpOnly (`auth.py` `_set_auth_cookies`); `frontend/src/api.ts` (bez localStorage) | tokeny wracają też w treści JSON logowania — panel ich nie zapisuje |
| 3.2.4 | Token tworzony zatwierdzoną kryptografią | ✅ | PyJWT HS256, `secrets` (`security.py`) | — |
| 3.3.1 | Wylogowanie i wygaśnięcie unieważniają sesję | ✅ | `auth.py` `logout` (`session_version += 1`, `revoke_user_refresh_tokens`); `test_hardening.py` `test_logout_invalidates_access_token` | — |
| 3.3.2 | Ponowne uwierzytelnienie: L2 co 12 h albo po 30 min bezczynności | ❌ | `config.py` `refresh_token_days=14`; `security.py` `issue_refresh_token` (każda rotacja daje nowe 14 dni) | sesja aktywnego użytkownika nie wygasa nigdy. Działanie: limit bezwzględny (czas pierwszego logowania w refresh) i limit bezczynności albo świadomy wyjątek PO |
| 3.3.3 | Po zmianie hasła wylogowanie innych sesji | ✅ | `auth.py` `change_password`, `reset_password` (`revoke_user_refresh_tokens`) | — |
| 3.3.4 | Użytkownik widzi i kończy aktywne sesje | ✅ | `auth.py` `my_sessions`, `revoke_my_session`, `revoke_other_sessions`; `frontend/src/pages/ProfilePage.tsx` | luka z oceny wstępnej zamknięta |
| 3.4.1 | Cookie z atrybutem `Secure` | ⚠️ | `auth.py` `_set_auth_cookies` (`secure=settings.secure_cookies`); `settings_check.py` (prod bez `SECURE_COOKIES` = odmowa); `test_prod_without_https.py` | wyjątek `ALLOW_INSECURE_HTTP` (E-06) |
| 3.4.2 | Cookie z `HttpOnly` | ✅ | `auth.py` `_set_auth_cookies` | — |
| 3.4.3 | Cookie z `SameSite` | ✅ | `auth.py` `_set_auth_cookies` (`lax`) | — |
| 3.4.4 | Prefiks `__Host-` | ❌ | `security.py` `ACCESS_COOKIE = "timporye_access"` | E-07; `__Host-` dla cookie access (refresh ma `path=/api/auth`, więc wymagałby zmiany ścieżki) |
| 3.4.5 | Atrybut `path` przy współdzielonej domenie | ✅ | `auth.py` `_set_auth_cookies` (refresh `path="/api/auth"`); aplikacja na własnym hoście | — |
| 3.5.1 | Użytkownik może odwołać tokeny OAuth | n/d | brak OAuth dla użytkowników (M365 tylko app-only) | — |
| 3.5.2 | Tokeny sesji zamiast stałych kluczy API | ⚠️ | `security.py` `automation_user` (statyczny token n8n) | jak 2.10.1 |
| 3.5.3 | Tokeny bezstanowe podpisane, z ochroną przed nadużyciem | ✅ | `security.py` `_decode` (`algorithms=[ALGORITHM]`), kontrola `type` i `sv`; `test_idor_scoping.py` `test_refresh_token_is_not_access_token` | — |
| 3.7.1 | Pełna sesja albo ponowne uwierzytelnienie przed operacjami wrażliwymi | ⚠️ | `auth.py` `change_password` (wymaga obecnego hasła) | włączenie 2FA, wylogowanie sesji, operacje admina (reset hasła, wyłączenie 2FA, nadanie `view_all_companies`) bez ponownego hasła |

## V4 Kontrola dostępu

| ID | Wymaganie (krótko, własnymi słowami) | Status | Dowód | Uwagi / działanie |
|---|---|---|---|---|
| 4.1.1 | Reguły dostępu egzekwowane na serwerze | ✅ | `security.py` `require_roles`; `deps.py`; `test_permissions_matrix.py` (macierz `tests/permissions.yaml`) | — |
| 4.1.2 | Atrybuty użytkownika i danych nie do zmanipulowania przez klienta | ✅ | `security.py` `get_current_user` (rola i przypisania z bazy; kontekst podglądu w podpisanym JWT); `deps.py` `own_company_id` | — |
| 4.1.3 | Najmniejsze uprawnienia | ✅ | 7 ról w `tests/permissions.yaml`; `automation_policy.py` `check_service_account` (konto serwisowe bez roli admin) | — |
| 4.1.5 | Kontrola dostępu zawodzi bezpiecznie | ✅ | `deps.py` `_enforce_scope` (nieznany kształt → 403), `get_scoped` (brak i obcy rekord → to samo 404) | — |
| 4.2.1 | Ochrona przed IDOR | ✅ | `deps.py` `get_scoped`; `test_idor_scoping.py`, `test_idor_containers.py`, `test_isolation_guard.py` | izolacja tylko w kodzie (R-01, ADR-0006) |
| 4.2.2 | Ochrona przed CSRF | ✅ | `backend/app/csrf.py` `csrf_rejected` (`X-Requested-With` albo własny `Origin`/`Referer`); `SameSite=Lax`; `test_csrf.py` | żądanie bez `Origin` i `Referer` przechodzi (E-07) |
| 4.3.1 | Interfejsy administracyjne z MFA | ❌ | `config.py` `require_2fa_admin: bool = False`; `backend/app/twofa_policy.py` | wyjątek E-01 (R-11); US-019 — włączyć na produkcji |
| 4.3.2 | Brak listowania katalogów i metadanych (.git) | ✅ | `backend/app/main.py` `spa_response` (tylko pliki z builda, `is_relative_to`); `test_spa_assets.py`; `test_dockerignore.py` | — |
| 4.3.3 | Dodatkowa autoryzacja / rozdział obowiązków dla operacji wysokiej wartości | ⚠️ | podgląd „jako rola” tylko GET z audytem (`security.py` `get_current_user`); 2FA admina wyłącza tylko inny admin (`system.py` `disable_2fa`) | brak potwierdzenia hasłem/2FA dla krytycznych operacji admina |

## V5 Walidacja, sanityzacja i kodowanie

| ID | Wymaganie (krótko, własnymi słowami) | Status | Dowód | Uwagi / działanie |
|---|---|---|---|---|
| 5.1.1 | Ochrona przed zanieczyszczeniem parametrów HTTP | ✅ | typowane parametry FastAPI/Pydantic | — |
| 5.1.2 | Ochrona przed masowym przypisaniem | ✅ | osobne schematy wejścia (`backend/app/schemas/`); `admin.py` `update_user` (`model_dump(exclude_unset=True)`, `_partner_scope_reset`) | `PUT /api/auth/me/prefs` przyjmuje dowolny JSON (limit 64 KB, `auth.py` `save_my_prefs`) — tylko preferencje UI |
| 5.1.3 | Walidacja wejścia (pozytywna) | ⚠️ | Pydantic `Field` w `backend/app/schemas/` | wiele pól `str` bez `max_length` (T-15) |
| 5.1.4 | Dane strukturalne silnie typowane | ✅ | schematy Pydantic v2 | — |
| 5.1.5 | Przekierowania tylko na dozwolone adresy | ✅ | jedyny `RedirectResponse`: `main.py` `dzis_removed` (stała ścieżka) | — |
| 5.2.1 | Sanityzacja HTML z edytora WYSIWYG | n/d | brak edytora HTML; tekst renderowany przez React jako tekst | — |
| 5.2.2 | Sanityzacja danych niestrukturalnych (znaki, długość) | ⚠️ | jak 5.1.3 | limity długości pól tekstowych (T-15) |
| 5.2.3 | Ochrona przed wstrzyknięciem w nagłówki poczty | ⚠️ | `backend/app/mailer.py` (`MIMEMultipart`, temat przez `message["Subject"]`; Graph — JSON) | brak jawnej walidacji CR/LF w temacie; potwierdzić testem |
| 5.2.4 | Brak `eval` i dynamicznego wykonania kodu | ✅ | brak `eval(`/`exec(` w `backend/app`; Semgrep jako bramka (`security.yml`) | — |
| 5.2.5 | Ochrona przed wstrzyknięciem szablonu | ⚠️ | Jinja2 tylko z plików (`html_templates.py`); `backend/app/routers/doc_templates.py` `render_docs_message` — `str.format_map` na szablonie edytowanym w panelu | format string pozwala na dostęp do atrybutów wartości (`{container_no.__class__}`) — mała szkoda, ale wymienić na `string.Template` albo zamianę regexem |
| 5.2.6 | Ochrona przed SSRF | ⚠️ | adresy z konfiguracji lub stałe (`teams.py`, `sms.py`, `nbp.py`); Ollama: `backend/app/llm.py` `url_problem` | zdjęcie statku: `backend/app/routers/tracking.py` pobiera `thumburl` z odpowiedzi Wikimedia bez kontroli hosta — ograniczyć do `upload.wikimedia.org` |
| 5.2.7 | Ochrona przed skryptami w SVG | ✅ | `config.py` `allowed_upload_extensions` (bez `svg`); obrazy po sygnaturze (`file_signatures.py` `looks_like_image`) | — |
| 5.2.8 | Ochrona przed treścią języków szablonów (Markdown, CSS, XSL) | n/d | brak renderowania Markdown/XSL od użytkownika (`frontend/package.json` bez biblioteki Markdown) | — |
| 5.3.1 | Kodowanie wyjścia wg kontekstu | ✅ | Jinja2 autoescape (`html_templates.py`); React; `test_mail_html_escape.py` | — |
| 5.3.2 | Kodowanie zachowuje zestaw znaków | ✅ | JSON UTF-8 (FastAPI), `MIMEText(..., "utf-8")` w `mailer.py` | — |
| 5.3.3 | Ochrona przed XSS | ✅ | React; CSP `script-src 'self'` (`main.py`); jedyne `dangerouslySetInnerHTML` — statyczny `frontend/src/pages/LandingPage.tsx` (E-03) | — |
| 5.3.4 | Zapytania parametryzowane / ORM | ✅ | SQLAlchemy ORM; Semgrep p/owasp-top-ten (`security.yml`) | — |
| 5.3.5 | Bez parametryzacji — kodowanie kontekstowe | ✅ | f-stringi SQL tylko ze stałych identyfikatorów (`backend/app/backup_verify.py`, `backend/app/db_bootstrap.py`, R-16) | — |
| 5.3.6 | Ochrona przed wstrzyknięciem JSON | ✅ | serializacja przez Pydantic/`json.dumps` | — |
| 5.3.7 | Ochrona przed wstrzyknięciem LDAP | n/d | brak LDAP | — |
| 5.3.8 | Ochrona przed wstrzyknięciem poleceń systemu | ✅ | jedyny `subprocess` — `backup_verify.py` (stałe argumenty, bez `shell=True`) | — |
| 5.3.9 | Ochrona przed LFI/RFI | ✅ | `forwarding_files.py` `safe_filename`; `main.py` `spa_response` (`is_relative_to`) | — |
| 5.3.10 | Ochrona przed wstrzyknięciem XPath/XML | ✅ | jedyny parser XML wejścia: `sad_xml.py` (DTD odrzucane); brak XPath z danych użytkownika | — |
| 5.4.1 | Bezpieczne operacje na pamięci | n/d | Python i TypeScript — pamięć zarządzana | — |
| 5.4.2 | Łańcuchy formatujące bez wrogiego wejścia (C) | n/d | jw. (dla Pythona zob. 5.2.5) | — |
| 5.4.3 | Ochrona przed przepełnieniem liczb całkowitych | n/d | jw.; zakresy przez `Field(ge=, le=)` | — |
| 5.5.1 | Obiekty serializowane z kontrolą integralności | ✅ | `invoices/ml.py` `_signature`/`_read_verified` (HMAC-SHA256); `test_ml_model_integrity.py` | — |
| 5.5.2 | Parsery XML bez XXE | ⚠️ | `sad_xml.py` `_has_dtd`; `test_sad_xml.py`, `test_imports_malicious.py` | XLSX przez openpyxl bez `defusedxml` (brak w `backend/requirements.txt`) — dodać `defusedxml` |
| 5.5.3 | Brak deserializacji niezaufanych danych | ✅ | brak `pickle`; joblib tylko z podpisem (5.5.1) | — |
| 5.5.4 | JSON w przeglądarce przez `JSON.parse` | ✅ | `frontend/src/api.ts` (`fetch` + `.json()`) | — |

## V6 Kryptografia przechowywanych danych

Pominięte (L3): 6.2.7, 6.2.8, 6.3.3.

| ID | Wymaganie (krótko, własnymi słowami) | Status | Dowód | Uwagi / działanie |
|---|---|---|---|---|
| 6.1.1 | Regulowane dane osobowe zaszyfrowane w spoczynku | ⚠️ | kopie szyfrowane `age` (`test_backup_encryption.py`) | baza i wolumen `/data` bez szyfrowania w aplikacji; szyfrowanie dysku — ❓ wymaga sprawdzenia na serwerze |
| 6.1.2 | Dane medyczne zaszyfrowane | n/d | aplikacja nie przetwarza danych medycznych | — |
| 6.1.3 | Regulowane dane finansowe zaszyfrowane | n/d | brak rachunków, historii kredytowej (faktury handlowe to klasa F, nie dane regulowane) | — |
| 6.2.1 | Moduły kryptograficzne zawodzą bezpiecznie | ✅ | `backend/app/crypto.py` (Fernet: szyfrowanie uwierzytelnione, błąd = `InvalidToken`) | — |
| 6.2.2 | Sprawdzone algorytmy i biblioteki | ✅ | `cryptography` (Fernet), `bcrypt`, PyJWT, `hashlib` | — |
| 6.2.3 | Bezpieczne IV, tryby i konfiguracja szyfrów | ✅ | Fernet (AES-128-CBC + HMAC, losowy IV) w `crypto.py` | — |
| 6.2.4 | Algorytmy i klucze wymienialne | ⚠️ | `crypto.py` `MultiFernet` (rotacja klucza); `config.py` `bcrypt_rounds` | algorytm JWT stały w kodzie (`security.py` `ALGORITHM`) |
| 6.2.5 | Brak słabych algorytmów (ECB, MD5, SHA-1 poza zgodnością) | ✅ | brak MD5/ECB w `backend/app`; SHA-1 tylko w HMAC TOTP (`security.py` `hotp`, wymóg RFC 6238) | — |
| 6.2.6 | Nonce/IV nie są używane ponownie | ✅ | Fernet generuje losowy IV dla każdego szyfrowania (`crypto.py` `encrypt`) | — |
| 6.3.1 | Losowość kryptograficzna dla tokenów, nazw, haseł | ✅ | `secrets` w `security.py`, `admin.py`, `avizo_workflow.py`, `routers/mag1.py`, nazwy plików (`secrets.token_hex(8)`) | `random` tylko do opóźnień (`backend/app/tracking/ais.py`) |
| 6.3.2 | GUID w wersji 4 | ✅ | `uuid.uuid4` (`main.py` `RequestIDMiddleware`, `automation_events.py`) | identyfikatory, nie sekrety |
| 6.4.1 | Sejf na sekrety (key vault) | ❌ | sekrety w zmiennych środowiskowych (`config.py`, Coolify) | dla jednej instancji — świadomy wyjątek albo sejf (np. sekrety Dockera) |
| 6.4.2 | Materiał kluczy niedostępny dla aplikacji (HSM) | ❌ | klucze w pamięci procesu (`config.py` `secret_key`, `data_encryption_key`) | jak 6.4.1 — wyjątek z uzasadnieniem skali |

## V7 Obsługa błędów i logowanie

Pominięte (L3): 7.3.3. Usunięte w 4.0.3: 7.3.2.

| ID | Wymaganie (krótko, własnymi słowami) | Status | Dowód | Uwagi / działanie |
|---|---|---|---|---|
| 7.1.1 | Logi bez poświadczeń i tokenów sesji | ✅ | `backend/app/redaction.py` (`redact_tokens`, `_sentry_before_send`); `main.py` `AvizoTokenLogFilter`; `test_brama_log_bez_tokenow.py`; `test_audit_auth_retention.py` (`test_failed_login_unknown_user_does_not_store_full_input`) | — |
| 7.1.2 | Logi bez innych danych wrażliwych | ⚠️ | `audit.py` `_mask`; retencja logu logowań 90 dni (`config.py` `audit_auth_retention_days`) | imiona w wolnym tekście nie są maskowane (R-09) |
| 7.1.3 | Logowanie zdarzeń bezpieczeństwa | ✅ | `auth.py` (`login`, `login_failed`, `2fa_enabled`, `session_revoked`, `password_changed`, `account_locked`) przez `audit.record` | — |
| 7.1.4 | Wpis zawiera dane do analizy zdarzenia | ✅ | `audit.record` (użytkownik, IP w notatce, czas); `logfile.py` (`rid`); `applog.py` (`request_id`, IP, `user_id`) | — |
| 7.2.1 | Logowanie decyzji uwierzytelniania | ✅ | `auth.py` `login`, `verify_2fa` (sukces i porażka z IP) | — |
| 7.2.2 | Logowanie decyzji kontroli dostępu, w tym odmów | ✅ | `applog.py` `RequestLogMiddleware`/`record_request` (każda odpowiedź ≥ 400 z `user_id`, IP, `request_id`) | — |
| 7.3.1 | Kodowanie danych w logach (log injection) | ⚠️ | `logfile.py` `LOG_FORMAT` (tekst) | znaki nowej linii z danych użytkownika nie są kodowane w logu tekstowym; audyt w bazie jest strukturalny |
| 7.3.4 | Synchronizacja czasu | ❓ | — | wymaga sprawdzenia na serwerze (NTP) |
| 7.4.1 | Ogólny komunikat błędu z identyfikatorem dla wsparcia | ⚠️ | debug wyłączony (`main.py` — `FastAPI(...)` bez `debug`); `X-Request-ID` w `RequestIDMiddleware` | przy nieobsłużonym wyjątku odpowiedź 500 nie niesie `X-Request-ID` (middleware nie kończy się) — dodać handler 500 z identyfikatorem |
| 7.4.2 | Obsługa wyjątków w całym kodzie | ✅ | `backend/app/db_errors.py` `integrity_error_handler`; `test_broad_except_logging.py`; `test_integration_errors.py` (US-026) | — |
| 7.4.3 | Handler ostateczny dla nieobsłużonych wyjątków | ✅ | Starlette `ServerErrorMiddleware` + `applog.py` (traceback w dzienniku) + Sentry (`redaction.py` `init_sentry`) | — |

## V8 Ochrona danych

Pominięte (L3): 8.1.5, 8.1.6.

| ID | Wymaganie (krótko, własnymi słowami) | Status | Dowód | Uwagi / działanie |
|---|---|---|---|---|
| 8.1.1 | Dane wrażliwe nie są buforowane w komponentach serwera | ✅ | brak cache po stronie aplikacji; `Cache-Control: no-store` na `/api/*` zabrania też buforowania w proxy (US-087) | — |
| 8.1.2 | Kopie tymczasowe danych wrażliwych chronione lub usuwane | ⚠️ | upload czytany do pamięci z limitem (`forwarding_files.py` `read_upload_capped`); sprzątanie osieroconych plików (`backend/app/orphan_files.py`) | brak retencji dokumentów handlowych (O-3) |
| 8.1.3 | Minimum parametrów w żądaniu | ✅ | sesja tylko w cookie (`frontend/src/api.ts`); brak ukrytych pól z danymi | — |
| 8.1.4 | Wykrywanie i alert przy nienormalnej liczbie żądań | ⚠️ | limit API 429 (`main.py` `RateLimitMiddleware`); alert adminów przy blokadzie konta (`auth.py` `_alert_account_lock`); alert 80 % budżetu SMS (`test_sms_budget.py`) | brak alertu przy zalewie API z jednego IP |
| 8.2.1 | Nagłówki zakazujące cache dla danych wrażliwych | ✅ | `main.py` `SecurityHeadersMiddleware`: `Cache-Control: no-store` dla `/api/*` (trasy z własną polityką ją zachowują); test `test_security_headers.py::test_api_responses_not_cached` | zrobione w US-087 |
| 8.2.2 | Brak danych wrażliwych w pamięci przeglądarki | ✅ | `localStorage` tylko preferencje UI (`frontend/src/prefs.ts`, `frontend/src/pages/queue/useViewPrefs.ts`); tokeny w cookies HttpOnly | — |
| 8.2.3 | Dane klienta czyszczone po zakończeniu sesji | ✅ | `auth.py` `clear_auth_cookies`; brak danych sesji w pamięci przeglądarki (8.2.2); PWA bez service workera (`frontend/public/manifest.json`) | — |
| 8.3.1 | Dane wrażliwe w treści/nagłówkach, nie w query string | ⚠️ | tokeny linków maskowane w logach i `no-referrer` (`redaction.py`, `main.py`) | token resetu hasła w `?token=` (`auth.py` `forgot_password`), tokeny linków publicznych w ścieżce (13.1.3) |
| 8.3.2 | Użytkownik może wyeksportować/usunąć swoje dane | ⚠️ | `backend/app/routers/data_subject.py` (eksport, anonimizacja kierowcy); `test_data_subject.py`; usunięcie konta = anonimizacja (`admin.py` `delete_user`) | tylko przez admina na wniosek (RUNBOOK §9), bez samoobsługi |
| 8.3.3 | Jasna informacja o przetwarzaniu danych osobowych | ⚠️ | klauzula RODO w formularzu kierowców (`frontend/src/i18n/pl.modules.ts` `av2Rodo`) | brak informacji dla użytkowników panelu; `RODO.md` mówi „brak tekstu” w formularzu awizacji — nieaktualne (US-012) |
| 8.3.4 | Dane wrażliwe zidentyfikowane, jest polityka | ✅ | `KLASYFIKACJA_DANYCH.md`; `docs/bezpieczenstwo/RODO.md` | — |
| 8.3.5 | Dostęp do danych wrażliwych audytowany | ⚠️ | audyt GET w podglądzie admina (`security.py` `get_current_user`); audyt pobrania ZIP (`backend/app/routers/documents.py`, `attachments_zip`) | zwykłe odczyty danych osobowych bez audytu |
| 8.3.6 | Dane wrażliwe w pamięci nadpisywane po użyciu | n/d | Python nie pozwala niezawodnie zerować pamięci obiektów `str` | — |
| 8.3.7 | Dane wymagające szyfrowania — szyfrowanie z integralnością | ⚠️ | Fernet dla cache MSAL (`powerbi.py`, `crypto.py`) | sekret TOTP jawnie (2.8.2) |
| 8.3.8 | Retencja danych osobowych z automatycznym usuwaniem | ⚠️ | `backend/app/retention.py`; `config.py` (`driver_data_retention_days`, `audit_auth_retention_days`, `token_retention_days`); `test_retention_tokens_sms.py`, `test_audit_auth_retention.py` | kontakty partnerów i dokumenty handlowe bez retencji (O-3, `RODO.md`) |

## V9 Komunikacja

Pominięte (L3): 9.2.5.

| ID | Wymaganie (krótko, własnymi słowami) | Status | Dowód | Uwagi / działanie |
|---|---|---|---|---|
| 9.1.1 | TLS dla wszystkich połączeń klientów, bez spadku do HTTP | ❓ | HSTS przy `SECURE_COOKIES` (`main.py` `SecurityHeadersMiddleware`); `test_security_headers.py` `test_hsts_only_behind_https` | TLS kończy proxy Coolify — wymaga sprawdzenia na serwerze; wyjątek E-06 |
| 9.1.2 | Tylko silne zestawy szyfrów | ❓ | — | wymaga sprawdzenia na serwerze (np. testssl.sh na domenie) |
| 9.1.3 | Tylko TLS 1.2 i 1.3 | ❓ | — | wymaga sprawdzenia na serwerze |
| 9.2.1 | Połączenia z zaufanymi certyfikatami | ⚠️ | httpx z weryfikacją certyfikatów domyślnie (`teams.py`, `sms.py`, `sharepoint.py`) | `POWERBI_SSL_VERIFY=false` możliwe (`config.py`, tylko dev) |
| 9.2.2 | Szyfrowanie wszystkich połączeń, także do bazy i monitoringu | ❌ | `docker-compose.coolify.yml` (`DATABASE_URL` bez TLS); `OLLAMA_URL` po HTTP w sieci Dockera | jak 1.9.1 |
| 9.2.3 | Połączenia z systemami zewnętrznymi uwierzytelnione | ✅ | Graph (MSAL, `mailer.py`), SMSAPI (token, `sms.py`), webhook n8n (HMAC, `automation_events.py`), domyślne adresy HTTPS/WSS (`config.py`) | — |
| 9.2.4 | Sprawdzanie unieważnienia certyfikatów (OCSP) | ❓ | — | wymaga sprawdzenia na serwerze (proxy) |

## V10 Złośliwy kod

Pominięte (L3): 10.1.1, 10.2.3–10.2.6.

| ID | Wymaganie (krótko, własnymi słowami) | Status | Dowód | Uwagi / działanie |
|---|---|---|---|---|
| 10.2.1 | Brak nieautoryzowanego „dzwonienia do domu” | ✅ | zewnętrzne połączenia opisane w `THREAT_MODEL.md` (diagram); Sentry wyłączony domyślnie (`config.py` `sentry_dsn=""`) | — |
| 10.2.2 | Brak zbędnych uprawnień (kamera, mikrofon, lokalizacja) | ✅ | `main.py` `Permissions-Policy: camera=(self), microphone=(), geolocation=()`; `test_security_headers.py` | — |
| 10.3.1 | Auto-aktualizacja przez bezpieczny kanał z podpisem | n/d | brak mechanizmu auto-aktualizacji (PWA bez service workera) | — |
| 10.3.2 | Integralność kodu, brak ładowania kodu z niezaufanych źródeł | ✅ | `frontend/index.html` (bez zewnętrznych skryptów); CSP `script-src 'self'`; `frontend/package-lock.json` (`integrity`); `test_dependency_lock.py` | — |
| 10.3.3 | Ochrona przed przejęciem subdomeny | ❓ | — | wymaga sprawdzenia DNS |

## V11 Logika biznesowa

| ID | Wymaganie (krótko, własnymi słowami) | Status | Dowód | Uwagi / działanie |
|---|---|---|---|---|
| 11.1.1 | Kroki procesu w ustalonej kolejności | ✅ | maszyna statusów — `test_status_flow.py`; awizacja dwuetapowa (`backend/app/avizo_workflow.py`) | — |
| 11.1.2 | Kroki w realistycznym, ludzkim czasie | ⚠️ | tylko limity żądań (`main.py`, `public_guards.py`) | brak kontroli czasu kroków (np. formularz awizacji wysłany w < 1 s) |
| 11.1.3 | Limity dla konkretnych akcji biznesowych | ✅ | dzienny limit SMS (`test_sms_budget.py`); limit asystenta (`test_llm_limits.py`); termin linków publicznych (`test_public_link_ttl.py`) | — |
| 11.1.4 | Ochrona przed nadmiernymi wywołaniami (eksfiltracja, DoS) | ✅ | `main.py` `RateLimitMiddleware` (300/min/IP); `public_guards.py` `public_limit` (30/min); `test_public_routes_guard.py`; `test_rate_limit.py` | limiter w pamięci procesu (E-04) |
| 11.1.5 | Limity wynikające z modelu zagrożeń | ✅ | bramka numeru w PDF (`test_document_gate.py`); limity ZIP (`archive_upload.py`); budżet SMS | — |
| 11.1.6 | Brak wyścigów (TOCTOU) w operacjach wrażliwych | ✅ | `security.py` `consume_refresh_token` (atomowy UPDATE); `test_refresh_grace.py`; `test_container_lost_update.py`, `test_status_lost_update.py` | — |
| 11.1.7 | Monitorowanie nietypowej aktywności biznesowej | ⚠️ | alert blokady konta (`auth.py` `_alert_account_lock`); strażnik automatów (`backend/app/automation_watchdog.py`) | brak reguł anomalii (np. masowe pobieranie danych) |
| 11.1.8 | Konfigurowalne alerty o atakach i anomaliach | ⚠️ | alert typu „system” wyłączalny w matrycy reguł (`auth.py` `_alert_account_lock` → `notify`) | jak 11.1.7 |

## V12 Pliki i zasoby

| ID | Wymaganie (krótko, własnymi słowami) | Status | Dowód | Uwagi / działanie |
|---|---|---|---|---|
| 12.1.1 | Brak plików zapychających dysk | ✅ | `forwarding_files.py` `read_upload_capped` (`MAX_UPLOAD_MB`); `test_upload_limits.py` (`test_no_uncapped_reads_in_routers`) | — |
| 12.1.2 | Archiwa sprawdzane na bomby dekompresyjne | ✅ | `archive_upload.py` (suma rozpakowania, współczynnik > 100×, odczyt do limitu); `test_imports_malicious.py`; `test_upload_limits.py` `test_xlsx_zip_bomb_rejected` | — |
| 12.1.3 | Limit rozmiaru i liczby plików na użytkownika | ❌ | brak limitu na użytkownika (tylko na plik i na archiwum, `config.py` `archive_zip_max_files`) | dzienny limit wgrań na konto |
| 12.2.1 | Typ pliku sprawdzany po zawartości | ⚠️ | `file_signatures.py` `content_matches`; `test_file_signatures.py` | .doc, .xls, .eml, .msg bez weryfikacji (`UNVERIFIED`, R-03) |
| 12.3.1 | Nazwa pliku od użytkownika nie trafia wprost do systemu plików | ✅ | `forwarding_files.py` `safe_filename`; nazwa na dysku z `secrets.token_hex(8)` | — |
| 12.3.2 | Nazwa pliku nie pozwala na LFI | ✅ | jak 12.3.1; pobieranie po `stored_name` z bazy (`download_attachment`) | — |
| 12.3.3 | Nazwa pliku nie pozwala na RFI/SSRF | ✅ | nazwy plików nigdy nie są używane jako URL | — |
| 12.3.4 | Ochrona przed Reflective File Download | ✅ | `download_attachment` (`application/octet-stream`, `Content-Disposition: attachment`); `nosniff` | — |
| 12.3.5 | Metadane pliku nie trafiają do poleceń systemu | ✅ | jedyny `subprocess` bez danych plików (`backup_verify.py`) | — |
| 12.3.6 | Brak dołączania funkcji z niezaufanych źródeł | ✅ | brak CDN (`frontend/index.html`); zależności z hashami (`test_dependency_lock.py`) | — |
| 12.4.1 | Pliki niezaufane poza katalogiem webowym, ograniczone uprawnienia | ✅ | `config.py` `uploads_dir` (poza `frontend/dist`); serwowane tylko przez trasy z `get_scoped` | — |
| 12.4.2 | Skanowanie antywirusowe plików | ❌ | brak AV w `backend/app` | ClamAV w osobnym kontenerze (R-03) |
| 12.5.1 | Serwer nie wydaje plików kopii/źródeł (.bak, .swp) | ✅ | `main.py` `spa_response` (tylko pliki z builda); `test_dockerignore.py` | — |
| 12.5.2 | Wgrane pliki nigdy nie wykonują się jako HTML/JS | ✅ | `download_attachment` (`application/octet-stream`); `nosniff` (`main.py`) | — |
| 12.6.1 | Lista dozwolonych celów żądań wychodzących | ⚠️ | cele z konfiguracji (`config.py`) lub stałe adresy (`nbp.py`, `tracking/weather.py`) | brak ograniczenia ruchu wychodzącego na poziomie serwera — ❓; zob. 5.2.6 |

## V13 API i usługi sieciowe

| ID | Wymaganie (krótko, własnymi słowami) | Status | Dowód | Uwagi / działanie |
|---|---|---|---|---|
| 13.1.1 | Te same kodowania i parsery we wszystkich komponentach | ✅ | jeden stos FastAPI + Pydantic, JSON UTF-8 | — |
| 13.1.3 | Adresy API bez danych wrażliwych (klucze, tokeny) | ⚠️ | tokeny linków publicznych w ścieżce, maskowane w logach (`redaction.py`, `test_brama_log_bez_tokenow.py`), `no-referrer` (`main.py`), limit 90 dni (`test_public_link_ttl.py`) | świadoma decyzja (link bez konta); token resetu w query (8.3.1) |
| 13.1.4 | Autoryzacja na poziomie trasy i zasobu | ✅ | `require_roles` (trasa) + `get_scoped` (zasób); `test_permissions_matrix.py`, `test_isolation_guard.py` | — |
| 13.1.5 | Odrzucanie nieoczekiwanych typów treści | ⚠️ | publiczne POST: 415 (`public_guards.py` `json_origin_guard`) | trasy z logowaniem — tylko walidacja FastAPI (422, nie 415) |
| 13.2.1 | Dozwolone metody HTTP adekwatne do akcji | ✅ | metoda w macierzy `tests/permissions.yaml`; FastAPI 405 dla innych | — |
| 13.2.2 | Walidacja schematu JSON przed przyjęciem | ✅ | schematy Pydantic w sygnaturach tras | — |
| 13.2.3 | REST z cookie chroniony przed CSRF | ✅ | `csrf.py`; `test_csrf.py` | E-07 |
| 13.2.5 | Jawna kontrola nagłówka `Content-Type` | ⚠️ | jak 13.1.5 | — |
| 13.2.6 | Nagłówki i treść komunikatów chronione w tranzycie | ⚠️ | HMAC zdarzeń do n8n (`automation_events.py`) | ruch przychodzący zależy od TLS proxy — ❓ |
| 13.3.1 | Walidacja schematu XSD (SOAP) | n/d | brak usług SOAP | — |
| 13.3.2 | Podpis WS-Security | n/d | brak usług SOAP | — |
| 13.4.1 | GraphQL: lista zapytań / limit głębokości | n/d | brak GraphQL | — |
| 13.4.2 | GraphQL: autoryzacja w warstwie logiki | n/d | brak GraphQL | — |

## V14 Konfiguracja

Pominięte (L3): 14.1.5. Usunięte w 4.0.3: 14.3.1.

| ID | Wymaganie (krótko, własnymi słowami) | Status | Dowód | Uwagi / działanie |
|---|---|---|---|---|
| 14.1.1 | Powtarzalny, bezpieczny build i wdrożenie | ✅ | `.github/workflows/` (ci-backend, ci-frontend, ci-infra, security); `Dockerfile.coolify`; `docs/DEPLOY_COOLIFY.md` | — |
| 14.1.2 | Flagi kompilatora chroniące przed przepełnieniem | n/d | projekt nie kompiluje kodu natywnego | — |
| 14.1.3 | Utwardzona konfiguracja serwera i frameworka | ⚠️ | fail-fast prod (`settings_check.py`); `/docs` wyłączone na prod (`main.py` `_docs_kw`); kontener bez roota | `ALLOWED_HOSTS` puste w `docker-compose.coolify.yml` (E-08, R-17); utwardzenie hosta i Coolify — ❓ |
| 14.1.4 | Odtworzenie wdrożenia ze skryptów/runbooka w rozsądnym czasie | ✅ | `docs/operacje/RUNBOOK.md` (wdrożenie, odtworzenie); `backend/app/backup_verify.py` (próbne odtworzenie); `test_backup_scripts.py` | — |
| 14.2.1 | Komponenty aktualne, kontrola zależności w buildzie | ✅ | `ci-infra.yml` (pip-audit, npm audit); `security.yml` (Trivy, bramka); `.github/dependabot.yml` | — |
| 14.2.2 | Usunięte zbędne funkcje, dokumentacja, przykłady | ✅ | `main.py` `_docs_kw` (bez `/docs`, `/openapi.json` na prod); `test_dockerignore.py` | — |
| 14.2.3 | SRI dla zasobów z CDN | n/d | brak zasobów z CDN (`frontend/index.html`) | — |
| 14.2.4 | Komponenty z zaufanych, utrzymywanych repozytoriów | ✅ | PyPI z hashami (`backend/requirements.txt`), npm z `integrity`; `test_dependency_lock.py` | — |
| 14.2.5 | Inwentarz komponentów (SBOM) | ✅ | `security.yml` (SBOM CycloneDX obrazu); `test_sbom_obrazu.py` | — |
| 14.2.6 | Biblioteki zewnętrzne izolowane (sandbox) | ⚠️ | OCR/ekstrakcja faktur w pętli tła (`config.py` `invoice_ocr_in_background`) | parsery PDF/OCR/ML w procesie API (R-07) |
| 14.3.2 | Tryby debug wyłączone na produkcji | ✅ | `main.py` (`FastAPI` bez `debug`); `Dockerfile.coolify` CMD bez `--reload` | — |
| 14.3.3 | Nagłówki bez szczegółowych wersji komponentów | ⚠️ | uvicorn wysyła `server: uvicorn` bez wersji (`Dockerfile.coolify` CMD bez `--no-server-header`) | `frontend/nginx.conf` bez `server_tokens off`; `/api/health` publikuje SHA builda — dodać `--no-server-header` i `server_tokens off` |
| 14.4.1 | `Content-Type` z bezpiecznym kodowaniem | ✅ | `JSONResponse` (`application/json`); pliki z jawnym `media_type` (`download_attachment`) | — |
| 14.4.2 | Odpowiedzi API z `Content-Disposition: attachment` | ✅ | `main.py` `SecurityHeadersMiddleware`: JSON z `/api/*` z `attachment; filename="api.json"`, pobierania plików zachowują własną nazwę; `test_security_headers.py::test_json_api_served_as_attachment` (US-089) | — |
| 14.4.3 | Nagłówek CSP | ✅ | `main.py` `SecurityHeadersMiddleware.CSP`; `frontend/nginx.conf`; `test_security_headers.py` | `style-src 'unsafe-inline'` |
| 14.4.4 | `X-Content-Type-Options: nosniff` | ✅ | `main.py` `SecurityHeadersMiddleware.HEADERS` | — |
| 14.4.5 | HSTS na wszystkich odpowiedziach i subdomenach | ⚠️ | `main.py` (`max-age=31536000; includeSubDomains` przy `SECURE_COOKIES`); `test_security_headers.py` | brak HSTS przy wyjątku E-06 |
| 14.4.6 | Odpowiedni `Referrer-Policy` | ✅ | `main.py` (`strict-origin-when-cross-origin`; `no-referrer` dla `/avizo/`, `/mag1/`) | — |
| 14.4.7 | Treść nie do osadzenia w obcej stronie | ✅ | `main.py` (`X-Frame-Options: DENY`, `frame-ancestors 'none'`) | — |
| 14.5.1 | Tylko używane metody HTTP; nieprawidłowe logowane | ✅ | FastAPI 405 dla niezdefiniowanych metod; `applog.py` zapisuje odpowiedzi ≥ 400 | — |
| 14.5.2 | `Origin` nie służy do uwierzytelniania ani autoryzacji | ✅ | `csrf.py` (`Origin` tylko jako warstwa CSRF; tożsamość z JWT w `security.py`) | — |
| 14.5.3 | CORS ze ścisłą listą, bez `null` | ✅ | `main.py` (`CORSMiddleware` tylko z `CORS_ORIGINS`; `*` wyłącza credentials i loguje ostrzeżenie) | — |
| 14.5.4 | Nagłówki od zaufanego proxy uwierzytelnione | ✅ | `rate_limit.py` `_is_trusted_proxy`, `client_ip` (XFF tylko z `TRUSTED_PROXY_CIDRS`); `test_trusted_proxy_cidrs.py` | — |

---

## Podsumowanie

### Liczba wymagań wg statusu

| Rozdział | ✅ | ⚠️ | ❌ | n/d | ❓ | Razem |
|---|---|---|---|---|---|---|
| V1 Architektura, projekt i model zagrożeń | 24 | 13 | 1 | 0 | 0 | 38 |
| V2 Uwierzytelnianie | 22 | 10 | 8 | 12 | 0 | 52 |
| V3 Zarządzanie sesją | 12 | 3 | 2 | 1 | 0 | 18 |
| V4 Kontrola dostępu | 7 | 1 | 1 | 0 | 0 | 9 |
| V5 Walidacja, sanityzacja i kodowanie | 18 | 6 | 0 | 6 | 0 | 30 |
| V6 Kryptografia przechowywanych danych | 7 | 2 | 2 | 2 | 0 | 13 |
| V7 Obsługa błędów i logowanie | 7 | 3 | 0 | 0 | 1 | 11 |
| V8 Ochrona danych | 6 | 8 | 0 | 1 | 0 | 15 |
| V9 Komunikacja | 1 | 1 | 1 | 0 | 4 | 7 |
| V10 Złośliwy kod | 3 | 0 | 0 | 1 | 1 | 5 |
| V11 Logika biznesowa | 5 | 3 | 0 | 0 | 0 | 8 |
| V12 Pliki i zasoby | 11 | 2 | 2 | 0 | 0 | 15 |
| V13 API i usługi sieciowe | 5 | 4 | 0 | 4 | 0 | 13 |
| V14 Konfiguracja | 17 | 4 | 0 | 2 | 0 | 23 |
| **Razem** | **145** | **60** | **17** | **29** | **6** | **257** |

Spełnione 145 z 222 wymagań, które dotyczą aplikacji (bez n/d i ❓) — 65 % (po US-087, US-088 i US-089; wcześniej 140, 63 %).

### Luki ❌ — proponowane działania

| ID | Luka | Proponowane działanie | Ryzyko / historyjka |
|---|---|---|---|
| 1.9.1, 9.2.2 | Połączenia do PostgreSQL i Ollamy otwartym tekstem w sieci Dockera | wyjątek „jeden host” w `RYZYKA.md` albo `sslmode=require` | nowe ryzyko (do wpisania) |
| 2.1.3, 2.4.5 | bcrypt obcina hasło do 72 bajtów; brak pieprzu | HMAC-SHA256 z kluczem z env przed bcrypt, migracja przy logowaniu | nowe (do historyjki) |
| 2.1.7, 2.1.8, 2.1.9, 2.1.12 | Brak listy wyciekłych haseł i miernika siły, reguła „litera + cyfra”, brak „pokaż hasło” | jedna historyjka „polityka haseł wg ASVS”: lista zakazanych offline, wskaźnik, przełącznik, usunięcie reguły składu | nowe |
| 2.3.2 | Brak kluczy sprzętowych (WebAuthn) | WebAuthn przynajmniej dla adminów | E-01, US-019 |
| 2.6.2, 2.6.3 | ~~Kody zapasowe 2FA: 40 bitów, SHA-256 bez soli~~ | zrobione: 60 bitów + scrypt z solą (US-088); stare kody do ponownego wygenerowania | zamknięte |
| 2.8.2 | Sekret TOTP jawnie w bazie | szyfrowanie `crypto.encrypt` + migracja | R-05 / US-002 (ten sam klucz danych) |
| 3.3.2 | Sesja bez limitu bezwzględnego i bezczynności | limit 12 h od logowania i 30 min bezczynności albo wyjątek PO | nowe |
| 3.4.4 | Brak prefiksu `__Host-` | `__Host-` dla cookie access | E-07 |
| 4.3.1 | MFA adminów nieobowiązkowe | `REQUIRE_2FA_ADMIN=true` na produkcji | E-01, R-11, US-019 |
| 6.4.1, 6.4.2 | Brak sejfu / HSM na klucze | świadomy wyjątek (skala jednej instancji) z przeglądem | nowy wyjątek (do wpisania) |
| 8.2.1 | ~~Brak `Cache-Control: no-store` w odpowiedziach API~~ | zrobione: nagłówek w `SecurityHeadersMiddleware` (US-087) | zamknięte |
| 12.1.3 | Brak limitu wgrań na użytkownika | dzienny limit liczby i rozmiaru plików na konto | R-07 |
| 12.4.2 | Brak skanowania antywirusowego | ClamAV w osobnym kontenerze | R-03, US-004 |
| 14.4.2 | ~~Odpowiedzi API bez `Content-Disposition`~~ | zrobione (US-089) | zamknięte |

### Luki ⚠️ — proponowane działania

| ID | Luka | Proponowane działanie | Ryzyko / historyjka |
|---|---|---|---|
| 1.1.2 | Nowe przepływy (US-075, US-076) bez STRIDE | dopisać wiersze do `THREAT_MODEL.md` | proces (krok 2) |
| 1.2.2, 1.2.4, 2.10.1, 3.5.2 | Token n8n statyczny; HMAC i CIDR opcjonalne | ustawić CIDR, termin i sekret HMAC na produkcji | E-10, R-14 |
| 1.5.1, 5.1.3, 5.2.2 | Pola tekstowe bez `max_length` | limity długości w schematach | T-15 |
| 1.6.1, 1.6.2, 1.6.3, 6.2.4 | Brak narzędzia przeszyfrowania, `DATA_ENCRYPTION_KEY` niewymagany | dokończyć US-002 | R-05, US-002 |
| 1.7.2 | Logi i audyt tylko na tym samym serwerze | wysyłka logów poza serwer albo w kopii off-site | R-10, US-013 |
| 1.8.2, 8.3.7 | Sekret TOTP łamie zasadę klasy S | jak 2.8.2 | R-05 |
| 1.9.2, 9.2.1 | `POWERBI_SSL_VERIFY=false` możliwe | odmowa startu prod z `false` | nowe |
| 1.11.2 | Stan w pamięci procesu | bez zmian przy jednej instancji | E-04 |
| 1.14.1, 14.2.6 | Parsery PDF/OCR/ML w procesie API | osobny worker | R-07, US-006 |
| 1.14.2 | Obrazy `postgres`, `nginx` bez digestu w compose | przypiąć po `sha256` | R-08 |
| 2.1.2 | Górna granica hasła 200 zamiast 128 | `max_length=128` | nowe |
| 2.2.3, 2.5.5, 2.8.5 | Brak maila po zmianie hasła/2FA i po ponownym użyciu kodu | rozszerzyć `login_devices` / powiadomienia | US-075 (rozszerzenie) |
| 2.3.1, 2.5.1 | Hasło tymczasowe bez terminu, wysyłane mailem | link jednorazowy z terminem zamiast hasła | nowe |
| 2.5.4 | Współdzielone konta demo | bez zmian (tylko demo) | E-05, R-12 |
| 2.5.7 | Brak procedury potwierdzenia tożsamości przy utracie 2FA | opis w RUNBOOK | US-019 |
| 2.10.3, 6.1.1 | Sekrety usług i baza bez szyfrowania w spoczynku | szyfrowanie dysku na serwerze (sprawdzić) | R-10 |
| 3.4.1, 14.4.5 | `Secure` i HSTS wyłączane przez `ALLOW_INSECURE_HTTP` | zamknąć wyjątek po HTTPS | E-06 |
| 3.7.1, 4.3.3 | Operacje admina bez ponownego uwierzytelnienia | potwierdzenie hasłem/2FA dla resetu hasła, 2FA, `view_all_companies` | E-01, US-019 |
| 5.2.3 | Brak testu CR/LF w temacie maila | test i odrzucenie CR/LF | nowe |
| 5.2.5 | `str.format_map` na edytowalnym szablonie | `string.Template` albo zamiana regexem | nowe |
| 5.2.6, 12.6.1 | `thumburl` z Wikimedia bez kontroli hosta; brak listy celów ruchu wychodzącego | ograniczyć host; egress na serwerze | nowe |
| 5.5.2 | openpyxl bez `defusedxml` | dodać `defusedxml` do zależności | R-07, US-006 |
| 7.1.2 | Imiona w wolnym tekście nie maskowane | zasada „nie wstawiać” + przegląd | R-09, US-012 |
| 7.3.1 | Log tekstowy bez kodowania nowych linii | filtr zamieniający `\r`/`\n` w danych | nowe |
| 7.4.1 | Odpowiedź 500 bez identyfikatora żądania | handler wyjątków z `X-Request-ID` | nowe |
| 8.1.1 | ~~Brak `no-store` (jak 8.2.1)~~ | zrobione (US-087) | zamknięte |
| 8.1.2, 8.3.8 | Dokumenty handlowe bez retencji | decyzja PO o retencji | O-3, R-09 |
| 8.1.4, 11.1.7, 11.1.8 | Brak alertów anomalii API i biznesowych | alert przy serii 429 z jednego IP / masowym pobieraniu | E-04 |
| 8.3.1, 13.1.3 | Token resetu w query, tokeny linków w ścieżce | token resetu we fragmencie `#` albo POST | R-06 |
| 8.3.2 | Eksport/usunięcie danych tylko przez admina | samoobsługa w Profilu | R-09, US-012 |
| 8.3.3 | Brak informacji o przetwarzaniu dla użytkowników panelu; `RODO.md` nieaktualny | tekst w panelu, aktualizacja `RODO.md` | R-09, US-012 |
| 8.3.5 | Odczyty danych osobowych bez audytu | audyt odczytu karty kierowcy i eksportów | R-09 |
| 11.1.2 | Brak kontroli „ludzkiego czasu” kroków | minimalny czas wypełnienia formularza awizacji | R-06 |
| 12.2.1 | .doc/.xls/.eml/.msg bez weryfikacji zawartości | jak w R-03 | R-03, US-004 |
| 13.1.5, 13.2.5 | Trasy z logowaniem bez jawnego 415 | middleware wymuszający `application/json` dla zapisów JSON | nowe |
| 13.2.6 | Ruch przychodzący zależy od TLS proxy | potwierdzić TLS (9.1.x) | E-06 |
| 14.1.3 | `ALLOWED_HOSTS` puste na produkcji | ustawić w Coolify | E-08, R-17 |
| 14.3.3 | `server: uvicorn`, brak `server_tokens off` | `--no-server-header`, `server_tokens off` | nowe |

### Do sprawdzenia na serwerze (❓)

1.2.1 (konta hosta), 7.3.4 (NTP), 9.1.1–9.1.3 i 9.2.4 (TLS proxy Coolify: wersje, szyfry, OCSP), 10.3.3 (DNS,
przejęcie subdomeny). Dodatkowo w uwagach: ochrona gałęzi `main` (1.10.1), szyfrowanie dysku (6.1.1), cache proxy
(8.1.1), ruch wychodzący (12.6.1), utwardzenie hosta (14.1.3). Właściciel: [OPS], przy najbliższym przeglądzie RUNBOOK.

### Wniosek

Aplikacja **nie spełnia jeszcze w pełni L2**. Najważniejsze luki w kolejności (stosunek skutku do kosztu):
2.6.2/2.6.3 i 2.8.2 (sekrety 2FA w bazie), 4.3.1 (MFA adminów, E-01), 3.3.2 (brak limitu sesji), 2.1.3
(obcinanie hasła), 8.2.1 (`no-store`). Ryzyka nowe względem `RYZYKA.md` (bez ID) wymagają wpisu przez [SEC]
i decyzji PO — ten dokument ich nie dodaje. Następna weryfikacja: po realizacji poprawek albo 2027-01-15.
