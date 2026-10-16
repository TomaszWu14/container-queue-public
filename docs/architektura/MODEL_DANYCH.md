# Model danych — indeks

[DEV], 2026-10-16. Dokument źródłowy: **[`../04-model-danych.md`](../04-model-danych.md)** — diagram ER
rdzenia (Mermaid, 18 encji), opis encji, reguły integralności, lista znanych niespójności. Pełna definicja:
modele SQLAlchemy w `backend/app/models/` (106 tabel), schemat w migracjach Alembic `backend/migrations/versions/`
(121 plików).

## Zasady

| Zasada | Gdzie pilnowane |
|---|---|
| Ten sam model na SQLite (dev, testy) i PostgreSQL 16 (prod) | `database.py`; testy na SQLite, migracje w CI na PostgreSQL |
| Każda zmiana modelu = migracja z działającym `upgrade()` **i** `downgrade()`, jedna głowa | `ci-migrations.yml`: `alembic upgrade head`, `downgrade -1`, `upgrade head` |
| Modele = schemat (zero dryfu) | `scripts/db_drift.py`, `db_enum_drift.py`; `db_drift_baseline.txt` pusty od 2026-09-28 |
| Klucze biznesowe jako indeksy unikalne (`ux_*`) → naruszenie = 409 | `db_errors.py` (DB-007) |
| Numer kontenera unikalny tylko wśród niezrealizowanych w spółce | częściowy indeks unikalny (D7) |
| Wyszukiwanie trigramowe | `pg_trgm` (migracje `trgm001/002`) |
| Spójność spółki między tabelami | **tylko w kodzie** (`deps.py`, D9) — ryzyko R-01 |

## Znane niespójności (skrót; pełna lista w `04` §„Znane niespójności modelu”)

Dwa statusy odprawy (`customs_status` i słownikowy `customs_case_status_id`), stan dokumentów w trzech
polach, powiązanie zamówienie ↔ kontener na cztery sposoby, dwa modele zlecenia transportu, brak UNIQUE
w `AvizoItem` i `DeliveryConfirmation`, statusy tekstowe bez CHECK, `proposed_delivery_date` nieużywane (D1).
Plan spłaty: US-021 (*Could*, decyzja PO).

## Zmiana modelu wymaga

1. wpisu w `../analiza/WYMAGANIA.md` (albo historyjki), jeśli zmienia regułę biznesową,
2. aktualizacji ERD w `04`, gdy dotyczy encji rdzenia,
3. migracji z `downgrade()` i przebiegu `ci-migrations.yml`,
4. przeglądu klasy danych nowych kolumn (`../bezpieczenstwo/KLASYFIKACJA_DANYCH.md`) — dane osobowe = retencja.
