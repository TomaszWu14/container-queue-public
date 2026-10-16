# ADR-0003 · Ochrona przed cichym nadpisaniem: oczekiwany status przy przejściach statusu

- **Status:** przyjęta (US-003, decyzja PO „rób” 2026-10-16)
- **Data:** 2026-10-16
- **Role:** [DEV] propozycja, [SEC] bez uwag (R-02), [BA] zgoda

## Kontekst

Ryzyko R-02 / problem P-13 / błąd B-004: przy kilku logistykach ostatni zapis nadpisuje poprzedni bez
ostrzeżenia. Rozpoznanie 2026-10-16 pokazało, że część jest już chroniona (audyt DB-005): formularz
kontenera i panel kierowcy wysyłają `expected_updated_at`, a `check_not_modified` robi warunkowy UPDATE
i zwraca 409. Bez ochrony zostały **przejścia statusu**: status kontenera, status odprawy, status zlecenia
transportowego. Tam dwie osoby klikają zmianę na podstawie tego, co widziały chwilę wcześniej.

## Rozważane opcje

1. **`expected_updated_at` także dla przejść statusu.** Jeden mechanizm wszędzie. Wada: `updated_at`
   zmienia się przy każdym zapisie wiersza (notatka, synchronizacja trackingu, plan dostawy), więc klik
   statusu dostawałby 409 przy niezwiązanych zmianach — fałszywe konflikty.
2. **Oczekiwany status** (`expected_status`, `expected_customs_status`): klient wysyła status, który
   widział; serwer sprawdza go warunkowym UPDATE-em na tej jednej kolumnie. Konflikt tylko wtedy, gdy
   naprawdę zmienił się ten sam status.
3. Kolumna `version` + migracja. Dokładne, ale ten sam problem fałszywych konfliktów co opcja 1
   i koszt migracji na żywej bazie.

## Decyzja

Opcja 2 dla przejść statusu; formularze zostają przy `expected_updated_at` (DB-005), bo wysyłają pełny
stan wielu pól. Wspólna funkcja `backend/app/optimistic.py::claim_expected_state`:

- `UPDATE … SET kolumna = oczekiwany WHERE id = … AND kolumna = oczekiwany` — zajmuje wiersz; drugi
  równoległy zapis czeka na blokadę, po commicie pierwszego jego warunek już nie pasuje → 409,
- 409 niesie `{"code": "state_changed", "message": …, "current": <aktualna wartość>}`,
- pole jest **opcjonalne**: stare klienty, importy, n8n i zmiany masowe działają jak dotąd.

## Konsekwencje

- Panel wysyła oczekiwany status we wszystkich pojedynczych zmianach statusu; użytkownik po konflikcie
  widzi aktualny stan w komunikacie i odświeża kartę.
- Zmiany masowe statusu (`containers_bulk`) świadomie bez kontroli — operują na liście filtrów, nie na
  widoku pojedynczego rekordu; do decyzji PO, jeśli zgłoszą problem.
- R-02 zamknięte dla ścieżek interaktywnych; zostaje dla importu Excela (reguła „nowsza zmiana wygrywa”, FR-026).
