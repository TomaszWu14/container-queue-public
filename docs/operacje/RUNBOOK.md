# Runbook — wdrożenie, kopie, odtworzenie, incydenty

[OPS/DEV/SEC], 2026-10-16, wersja 0.1. Procedury dla operatora aplikacji (rola admin + dostęp do Coolify).
Źródła szczegółowe: [`../DEPLOY_COOLIFY.md`](../DEPLOY_COOLIFY.md), [`../BACKUPY.md`](../BACKUPY.md),
[`../JEDNA-INSTANCJA.md`](../JEDNA-INSTANCJA.md), [`../ZMIENNE-SRODOWISKOWE.md`](../ZMIENNE-SRODOWISKOWE.md),
`scripts/smoke.sh`. Sekretów w tym pliku nie ma i nie będzie.

## 1. Architektura operacyjna w jednym zdaniu

Jeden kontener `app` (API + panel, migracje przy starcie) + kontener `db` (PostgreSQL 16) w Coolify, wolumeny
`uploads`, `backups`, `logs`; domena i TLS z proxy Coolify; opcjonalnie brama nginx (profil `gateway`) i osobny
stack n8n. Jedna instancja — przed podniesieniem liczby workerów przeczytaj `JEDNA-INSTANCJA.md`.

## 2. Wdrożenie (Redeploy)

Merge do `main` **niczego nie wdraża**. Wdrożenie = decyzja PO + ręczny Redeploy.

1. Upewnij się, że PR jest scalony, CI zielone, `CHANGELOG.md` ma wpis.
2. Sprawdź nowe zmienne środowiskowe z `CHANGELOG.md` / `ZMIENNE-SRODOWISKOWE.md` i ustaw je w Coolify
   **przed** redeployem (fail-fast na produkcji zatrzyma start bez wymaganych).
3. Wykonaj kopię bazy przed wdrożeniem ze zmianą modelu: `backend/scripts/backup.sh` (albo poczekaj na
   najbliższą cykliczną i sprawdź, że istnieje).
4. Coolify → zasób → **Redeploy**. Start: `alembic upgrade head && uvicorn`; `start-period` healthchecku 120 s.
5. Smoke: `sh scripts/smoke.sh https://<domena>` (health, strona główna; z `SMOKE_LOGIN` także logowanie
   kontem tylko do odczytu i lista kolejki). Kod ≠ 0 = wdrożenie do sprawdzenia lub cofnięcia.
6. Sprawdź `/api/health` → `version` = SHA wdrożonego commita; panel Administracja → System/Logi bez błędów startu.

### Cofnięcie

Redeploy poprzedniego commita w Coolify. Migracja z `downgrade()` istnieje dla każdej wersji
(`ci-migrations.yml` to sprawdza), ale **cofanie migracji na produkcji wymaga kopii bazy i decyzji PO**:
`python -m alembic downgrade -1` w kontenerze `app`.

## 3. Wymagane zmienne na produkcji (fail-fast)

`ENVIRONMENT=production`, `SECRET_KEY` (≥ 32 znaki), `ADMIN_PASSWORD` (nie domyślne), `POSTGRES_PASSWORD`,
`PUBLIC_BASE_URL`, `SECURE_COOKIES=true` (albo świadome `ALLOW_INSECURE_HTTP=true` — wyjątek E-06),
`BCRYPT_ROUNDS ≥ 12`. Zalecane: `ALLOWED_HOSTS` (E-08), `DATA_ENCRYPTION_KEY` (do czasu US-002 opcjonalne),
`AUTOMATION_ALLOWED_CIDRS` i `AUTOMATION_TOKEN_EXPIRES`, gdy n8n włączone (E-10), `SENTRY_DSN`, `LOG_FILE`.
Pełny katalog: `ZMIENNE-SRODOWISKOWE.md`. **Zmienne nie są objęte kopią zapasową** — trzymaj ich kopię
w menedżerze sekretów poza serwerem.

## 4. Kopie zapasowe

- Harmonogram (decyzja 2026-09-28, E-02): raz w tygodniu, sobota 22:00, baza + załączniki; retencja GFS
  (`BACKUP_KEEP` 14 + 8 tygodni + 12 miesięcy). Zadanie: Scheduled Task w Coolify → `backend/scripts/backup.sh`.
- Szyfrowanie: `BACKUP_AGE_RECIPIENT` (klucz publiczny `age`); klucz prywatny **poza serwerem**.
- Weryfikacja: `verify_backup.py` co tydzień (`VERIFY_BACKUP_WEEKDAY`) odtwarza kopię do bazy tymczasowej
  i liczy wiersze; wynik w panelu Logi → Zadania i alert dla adminów.
- Heartbeat: `BACKUP_PING_URL` (np. Uptime Kuma) — brak pingu = kopia nie powstała.
- **Luka:** kopie leżą na tym samym serwerze (R-10, US-013).

## 5. Odtworzenie

1. Zatrzymaj `app` (Coolify → Stop), żeby nic nie pisało do bazy.
2. Wybierz plik kopii w `/data/backups` (`timporye-YYYYMMDD-HHMMSS.sql.gz[.age]`).
3. W kontenerze `app`: `BACKUP_AGE_IDENTITY=/tmp/klucz.txt sh scripts/restore.sh <plik>` (skrypt prosi
   o potwierdzenie); klucz prywatny skopiuj tylko na czas odtwarzania i usuń.
