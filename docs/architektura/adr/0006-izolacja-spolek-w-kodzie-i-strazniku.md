# ADR-0006 · Izolacja spółek: kontrola w `deps.py` + strażnik tras, bez RLS w bazie

- **Status:** proponowana — czeka na akceptację PO (US-011, R-01)
- **Data:** 2026-10-17
- **Role:** [DEV] propozycja, [SEC] przegląd niżej

## Kontekst

Dane kilku spółek i partnerów są w jednej bazie. Izolacja jest w jednym miejscu kodu (`deps.py`, D9):
`get_scoped`, `scope_*`, `check_container_access`. Baza nie wymusza spójności `company_id`, więc jedna nowa
trasa bez tej kontroli = wyciek między firmami (R-01). Dziś: 226 tras z identyfikatorem w adresie.

## Rozważane opcje

1. **Strażnik w testach** (`tests/test_isolation_guard.py`): każda trasa z `{..._id}` przechodzi przez
   kontrolę z `deps.py` albo jest na liście wyjątków z powodem. Tanio, łapie błąd przed scaleniem.
   Heurystyka po źródle — nie dowód.
2. **CHECK / złożone klucze obce** (`(company_id, id)`), żeby rekord podrzędny nie mógł wskazać rekordu innej
   spółki. Chroni spójność zapisu, nie odczyt; migracje na żywej bazie dla kilkunastu tabel.
3. **Row-Level Security w PostgreSQL** (polityka per spółka, `SET app.company_id` na połączenie). Najmocniejsze,
   ale aplikacja łączy się jednym użytkownikiem bazy, ma role „wszystkie spółki” (admin, `view_all_companies`),
   zadania tła i importy grupowe; SQLite w testach nie ma RLS — dwie ścieżki zachowania.

## Decyzja (proponowana)

Opcja 1 teraz (wdrożona w tym PR); opcja 2 punktowo, gdy nowa tabela podrzędna dostaje `company_id`
(nowe tabele — od razu z kluczem złożonym); opcja 3 odrzucona na obecną skalę i architekturę.

## Przegląd bezpieczeństwa [SEC]

- **I (ujawnienie):** ryzyko R-01 maleje z „jedno pominięcie = wyciek” do „pominięcie zatrzymuje CI, chyba że
  ktoś świadomie dopisze wyjątek z powodem”. Wyjątki są w przeglądzie PR (34 dziś: słowniki wspólne grupy,
  konta użytkowników admina, baza wiedzy, statki AIS, własne sesje).
- Strażnik nie zastępuje testów na danych („obca spółka = 404”) ani macierzy ról (`permissions.yaml`).
- Pozostaje: brak wymuszenia w bazie (opcja 2/3) — R-01 zostaje „w realizacji” z niższą wagą.

## Konsekwencje

- Nowa trasa z identyfikatorem = kontrola z `deps.py` albo wpis do `EXCEPTIONS` (widoczny w diffie PR).
- Test pilnuje też, żeby lista wyjątków nie starzała się (trasa usunięta albo już chroniona = czerwony test).
