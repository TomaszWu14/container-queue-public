# 01. Problem i zakres

## Problem

Kilka spółek jednej grupy sprowadza towar w kontenerach morskich. Kolejką dostaw zarządzano
w jednym arkuszu Excel (`KOLEJKA KONTENERÓW`), który leżał na SharePoincie, był edytowany przez
operatora i rozsyłany mailem do pozostałych stron.

Skutki, które wynikają z tego układu:

- **Brak jednego statusu.** Arkusz znał tylko status odprawy (BRAK / ZLECONA / ODPRAWIONY).
  Etapu kontenera nie było, każdy wyciągał go z dat po swojemu
  (`backend/app/importers/queue.py:158-182`).
- **Brak historii.** Nie było wiadomo, kto zmienił datę dostawy i dlaczego.
- **Brak widoczności dla partnerów.** Magazyny, spedytorzy i agencja celna pracowali na
  kopiach pliku albo na mailach.
- **Awizacja i dokumenty mailem.** Termin dostawy ustalano korespondencją ze spedytorem,
  drafty zgłoszeń celnych przychodziły jako załączniki (`tools/outlook-sad/Zbierz-SAD.ps1`).

Skala i koszt: `<DO UZUPEŁNIENIA: liczba kontenerów miesięcznie, liczba osób zaangażowanych,
koszt przestoju / demurrage, czas tygodniowo na uzgadnianie arkusza>`.
Jedyna liczba z dokumentacji projektu: przy migracji z Excela wczytano **214 kontenerów, z czego 84
zrealizowane** (`docs/SPECYFIKACJA.md`, §8).

## Cel

Jedno miejsce, w którym każda strona widzi ten sam stan kontenera — od zamówienia, przez
statek i odprawę celną, po rozładunek w magazynie — z historią każdej zmiany i z podziałem
danych między spółki i partnerów.

## Interesariusze

| Interesariusz | Rola w systemie | Czego potrzebuje |
|---|---|---|
| Logistyka spółki | `logistics` | planować dostawy, pilnować odprawy i terminów, uzgadniać awizację |
| Logistyka grupy | `logistics` + widok wszystkich spółek | jeden obraz kolejki wszystkich spółek |
| Magazyn (własny lub zewnętrzny) | `warehouse` | wiedzieć, co przyjedzie i kiedy; potwierdzić rozładunek |
| Spedytor | `forwarder` albo link bez konta | dostać zlecenie, potwierdzić termin, podać dane kierowcy |
| Agencja celna | `customs` | widzieć zlecone odprawy i dokumenty, raportować status odprawy |
| Zakupy | `purchasing` | śledzić zamówienia i dokumenty handlowe |
| Sprzedaż | `sales` | wiedzieć, kiedy towar będzie dostępny (tylko odczyt) |
| Administrator | `admin` | konta, słowniki, konfiguracja, audyt |

Role są zdefiniowane w `backend/app/models/enums.py:32-39`, a zakres widoczności każdej roli —
w `backend/app/deps.py:60-142`. Wymagania zebrano w wywiadzie projektowym (50 pytań, 02.07.2026)
— zapis: [`SPECYFIKACJA.md`](SPECYFIKACJA.md).

## Zakres tej dokumentacji

Dokumenty 02–07 opisują **rdzeń procesu**:

**kontener → śledzenie → odprawa celna → plan i awizacja dostawy → rozładunek → rozliczenie**

To jest ta część, która zastąpiła arkusz kolejki. Aplikacja ma więcej modułów (patrz niżej);
są zaimplementowane, ale tu opisane tylko jednym zdaniem, żeby nie zasłaniały głównego procesu.

### W zakresie (rdzeń)

| Obszar | Co robi system | Dokument |
|---|---|---|
| Kolejka kontenerów | lista dostaw pogrupowana datami, filtry, eksport do Excela | [03](03-user-flow.md) |
| Cykl życia kontenera | 10 statusów z regułami cofania | [02](02-proces.md) |
| Odprawa celna | osobny status odprawy, zlecenie agencji, automat statusu kontenera | [02](02-proces.md) |
| Dokumenty dostawy | załączniki z typem, kafelki wymaganych dokumentów, bramka zgodności | [05](05-wymagania.md) |
| Plan i awizacja | propozycja daty, limit dzienny magazynu, sloty, awizacja dwuetapowa ze spedytorem | [02](02-proces.md), [03](03-user-flow.md) |
| Rozładunek | brama, rampa, potwierdzenie DOSTARCZONY przez magazyn | [02](02-proces.md) |
| Separacja danych | każda spółka i każdy partner widzi tylko swoje kontenery | [05](05-wymagania.md) |
| Historia zmian | audyt każdego pola: kto, kiedy, było → jest, powód | [05](05-wymagania.md) |
| Import z Excela | wczytanie i synchronizacja dawnego arkusza kolejki | [06](06-decyzje.md) |

### Moduły poboczne (zaimplementowane, poza tą dokumentacją)

Wyceny transportu (RFQ) i zlecenia transportowe, śledzenie statków (AIS), powiadomienia
(e-mail, Teams, SMS do kierowców), faktury i import zgłoszeń SAD, reklamacje, wywołania palet
z magazynu zewnętrznego, kartoteka dostawców, analityka, baza wiedzy. Szczegóły techniczne:
[`TECHNICZNE.md`](TECHNICZNE.md).

### Poza zakresem — czego system świadomie nie robi

| Czego nie ma | Dlaczego | Źródło |
|---|---|---|
| Zapisu do SAP | system tylko czyta pliki eksportu i raporty Power BI; SAP pozostaje źródłem zamówień | `backend/app/routers/imports_master.py`, `backend/app/powerbi.py` |
| Trackingu kontenerów u armatora | integracja z zewnętrznym dostawcą została usunięta decyzją biznesową; ETA wpisuje logistyka albo import z Excela, statki śledzi AIS | `docs/SPECYFIKACJA.md` §4, `backend/app/tracking/service.py:1-4` |
| Publicznego linku dla klienta i strony kierowcy | usunięte 2026-10-07; publiczne zostały tylko formularze awizacji i wywołania palet | `backend/app/models/links.py:1` — powód `<DO UZUPEŁNIENIA>` |
| Twardej blokady statusu przy brakujących dokumentach | brak dokumentu daje ostrzeżenie z powodem w historii, nie blokadę | [06-decyzje.md](06-decyzje.md), D4 |
| Twardej blokady limitu dziennego magazynu | przekroczenie = ostrzeżenie i wpis „kto zignorował limit” | [06-decyzje.md](06-decyzje.md), D5 |
| Automatycznej zmiany statusu z bramy i rozładunku | brama i rampa to osobny wymiar (`ramp_stage`); status DOSTARCZONY potwierdza człowiek | `backend/app/routers/warehouse_ops.py:107` |
| Anulowania zlecenia transportowego | obieg zlecenia nie ma stanu „anulowane”; są tylko korekty z powodem | `backend/app/routers/forwarding.py:79-98` |
