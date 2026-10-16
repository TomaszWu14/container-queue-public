# Architektura — indeks

[DEV], 2026-10-16. Dokument źródłowy: **[`../ARCHITEKTURA.md`](../ARCHITEKTURA.md)** (stan zweryfikowany
2026-09-28: stos, struktura repozytorium, model danych i role, przepływy, bezpieczeństwo, wdrożenie, diagram
Mermaid na poziomie kontekstu i kontenerów C4). Zgodnie z Z-012 nie przenosimy go — ten plik mówi, co gdzie
jest i co od 2026-09-28 się zmieniło.

## Poziomy C4

| Poziom | Gdzie | Uwagi |
|---|---|---|
| Kontekst (aktorzy, systemy zewnętrzne) | `../ARCHITEKTURA.md` §2 „Widok wysokopoziomowy” | aktorzy i role: `../analiza/INTERESARIUSZE.md` |
| Kontenery (API + panel, PostgreSQL, wolumen, n8n, Ollama, M365) | `../ARCHITEKTURA.md` §2–§3 | jeden obraz Docker: API serwuje zbudowany panel |
| Komponenty (routery → `deps.py` → modele; pętle tła; integracje) | `../ARCHITEKTURA.md` §4 „Struktura repozytorium” i dalsze | izolacja danych: `backend/app/deps.py` (D9) |
| Kod | `backend/app/`, `frontend/src/` | limit 500 linii/plik (`scripts/check_file_lengths.py`) |
| Model danych | `MODEL_DANYCH.md` → `../04-model-danych.md` | 106 tabel, ERD rdzenia (18 encji) |
| Decyzje | `adr/` → `../06-decyzje.md` (D1–D12) | nowe decyzje jako osobne pliki ADR |

## Co zmieniło się od stanu 2026-09-28 (do wniesienia przy następnej aktualizacji `../ARCHITEKTURA.md`)

- Instancja demo za HTTPS (`SECURE_COOKIES=true`, `docker-compose.demo.yml`); w dokumencie „HTTP :81 bez TLS”.
- Workflowy CI w tym repozytorium biegną na runnerach GitHub (`ubuntu-latest`), nie self-hosted; brak
  `automerge.yml`, `e2e.yml`, `claude*.yml` (`docs/AUDYT.md` §4).
- Publiczne linki dla klienta i kierowcy usunięte (D11, 2026-10-07) — diagram wymienia „kierowca, portal”.
- Pętle tła: `jobs.py` ma kilkanaście zadań (w tym retencje OBS-011/GDPR-007); lider na advisory locku (`leader.py`).

## Cechy architektury istotne dla decyzji (skrót z audytu)

1. **Monolit, jeden proces** z pętlami tła w procesie API; `WEB_CONCURRENCY>1` tylko na PostgreSQL; limiter API
   w pamięci (`../JEDNA-INSTANCJA.md`, E-04).
2. **Izolacja danych w jednym module** (`deps.py`) — zaleta testowalności, ryzyko R-01.
3. **Ciężkie przetwarzanie w procesie** (OCR, PDF, ML, pakowanie 3D) z limitami RAM/CPU w compose i częściowo w tle.
4. **Integracje włączane konfiguracją** — puste zmienne = funkcja wyłączona (`../ZMIENNE-SRODOWISKOWE.md`).
5. **Jeden obraz, migracje przy starcie** (`alembic upgrade head && uvicorn`), ręczny Redeploy w Coolify.

## Zmiana architektury wymaga

ADR w `adr/` (kontekst, opcje, decyzja, konsekwencje) **przed** kodem, aktualizacji `../ARCHITEKTURA.md`
albo tego indeksu, oraz przeglądu `../bezpieczenstwo/THREAT_MODEL.md` (nowy przepływ = nowa tabela STRIDE).
