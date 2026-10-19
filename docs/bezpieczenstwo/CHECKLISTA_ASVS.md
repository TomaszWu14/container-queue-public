# Checklista OWASP ASVS

> **Pełna weryfikacja L2 wymaganie po wymaganiu (2026-10-19, US-025): [`ASVS-L2-WERYFIKACJA.md`](ASVS-L2-WERYFIKACJA.md).** Tabela niżej to podsumowanie per rozdział; statusy poprawione wg weryfikacji.

2026-10-16, [SEC]. Poziom: **L2** (Z-017 — aplikacja przetwarza dane osobowe osób trzecich i dane handlowe
kilku firm; L3 nieuzasadnione przy tej skali). Wersja ASVS: 4.0.3.

**To ocena wstępna per rozdział**, oparta na audycie (`docs/AUDYT.md` §3.1) i kodzie — nie weryfikacja
każdego wymagania ASVS z osobna. Pełne przejście L2 wymaganie po wymaganiu: US-025. Status: ✅ spełnione
w zakresie L2 · ⚠️ częściowo · ❌ brak · n/d nie dotyczy.

| Rozdział | Status | Dowody | Luki / działania |
|---|---|---|---|
| V1 Architektura, projekt, model zagrożeń | ⚠️ | izolacja w jednym miejscu (`deps.py`, D9); `THREAT_MODEL.md` 0.1; ADR-y w `06-decyzje.md` | model zagrożeń dopiero od 2026-10-16; brak wymuszenia spójności spółki w bazie (R-01) |
| V2 Uwierzytelnianie | ⚠️ | bcrypt 12, polityka haseł 12+ znaków, limity prób w bazie, stały czas odpowiedzi, reset hasła tokenem z TTL i 202, 2FA TOTP z kodami zapasowymi | 2FA adminów nieobowiązkowe (E-01); brak sprawdzania haseł z wycieków (2.1.7); bcrypt obcina do 72 B (2.1.3); sekret TOTP jawnie w bazie (2.8.2); kody zapasowe 40 bitów bez soli (2.6.2) — zob. `ASVS-L2-WERYFIKACJA.md` |
| V3 Zarządzanie sesją | ⚠️ | JWT w cookie `HttpOnly`/`SameSite=Lax`/`Secure`; access 15 min; refresh 30 min od ostatniego odświeżenia (bezczynność), nic poza 12 h od zalogowania, z rotacją i wykryciem ponownego użycia; `session_version`; wylogowanie ze wszystkich urządzeń | brak prefiksu `__Host-` (E-07); limity sesji 3.3.2 ✅ (US-091); ekran aktywnych sesji jest (3.3.4 ✅) — zob. `ASVS-L2-WERYFIKACJA.md` |
| V4 Kontrola dostępu | ⚠️ | RBAC 7 ról, `require_roles`, `scope_*`/`get_scoped`, 404 dla obcych rekordów, macierz rola × trasa w testach, trasy bez logowania tylko z listy `PUBLIC` | MFA adminów nieobowiązkowe — 4.3.1 ❌ (E-01); izolacja tylko w kodzie, strażnik tras (US-011, R-01) — zob. `ASVS-L2-WERYFIKACJA.md` |
| V5 Walidacja, sanityzacja, kodowanie | ⚠️ | Pydantic v2, ORM, Jinja2 autoescape, React, neutralizacja formuł, bramka numeru w PDF | `csv_safe` i XML z DTD naprawione (US-008, US-006); pola tekstowe bez limitu długości (T-15); `str.format_map` w szablonie (5.2.5) — zob. `ASVS-L2-WERYFIKACJA.md` |
| V6 Kryptografia | ⚠️ | HS256 ≥ 32 znaki; Fernet (AES-128-CBC+HMAC) dla cache MSAL; SHA-256 dla tokenów linków i kodów zapasowych; `secrets` dla losowości | jeden sekret do JWT i szyfrowania bez `DATA_ENCRYPTION_KEY` (R-05, US-002); brak udokumentowanej rotacji kluczy (RUNBOOK) |
| V7 Obsługa błędów i logowanie | ⚠️ | `X-Request-ID`, logi bez tokenów/PII, Sentry ze scrubbingiem, audit log zmian, `job_runs`, `LOG_FILE` z rotacją | scrubbing nie łapie imion w wolnym tekście; log tekstowy bez kodowania nowych linii (7.3.1); 500 bez identyfikatora (7.4.1) — zob. `ASVS-L2-WERYFIKACJA.md` |
| V8 Ochrona danych | ⚠️ | klasyfikacja (`KLASYFIKACJA_DANYCH.md`), retencje, maskowanie danych kierowcy, `no-referrer`/`noindex` dla linków, `Cache-Control` dla assetów | brak retencji dokumentów handlowych (O-3); kopie zapasowe dłużej niż retencja; `RODO.md` 0.1 |
| V9 Komunikacja | ⚠️ | HTTPS przez proxy Coolify; HSTS przy `SECURE_COOKIES`; zaufane proxy dla `X-Forwarded-For`; Ollama tylko wewnętrznie | `ALLOW_INSECURE_HTTP` jako wyjątek (E-06); baza i Ollama bez TLS w sieci Dockera (9.2.2); TLS proxy niezweryfikowany (❓) — zob. `ASVS-L2-WERYFIKACJA.md` |
| V10 Złośliwy kod | ✅ | zależności z hashami, akcje po SHA, obrazy po digest, gitleaks, Bandit, pip-audit, npm audit; brak `eval`/`pickle`/`shell=True` | Trivy i Semgrep bramkują PR (US-007 — zamknięte); DNS/subdomeny ❓ — zob. `ASVS-L2-WERYFIKACJA.md` |
| V11 Logika biznesowa | ⚠️ | maszyna stanów statusów, reguły cofania z notatką, limity jako ostrzeżenia z audytem, jednorazowe linki, dedup wysyłek | wersjonowanie statusów zrobione (US-003); limit API w pamięci (E-04); brak alertów anomalii (11.1.7–11.1.8) — zob. `ASVS-L2-WERYFIKACJA.md` |
| V12 Pliki i zasoby | ⚠️ | `MAX_UPLOAD_MB` na każdej trasie, sygnatury dla zdjęć, lista rozszerzeń, nazwa z losowym składnikiem, pliki poza katalogiem publicznym, pobieranie jako `attachment`, limit stron PDF i plików w ZIP | załączniki po rozszerzeniu (R-03, US-004); ZIP z deklarowanego rozmiaru (US-006); brak AV |
| V13 API i usługi sieciowe | ⚠️ | JSON przez Pydantic, CSRF dla cookie, `/docs` wyłączone na prod, limity, HMAC dla webhooków wychodzących, token n8n w stałym czasie | CIDR/termin tokenu n8n opcjonalne (E-10); trasy z logowaniem bez jawnego 415 (13.1.5); MAG-1 z limitem (US-005 — zamknięte) — zob. `ASVS-L2-WERYFIKACJA.md` |
| V14 Konfiguracja | ⚠️ | fail-fast na prod (sekrety, `PUBLIC_BASE_URL`, `SECURE_COOKIES`), nagłówki bezpieczeństwa, kontenery bez roota, limity RAM/CPU, `.env.example` bez wartości (test), katalog zmiennych z testem kompletności | `DATABASE_URL` z fail-fast (US-001 — zamknięte); `ALLOWED_HOSTS` puste na prod (E-08); API bez `Content-Disposition` (14.4.2); `server: uvicorn` (14.3.3) — zob. `ASVS-L2-WERYFIKACJA.md` |

## Podsumowanie

- Rozdziały z ✅: 1 z 14; ⚠️: 13; ❌: 0 (po weryfikacji 2026-10-19; wcześniej 8 / 6 / 0). Wymagania: 140 ✅, 61 ⚠️, 21 ❌, 29 n/d, 6 ❓ — `ASVS-L2-WERYFIKACJA.md`.
- Luki z oceny wstępnej mają historyjkę lub wyjątek w `RYZYKA.md`; weryfikacja z 2026-10-19 znalazła nowe
  (m.in. sekret TOTP jawnie, kody zapasowe 40 bitów, brak limitu sesji) — bez ID, do wpisania przez [SEC]
  (lista w `ASVS-L2-WERYFIKACJA.md`, „Podsumowanie”).
- Następny przegląd: po scaleniu historyjek *Must* albo 2027-01-15, co pierwsze.
