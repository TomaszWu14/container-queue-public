# ADR-0001 · Nowa struktura `docs/` jako indeksy do istniejących dokumentów

- **Status:** przyjęta warunkowo (założenie Z-012; PO może odrzucić)
- **Data:** 2026-10-16
- **Role:** [DEV] propozycja, [BA] zgoda, [SEC] bez uwag

## Kontekst

Proces zespołowy wymaga struktury `docs/analiza`, `docs/architektura`, `docs/bezpieczenstwo`, `docs/testy`,
`docs/operacje`. Repozytorium ma już 113 plików dokumentacji, w tym świeże i dobre `docs/01–07`,
`ARCHITEKTURA.md`, `BEZPIECZENSTWO.md`, `BACKUPY.md`, `DEPLOY_COOLIFY.md`, do których linkują `README.md`,
`docs/README.md`, komentarze w kodzie i opisy PR-ów w repozytorium prywatnym.

## Rozważane opcje

1. **Przenieść** istniejące pliki do nowych katalogów (`git mv`) i poprawić linki.
2. **Zostawić** istniejące pliki na miejscu, a nową strukturę zbudować z cienkich indeksów, które linkują do
   źródeł i dodają tylko to, czego brakuje (NFR, SR, backlog, słownik, model zagrożeń, rejestr ryzyk).
3. Skopiować treść do nowych plików (duplikacja).

## Decyzja

Opcja 2. Nowe pliki są indeksami z własną treścią tylko tam, gdzie jej dotąd nie było. Przy sprzeczności
obowiązuje kolejność: kod → `docs/01–07` → indeksy → starsze opisy modułów.

## Konsekwencje

- Zero zerwanych linków i zero konfliktów z równoległymi PR-ami (zasada „nie przenoś kodu, którego nie
  zmieniasz” z `CLAUDE.md` dotyczy też dokumentów).
- Czytelnik z zewnątrz ma jedno wejście (`docs/README.md`), ale dwa poziomy (indeks → źródło).
- Opcja 3 odrzucona: duplikaty szybko stają się nieprawdziwe („krótko i prawdziwie” > „długo i nieaktualnie”).
- Jeśli PO wybierze opcję 1, przeniesienie robimy jednym PR-em bez zmian treści, z aktualizacją linków
  w `README.md`, `docs/README.md` i komentarzach kodu (grep po ścieżkach).
