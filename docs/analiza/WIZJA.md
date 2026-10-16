# Wizja produktu

Wersja 0.1 (2026-10-16), [BA]. Źródła: `docs/01-problem-i-zakres.md`, `docs/SPECYFIKACJA.md`,
`docs/AUDYT.md`. Założenia: `ZALOZENIA.md` (Z-001, Z-003, Z-004, Z-005).

## Cel

**Jedno miejsce, w którym każda strona procesu importu — logistyka spółek, magazyny, spedytorzy i agencja
celna — widzi ten sam stan kontenera, z historią każdej zmiany i z danymi podzielonymi między spółki
i partnerów.** Aplikacja zastępuje arkusz Excel rozsyłany mailem.

## Problem

Grupa kilku spółek sprowadza ok. 200 kontenerów miesięcznie. Kolejkę dostaw prowadzono w jednym arkuszu
na SharePoincie, edytowanym przez operatora i rozsyłanym mailem. Skutki: brak jednego statusu kontenera,
brak historii zmian, brak walidacji numerów, gubienie informacji między wersjami pliku, partnerzy
pracujący na kopiach. Utrzymanie arkusza zajmowało 4 osobom ok. 30 godzin tygodniowo.
Szczegóły: `docs/01-problem-i-zakres.md`.

## Użytkownicy

| Kto | Czego potrzebuje | Rola |
|---|---|---|
| Logistyka spółki i grupy | planować dostawy, pilnować odprawy i terminów, uzgadniać awizację | `logistics` |
| Magazyn (własny, zewnętrzny) | wiedzieć, co i kiedy przyjedzie; potwierdzić rozładunek | `warehouse` |
| Spedytor | dostać zlecenie, potwierdzić termin, podać kierowcę — także bez konta (link) | `forwarder` / link |
| Agencja celna | widzieć zlecone odprawy i dokumenty, raportować status | `customs` |
| Zakupy, sprzedaż | śledzić zamówienia i dostępność towaru | `purchasing`, `sales` |
| Administrator | konta, słowniki, konfiguracja, audyt | `admin` |

Pełna lista interesariuszy: `INTERESARIUSZE.md`. W fazie testów korzysta ok. 4 osób logistyki i 1 magazyn (Z-003).

## Mierniki sukcesu (propozycja, Z-004)

Żaden miernik nie jest dziś mierzony. Wartości docelowe wymagają decyzji PO.

| ID | Miernik | Stan wyjściowy | Cel (propozycja) | Jak mierzyć |
|---|---|---|---|---|
| M-1 | Czas pracy logistyki nad kolejką tygodniowo | ok. 30 h (4 osoby, arkusz) | ≤ 10 h | wywiad z użytkownikami raz na kwartał |
| M-2 | Udział kontenerów prowadzonych w aplikacji (nie w Excelu) | nieznany, okres przejściowy | 100 % po wyjściu z Excela | kontenery utworzone w aplikacji vs z importu/synchronizacji |
| M-3 | Błędne numery kontenerów zatrzymane walidacją ISO 6346 | nieznany | raportowany miesięcznie | odrzucenia 422 w logu żądań |
| M-4 | Aktywni użytkownicy tygodniowo, per rola | nieznany | wszystkie role z `INTERESARIUSZE.md` aktywne | `users.last_seen` |
| M-5 | Awizacje potwierdzone przez spedytora w terminie ważności linku | nieznany | ≥ 90 % | tokeny awizacji użyte vs wygasłe |
| M-6 | Czas od odprawy (ODPRAWIONY) do rozładunku (DOSTARCZONY) | nieznany | trend malejący | `audit_log` zmian statusu |
| M-7 | Incydenty wycieku danych między spółkami/partnerami | 0 znanych | 0 | rejestr ryzyk, audyt dostępu |

## Zakres

- **Rdzeń (Must):** kolejka, cykl kontenera (10 statusów), odprawa celna (9 statusów), dokumenty dostawy,
  plan i awizacja (dwuetapowe linki), rozładunek, separacja danych, historia zmian, import z Excela,
  powiadomienia. Wymagania: `WYMAGANIA.md` (FR-001…FR-028).
- **Moduły poboczne (Could, Z-005):** wyceny i zlecenia transportu, śledzenie statków (AIS), faktury i SAD,
  reklamacje, wywołania palet, kartoteka dostawców, analityka, baza wiedzy, asystent (lokalny LLM),
  poczekalnia dokumentów. Zaimplementowane; bez nowych prac do decyzji PO.
- **Poza zakresem:** zapis do SAP, tracking u armatora (planowany powrót, D10), twarde blokady statusów
  (D4, D5), publiczne linki dla klienta i kierowcy (usunięte, D11).

## Zasady produktu

1. **Ostrzegaj, nie blokuj.** Brak dokumentu albo przekroczony limit magazynu = ostrzeżenie i ślad w historii,
   nie blokada (D4, D5). Decyzja zostaje u człowieka.
2. **Jedno źródło prawdy.** Jedno pole daty dostawy ze statusem planu (D1); Excel nigdy nie cofa stanu
   z aplikacji (D6).
3. **Każda zmiana zostawia ślad.** Kto, kiedy, było → jest, powód (FR-006).
4. **Dane podzielone.** Spółka widzi swoje, partner tylko to, co mu zlecono (FR-022…FR-024).
5. **Partner bez konta też działa.** Jednorazowe, krótko ważne linki zamiast zakładania kont małym spedycjom (D3).
6. **Dane osobowe tylko tyle, ile trzeba, i tylko tak długo, jak trzeba.** Retencje w `../bezpieczenstwo/RODO.md`.

## Horyzont

1. **Teraz:** faza testów z użytkownikami, równolegle z Excelem (synchronizacja ręczna).
2. **Następnie:** wyjście z Excela na produkcji; pilne poprawki z audytu (`HISTORYJKI.md`, Must).
3. **Dalej:** powrót trackingu kontenerów u armatora (D10); decyzje o modułach pobocznych.

## Ograniczenia

Jedna instancja aplikacji (`docs/JEDNA-INSTANCJA.md`), izolacja danych tylko w warstwie aplikacji
(`../bezpieczenstwo/RYZYKA.md` R-01), zależność od usług zewnętrznych włączanych konfiguracją
(M365, SMSAPI, AIS). Kopia zapasowa raz w tygodniu (RPO do 7 dni, decyzja właściciela 2026-09-28).
