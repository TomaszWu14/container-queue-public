# Backupy bazy danych (Postgres)

Automatyczna kopia zapasowa całej bazy do lokalnego pliku `.sql.gz`, z retencją.
Chroni przed przypadkowym skasowaniem danych i nieudaną migracją.

> ⚠️ Domyślnie backup jest **lokalny** — pliki leżą na tym samym serwerze co aplikacja i nie chronią
> przed utratą całego serwera/dysku. Włącz **kopię poza serwer** (niżej, US-013): zaszyfrowane pliki
> po każdej kopii trafiają do zewnętrznego magazynu.

## Skrypty
- `backend/scripts/backup.sh` — `pg_dump` → `BACKUP_DIR/timporye-<data>.sql.gz`, retencja GFS (niżej).
- `backend/scripts/restore.sh` — odtworzenie bazy z wybranego pliku (z potwierdzeniem).

Wymagają `pg_dump`/`psql` — są w obrazie (`postgresql-client` w `Dockerfile.coolify`).

## Konfiguracja (zmienne środowiskowe)
| Zmienna | Domyślnie | Znaczenie |
|---|---|---|
| `DATABASE_URL` | — | połączenie do Postgresa (to samo co aplikacja) |
| `BACKUP_DIR` | `/data/backups` | katalog na kopie (musi być na **trwałym wolumenie**) |
| `BACKUP_KEEP` | `14` | ile najnowszych kopii bazy zostawić (przy 3 kopiach/dobę: `21` = 7 dni) |
| `BACKUP_KEEP_WEEKLY` | `8` | dodatkowo najnowsza kopia z każdego z ostatnich N tygodni (pon–niedz.) |
| `BACKUP_KEEP_MONTHLY` | `12` | dodatkowo najnowsza kopia z każdego z ostatnich N miesięcy |
| `BACKUP_KEEP_UPLOADS` | `7` | ile archiwów załączników zostawić |
| `UPLOADS_DIR` | `/data/uploads` | katalog załączników archiwizowany do `uploads-<data>.tar.gz` |
| `BACKUP_SKIP_UPLOADS` | `0` | `1` = tylko baza, bez archiwum załączników (kopie w ciągu dnia) |
| `BACKUP_AGE_RECIPIENT` | puste | klucz **publiczny** [age](https://age-encryption.org) (`age1…`): kopie bazy i załączników zapisywane wyłącznie zaszyfrowane (`*.sql.gz.age`, `*.tar.gz.age`); puste = jawne pliki jak dotąd (BACKUP-007) |
| `BACKUP_AGE_IDENTITY` | puste | tylko `restore.sh` przy pliku `.age`: ścieżka do pliku klucza **prywatnego** age (na czas odtwarzania, nie trzymaj go na serwerze) |

**Retencja GFS (audyt BACKUP-008):** zostają `BACKUP_KEEP` najnowszych kopii bazy **plus**
najnowsza kopia z każdego z ostatnich `BACKUP_KEEP_WEEKLY` tygodni i `BACKUP_KEEP_MONTHLY`
miesięcy (liczone po dacie w nazwie `timporye-YYYYMMDD-HHMMSS.sql.gz`, tylko tygodnie/miesiące,
w których jest jakaś kopia). Usuwane jest wyłącznie to, co nie należy do żadnego z trzech zbiorów —
cofnięcie o ~rok jest możliwe, a ręczne uruchomienia nie wypychają kopii miesięcznych.
Przy domyślnych wartościach na dysku jest do ~`KEEP + 8 + 12` plików (w praktyce mniej — zbiory się
pokrywają); zajętość ≈ ta liczba × rozmiar jednej kopii (`ls -lh /data/backups`).
Samo sprzątanie bez nowej kopii: `sh /app/scripts/backup.sh --retencja`.

`/data` to ten sam trwały wolumen co uploady — kopie przeżywają redeploy i restart.
Jeśli `DATABASE_URL` wskazuje SQLite (dev), skrypt grzecznie się pomija.

## Harmonogram w Coolify — przykład: raz w tygodniu
Przykładowo kopia raz w tygodniu, w sobotę 22:00 (baza + załączniki).
Rzadszy harmonogram = większe ryzyko utraty zmian (do 7 dni).

Scheduled Tasks → Add:

| Nazwa | Command | Frequency (cron) |
|---|---|---|
| `backup-tygodniowy` | `env BACKUP_KEEP=8 sh /app/scripts/backup.sh` | `0 22 * * 6` |

Po dodaniu **Execute Now** i sprawdź log (`backup: gotowe (…)`, `backup: załączniki → …`).
Cotygodniowa weryfikacja (niedziela) akceptuje kopię do `BACKUP_MAX_AGE_HOURS` (194 h).
Cron Coolify liczy w strefie serwera. `/data` musi być **Persistent Storage**.

### Uruchomienie ręczne (test)
```sh
docker exec -it <kontener> sh /app/scripts/backup.sh
docker exec -it <kontener> ls -lh /data/backups
```

## Szyfrowanie kopii (opcjonalne, BACKUP-007)
Kopia zawiera hashe haseł, sekrety 2FA i dane kierowców — przed wysłaniem poza serwer powinna być
zaszyfrowana. Klucz **prywatny** nie może leżeć na serwerze (przechowuj go offline, poza serwerem):
```sh
age-keygen -o timporye-backup.key        # NA KOMPUTERZE ADMINA; linia „# public key: age1…”
```
W zmiennych aplikacji ustaw `BACKUP_AGE_RECIPIENT=age1…` (klucz publiczny). Od tej pory w
`BACKUP_DIR` powstają tylko pliki `.age` (retencja, `/api/health/deep` i cotygodniowa weryfikacja je
rozumieją). Weryfikacja na serwerze sprawdza wtedy tylko świeżość kopii — **próbne odtworzenie rób
poza serwerem** (z kluczem prywatnym), np. raz w miesiącu. Program `age` jest w obrazie
(`Dockerfile.coolify`), a zmienna przekazywana do kontenera (`docker-compose.coolify.yml`); gdyby
szyfrowanie nie działało, backup kończy się głośnym błędem, nigdy jawną kopią.
Sprawdzenie: `gunzip -t plik.sql.gz.age` zwraca błąd (nieczytelny bez klucza).

## Kopia poza serwer (US-013, R-10)
Po każdej udanej kopii `backup.sh` wysyła **zaszyfrowane** pliki z tego uruchomienia (baza i, jeśli
powstało, archiwum załączników) do magazynu zgodnego z S3: Backblaze B2, Cloudflare R2, Hetzner
Object Storage, Wasabi, AWS S3. Bez nowych bibliotek — `curl` z podpisem AWS SigV4.

Zasady bezpieczeństwa (wymuszone w skrypcie, testy `tests/test_backup_offsite.py`):
- **jawna kopia nigdy nie wychodzi z serwera**: `BACKUP_OFFSITE_URL` bez `BACKUP_AGE_RECIPIENT` = błąd,
- klucze dostępu idą do `curl` przez stdin, nie w argumentach (niewidoczne w liście procesów),
- błąd wysyłki = kod błędu i **brak heartbeatu** (`BACKUP_PING_URL`), więc monitor zaalarmuje;
  kopia lokalna zostaje.

| Zmienna | Znaczenie |
|---|---|
| `BACKUP_OFFSITE_URL` | adres magazynu **z nazwą koszyka**, np. `https://s3.eu-central-003.backblazeb2.com/timporye-kopie`; puste = wyłączone |
| `BACKUP_OFFSITE_REGION` | region podpisu (B2: np. `eu-central-003`, R2: `auto`, AWS: np. `eu-central-1`); domyślnie `auto` |
| `BACKUP_OFFSITE_ACCESS_KEY` | identyfikator klucza aplikacji |
| `BACKUP_OFFSITE_SECRET_KEY` | sekret klucza — tylko w Coolify (Environment Variables), nigdy w repo |

### Jak włączyć (jednorazowo, ok. 15 min)
1. **Klucz szyfrowania** (jeśli jeszcze nie ma): na swoim komputerze `age-keygen -o timporye-backup.key`.
   Plik z kluczem prywatnym schowaj w menedżerze haseł / sejfie; **nie na serwerze**. Linię
   `# public key: age1…` wpisz w Coolify jako `BACKUP_AGE_RECIPIENT`.
2. **Magazyn:** załóż koszyk (bucket) u wybranego dostawcy, **prywatny**, najlepiej w UE (RODO).
3. **Klucz dostępu tylko do zapisu** (bez prawa kasowania i odczytu, jeśli dostawca na to pozwala; B2:
   „Application Key” z uprawnieniem `writeFiles` do tego jednego koszyka). Przejęty serwer nie skasuje
   wtedy kopii poza nim.
4. **Retencja po stronie magazynu:** reguła cyklu życia (lifecycle), np. usuwanie plików starszych niż
   400 dni; skrypt niczego poza serwerem nie kasuje.
5. W Coolify ustaw 4 zmienne z tabeli, **Redeploy**, potem Scheduled Task → **Execute Now** i sprawdź log:
   `backup: poza serwer → timporye-….sql.gz.age`. W panelu dostawcy powinny być nowe pliki.
6. **Próbne odtworzenie** z pliku pobranego z magazynu (RUNBOOK §5) — raz na kwartał, z wpisem w rejestrze.

## Odtworzenie (restore)
> ⚠️ Nadpisuje obecne dane w bazie. Najlepiej najpierw zrób świeży backup.
```sh
docker exec -it <kontener> sh /app/scripts/restore.sh /data/backups/timporye-20260710-020000.sql.gz
# skrypt zapyta o potwierdzenie; w automatyzacji dodaj --force
```
Kopia zaszyfrowana: `BACKUP_AGE_IDENTITY=/sciezka/timporye-backup.key sh /app/scripts/restore.sh /data/backups/timporye-….sql.gz.age` (klucz skopiuj na czas odtwarzania i usuń).
Dump jest robiony z `--clean --if-exists`, więc odtwarza się także na istniejącej bazie.
Po restore zrestartuj aplikację.

## Dobre praktyki
- Raz na jakiś czas **przetestuj restore** na osobnej bazie — backup bez sprawdzonego odtworzenia jest wart połowę.
- Wersja `pg_dump` (klienta) powinna być ≥ wersji serwera Postgres.
- Kolejny krok bezpieczeństwa: kopia **poza serwer** (S3/rsync na inny host).