4. Załączniki: rozpakuj `uploads-<data>.tar.gz[.age]` do wolumenu `uploads`.
5. Start `app`; `alembic upgrade head` dociągnie migracje nowsze niż kopia.
6. Smoke (§2 pkt 5) + sprawdzenie w panelu: liczba kontenerów, ostatnie wpisy historii.
7. Wpis w rejestrze ryzyk: data ćwiczenia/odtworzenia, czas trwania (RTO), uwagi.

**Ćwiczenie odtworzenia** (nie tylko automatyczna weryfikacja) raz na kwartał — US-013.

## 6. Monitoring i diagnostyka

| Sygnał | Gdzie | Co znaczy |
|---|---|---|
| `GET /api/health` | 200 `{"status":"ok","database":"ok","version":…}` | aplikacja i baza żyją; 503 = baza niedostępna |
| `GET /api/health/deep` | 200/503 (szczegóły tylko dla admina) | zadania tła, integracje |
| HEALTHCHECK Dockera + strażnik | kontener `unhealthy` → proces kończy się → restart (`HEALTH_RESTART_AFTER`) | zawieszenie (np. OCR) |
| Panel → Administracja → Logi / Zadania / System | `applog`, `job_runs`, pamięć | błędy startu, zadania tła, RAM |
| Sentry (jeśli `SENTRY_DSN`) | zdarzenia z `request_id` | wyjątki; PII wyczyszczone |
| `docker logs app` / `LOG_FILE` | linie z `rid=` | korelacja z `X-Request-ID` z przeglądarki |

Typowe objawy: start pada z „Konfiguracja wymaga zmiany dla produkcji: …” = brak zmiennej (§3);
`WEB_CONCURRENCY>1` na SQLite = odmowa startu (zamierzona); 429 w panelu = limit API (pętla w kliencie?).

## 7. Incydent bezpieczeństwa

1. **Zatrzymaj szkodę:** przy podejrzeniu przejęcia konta — dezaktywuj konto i unieważnij sesje (panel: konto →
   wyloguj ze wszystkich urządzeń / `session_version`); przy podejrzeniu wycieku tokenu n8n — ustaw nowy
   `AUTOMATION_API_TOKEN`, stary do `AUTOMATION_API_TOKEN_PREVIOUS` na czas przełączenia, potem wyczyść.
2. **Kopia dowodów przed zmianami:** kopia bazy (`backup.sh`), eksport logów (`LOG_FILE`, `docker logs`),
   zrzut `audit_log` typu `auth` (IP, loginy, czasy).
3. **Rotacja sekretów** wg skali: `SECRET_KEY` (unieważnia wszystkie sesje; przy braku `DATA_ENCRYPTION_KEY`
   psuje odszyfrowanie cache MSAL — zaloguj integrację ponownie), hasła DB/SMTP, tokeny M365/SMSAPI/AIS,
   klucz `age` (nowe kopie nowym kluczem, stare zostają czytelne starym).
4. **Ocena RODO:** czy dotknięte dane osobowe (kierowcy, użytkownicy)? Jeśli ryzyko dla osób — zgłoszenie
   do organu w 72 h, zawiadomienie osób przy wysokim ryzyku (`../bezpieczenstwo/RODO.md` §8). Decyduje PO.
5. **Zapis:** wpis w `../bezpieczenstwo/RYZYKA.md` (nowe ryzyko albo aktualizacja), lekcje w CHANGELOG
   (sekcja Security) bez szczegółów exploita.
6. **Przegląd po incydencie:** w ciągu 7 dni — co zawiodło, jaka historyjka to naprawia.

## 8. Rotacja kluczy (procedury)

| Klucz | Jak | Skutek |
|---|---|---|
| `SECRET_KEY` | nowa wartość ≥ 32 znaki w Coolify, Redeploy | wszyscy wylogowani; bez `DATA_ENCRYPTION_KEY` dane Fernet nieczytelne (do czasu US-002 rotuj oba razem albo ustaw `DATA_ENCRYPTION_KEY` = stary `SECRET_KEY` przed zmianą) |
| `DATA_ENCRYPTION_KEY` | nowa wartość; stare wartości czyta MultiFernet dowolnym z listy (`crypto.py`) | nowe zapisy nowym kluczem; pełna rotacja = ponowny zapis wartości (brak narzędzia — US-002) |
| `AUTOMATION_API_TOKEN` | nowy token (`secrets.token_urlsafe(32)`), stary do `_PREVIOUS`, przełącz credential w n8n, usuń `_PREVIOUS` | bez przestoju |
| Hasło admina / użytkownika | panel: reset przez admina → hasło tymczasowe → wymuszona zmiana | sesje unieważnione |
| Klucz `age` | nowa para; `BACKUP_AGE_RECIPIENT` = nowy publiczny; stary prywatny zachowaj do końca retencji kopii | — |

## 9. Wniosek osoby (RODO)

Dostęp/eksport: admin → `GET /api/admin/data-subject` z identyfikatorem (login/e-mail albo telefon
kierowcy) → JSON dla osoby. Usunięcie: użytkownik → `DELETE /api/users/{id}` (anonimizacja); kierowca →
`POST /api/admin/data-subject/anonymize-driver`. Termin 30 dni; wpis w rejestrze wniosków (do założenia, US-012).

## 10. Instancja demo

`docker-compose.demo.yml`; konto `demo` tylko do odczytu; nocny reset `python -m scripts.seed_demo
--wyczysc-wszystko` (Scheduled Task 03:00). **Nigdy** nie podłączać do bazy produkcyjnej ani nie wgrywać
danych rzeczywistych (E-05). Weryfikacja backupu wyłączona (`VERIFY_BACKUP_WEEKDAY=-1`) — dane są syntetyczne.
