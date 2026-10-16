# Checklista OWASP ASVS

2026-10-16, [SEC]. Poziom: **L2** (Z-017 — aplikacja przetwarza dane osobowe osób trzecich i dane handlowe
kilku firm; L3 nieuzasadnione przy tej skali). Wersja ASVS: 4.0.3.

**To ocena wstępna per rozdział**, oparta na audycie (`docs/AUDYT.md` §3.1) i kodzie — nie weryfikacja
każdego wymagania ASVS z osobna. Pełne przejście L2 wymaganie po wymaganiu: US-025. Status: ✅ spełnione
w zakresie L2 · ⚠️ częściowo · ❌ brak · n/d nie dotyczy.

| Rozdział | Status | Dowody | Luki / działania |
|---|---|---|---|
| V1 Architektura, projekt, model zagrożeń | ⚠️ | izolacja w jednym miejscu (`deps.py`, D9); `THREAT_MODEL.md` 0.1; ADR-y w `06-decyzje.md` | model zagrożeń dopiero od 2026-10-16; brak wymuszenia spójności spółki w bazie (R-01) |
| V2 Uwierzytelnianie | ✅ | bcrypt 12, polityka haseł 12+ znaków, limity prób w bazie, stały czas odpowiedzi, reset hasła tokenem z TTL i 202, 2FA TOTP z kodami zapasowymi | 2FA adminów nieobowiązkowe (E-01); brak sprawdzania haseł z wycieków (ASVS 2.1.7) |
| V3 Zarządzanie sesją | ✅ | JWT w cookie `HttpOnly`/`SameSite=Lax`/`Secure`; access 2 h; refresh 14 dni z rotacją i wykryciem ponownego użycia; `session_version`; wylogowanie ze wszystkich urządzeń | brak prefiksu `__Host-` (E-07); brak ekranu aktywnych sesji dla użytkownika (ASVS 3.3.4) |
| V4 Kontrola dostępu | ✅ | RBAC 7 ról, `require_roles`, `scope_*`/`get_scoped`, 404 dla obcych rekordów, macierz rola × trasa w testach, trasy bez logowania tylko z listy `PUBLIC` | strażnik nowych tras (US-011); IDOR zależy od dyscypliny użycia `get_scoped` (R-01) |
| V5 Walidacja, sanityzacja, kodowanie | ⚠️ | Pydantic v2, ORM, Jinja2 autoescape, React, neutralizacja formuł, bramka numeru w PDF | `csv_safe` bez `\t`/`\r` (US-008); XML stdlib (US-006); pola tekstowe bez limitu długości w schemacie (T-15) |
| V6 Kryptografia | ⚠️ | HS256 ≥ 32 znaki; Fernet (AES-128-CBC+HMAC) dla cache MSAL; SHA-256 dla tokenów linków i kodów zapasowych; `secrets` dla losowości | jeden sekret do JWT i szyfrowania bez `DATA_ENCRYPTION_KEY` (R-05, US-002); brak udokumentowanej rotacji kluczy (RUNBOOK) |
| V7 Obsługa błędów i logowanie | ✅ | `X-Request-ID`, logi bez tokenów/PII, Sentry ze scrubbingiem, audit log zmian, `job_runs`, `LOG_FILE` z rotacją | scrubbing nie łapie imion w wolnym tekście (zasada: nie wstawiać) |
| V8 Ochrona danych | ⚠️ | klasyfikacja (`KLASYFIKACJA_DANYCH.md`), retencje, maskowanie danych kierowcy, `no-referrer`/`noindex` dla linków, `Cache-Control` dla assetów | brak retencji dokumentów handlowych (O-3); kopie zapasowe dłużej niż retencja; `RODO.md` 0.1 |
| V9 Komunikacja | ✅ | HTTPS przez proxy Coolify; HSTS przy `SECURE_COOKIES`; zaufane proxy dla `X-Forwarded-For`; Ollama tylko wewnętrznie | `ALLOW_INSECURE_HTTP` jako wyjątek (E-06) |
| V10 Złośliwy kod | ✅ | zależności z hashami, akcje po SHA, obrazy po digest, gitleaks, Bandit, pip-audit, npm audit; brak `eval`/`pickle`/`shell=True` | Trivy nie bramkuje, brak Semgrep (US-007) |
| V11 Logika biznesowa | ✅ | maszyna stanów statusów, reguły cofania z notatką, limity jako ostrzeżenia z audytem, jednorazowe linki, dedup wysyłek | brak wersjonowania rekordów (R-02, US-003); limit API w pamięci (E-04) |
| V12 Pliki i zasoby | ⚠️ | `MAX_UPLOAD_MB` na każdej trasie, sygnatury dla zdjęć, lista rozszerzeń, nazwa z losowym składnikiem, pliki poza katalogiem publicznym, pobieranie jako `attachment`, limit stron PDF i plików w ZIP | załączniki po rozszerzeniu (R-03, US-004); ZIP z deklarowanego rozmiaru (US-006); brak AV |
| V13 API i usługi sieciowe | ✅ | JSON przez Pydantic, CSRF dla cookie, `/docs` wyłączone na prod, limity, HMAC dla webhooków wychodzących, token n8n w stałym czasie | CIDR/termin tokenu n8n opcjonalne (E-10); publiczne trasy DLT bez limitu (US-005) |
| V14 Konfiguracja | ✅ | fail-fast na prod (sekrety, `PUBLIC_BASE_URL`, `SECURE_COOKIES`), nagłówki bezpieczeństwa, kontenery bez roota, limity RAM/CPU, `.env.example` bez wartości (test), katalog zmiennych z testem kompletności | `DATABASE_URL` bez fail-fast (US-001); `ALLOWED_HOSTS` puste (E-08); rozjazd wersji Python/Node (US-015) |

## Podsumowanie

- Rozdziały z ✅: 8 z 14; ⚠️: 6; ❌: 0.
- Wszystkie luki mają historyjkę lub wyjątek w `RYZYKA.md`. Po realizacji US-001…US-008 oczekiwany stan:
  V5, V6, V12, V14 → ✅.
- Następny przegląd: po scaleniu historyjek *Must* albo 2027-01-15, co pierwsze.
