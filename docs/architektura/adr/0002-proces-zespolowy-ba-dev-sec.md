# ADR-0002 · Proces zespołowy BA / DEV / SEC z Product Ownerem

- **Status:** przyjęta
- **Data:** 2026-10-16
- **Role:** wszystkie; decyzja PO (polecenie uruchomienia procesu)

## Kontekst

Projekt prowadziła dotąd jedna osoba, z dobrą automatyzacją jakości, ale bez rozdzielenia perspektyw:
wymagania odtwarzano z kodu, ryzyka bezpieczeństwa opisywano w komentarzach i audytach ad hoc, decyzje
o zakresie zapadały bez śladu w backlogu. Repozytorium publiczne ma pokazywać dojrzały proces osobom
z zewnątrz (rekruter, audytor, nowy członek zespołu).

## Rozważane opcje

1. Dalej jednoosobowo, dokumentując post factum.
2. Trzy jawne role (BA, DEV, SEC) z osobnymi artefaktami i krokami, PO jako jedyny decydent; każda zmiana
   przechodzi 7 kroków (`CONTRIBUTING.md`).
3. Pełny proces korporacyjny (komitety, formalne przeglądy) — nieproporcjonalny do skali.

## Decyzja

Opcja 2. Zasady:

- Każdy krok podpisany rolą (**[BA]**, **[DEV]**, **[SEC]**); role nie mieszają się w jednym kroku.
- **BA nie pisze kodu**; gdy wymaganie jest niejasne — pyta PO; brak odpowiedzi = bezpieczne minimum
  w `docs/analiza/ZALOZENIA.md` ze statusem „do potwierdzenia”.
- **DEV nie zmienia zakresu** bez BA/PO i nie wyłącza testów ani kontroli bezpieczeństwa.
- **SEC ma prawo weta**: ryzyko wysokie/krytyczne blokuje merge bez poprawki albo akceptacji PO wpisanej
  w `docs/bezpieczenstwo/RYZYKA.md`.
- **Merge tylko po akceptacji PO** (Z-014); PR-y powstają jako draft.
- Dokumentacja po polsku; kod, nazwy i commity po angielsku (Z-011).
- Definition of Ready i Definition of Done w `CONTRIBUTING.md`; macierz śledzenia w `docs/analiza/SLEDZENIE.md`.

## Konsekwencje

- Więcej artefaktów na funkcję (historyjka, mini-STRIDE, test per kryterium, wpis w macierzy, CHANGELOG);
  w zamian ślad decyzji czytelny dla osoby z zewnątrz.
- Istniejące mechanizmy zostają i są wykorzystywane: `REGULY-PROCESU.md` (reguły), `06-decyzje.md` (D1–D12),
  `tests/permissions.yaml` (wykonywalne wymagania autoryzacji), bramki CI.
- Konflikt ról (np. DEV chce prościej, SEC widzi ryzyko) = obie opcje z konsekwencjami do PO; decyzja
  zapisana w ADR albo w rejestrze ryzyk.
- Po każdym etapie: podsumowanie 5–8 punktów per rola i lista decyzji dla PO.
