# Excel, Power BI i Power Automate — instrukcje (bez nowego dostępu do danych)

Decyzja PO (2026-10-18): narzędzia Microsoft czytają dane z **eksportu kolejki do Excela**, który użytkownik
pobiera z aplikacji; nie dokładamy nowego dostępu do API (publiczne API z kluczami per spółka — ADR-0004 —
zostaje propozycją). Plik ma ten sam zakres danych co ekran kolejki tej osoby: tylko jej spółki i partnerzy.

Zdarzenia z aplikacji (powiadomienia) do Power Automate idą istniejącym kanałem z podpisem HMAC —
[`ZDARZENIA-N8N.md`](ZDARZENIA-N8N.md).

## 0. Skąd plik

Kolejka → przefiltruj (np. „bieżący miesiąc” albo „wszystkie otwarte”) → **Eksport do Excela**.
Plik `kolejka_RRRR-MM-DD.xlsx`, arkusz `KOLEJKA`, kolumny:

| Kolumna | Typ | Uwagi |
|---|---|---|
| DATA AWIZACJI | data `DD.MM.RRRR` | pusta = brak planu |
| NR KONTENERA | tekst | ISO 6346 |
| SPÓŁKA | tekst | |
| DOSTAWCA | tekst | ukryty dla magazynu i agencji (puste) |
| NR ZAMÓWIENIA | tekst | |
| ETA | data `DD.MM.RRRR` | |
| ATD | data `DD.MM.RRRR` | faktyczne wypłynięcie |
| STATUS | tekst | 10 etapów, np. `W_PORCIE`, `ODPRAWA` |
| STATUS ODPRAWY | tekst | np. `ZLECONA`, `ODPRAWIONY` |
| STATUS DOKUMENTÓW | tekst | `BRAK` / `ZALACZONE` / `WYSLANE` |
| SPEDYTOR | tekst | |
| MAGAZYN | tekst | |
| PORT | tekst | |
| STATEK | tekst | |
| TRANSPORT | tekst | |
| WIELKOŚĆ | tekst | np. `40HC` |
| DOKUMENTY | `TAK` / puste | komplet wymaganych dokumentów |
| AGENCJA CELNA | tekst | |
| DNI WOLNE OD DEMURRAGE | liczba | |
| NR DOSTAWY | tekst | |
| NR RF | tekst | |
| OPÓŹNIONY | `TAK` / puste | |
| UWAGI | tekst | |

**Praktyka:** zapisuj eksport zawsze w tym samym folderze na SharePoincie / OneDrive (np. `Eksporty TIMPORYE`).
Zapytania niżej biorą **najnowszy plik z folderu**, więc odświeżenie raportu = wgranie nowego eksportu.

## 1. Excel — Power Query (10 min)

Dane → Pobierz dane → **Z innych źródeł → Puste zapytanie** → Edytor zaawansowany → wklej:

```powerquery
let
    // adres folderu SharePoint z eksportami (Kopiuj link do folderu, bez „/Forms/...”)
    Witryna = "https://twojafirma.sharepoint.com/sites/Logistyka",
    Folder  = "Eksporty TIMPORYE",

    Pliki   = SharePoint.Files(Witryna, [ApiVersion = 15]),
    Eksporty = Table.SelectRows(Pliki, each Text.StartsWith([Name], "kolejka_")
                                         and [Extension] = ".xlsx"
                                         and Text.Contains([Folder Path], Folder)),
    Najnowszy = Table.First(Table.Sort(Eksporty, {{"Date modified", Order.Descending}})),
    Skoroszyt = Excel.Workbook(Najnowszy[Content], true),
    Kolejka   = Skoroszyt{[Item = "KOLEJKA", Kind = "Sheet"]}[Data],

    PL = "pl-PL",
    // puste komórki dat zapisane jako pusty tekst → null (inaczej zmiana typu da błąd)
    BezPustych = Table.ReplaceValue(Kolejka, "", null, Replacer.ReplaceValue,
        {"DATA AWIZACJI", "ETA", "ATD", "DNI WOLNE OD DEMURRAGE"}),
    Typy = Table.TransformColumnTypes(BezPustych, {
        {"DATA AWIZACJI", type date}, {"ETA", type date}, {"ATD", type date},
        {"DNI WOLNE OD DEMURRAGE", Int64.Type}}, PL),
    Flagi = Table.TransformColumns(Typy, {
        {"DOKUMENTY", each _ = "TAK", type logical},
        {"OPÓŹNIONY", each _ = "TAK", type logical}}),
    DniDoETA = Table.AddColumn(Flagi, "DNI DO ETA",
        each if [ETA] = null then null else Duration.Days([ETA] - Date.From(DateTime.LocalNow())), Int64.Type)
in
    DniDoETA
```

Plik lokalny zamiast SharePointa: zamień trzy pierwsze kroki na
`Skoroszyt = Excel.Workbook(File.Contents("C:\Eksporty\kolejka_2026-10-18.xlsx"), true)`.

Gotowe widoki w Excelu (tabela przestawna z zapytania):
- **Dostawy w tygodniu** — wiersze: `DATA AWIZACJI` (grupowanie po dniach), kolumny: `MAGAZYN`, wartości: liczba `NR KONTENERA`.
- **Ryzyko kary** — filtr `DNI WOLNE OD DEMURRAGE` ≤ 3 i `STATUS` ≠ `DOSTARCZONY`/`ZREALIZOWANY`.
- **Braki dokumentów** — filtr `DOKUMENTY` = FAŁSZ i `DNI DO ETA` ≤ 7.

## 2. Power BI Desktop (20 min)

1. **Pobierz dane → Puste zapytanie**, wklej to samo zapytanie co w Excelu, nazwij tabelę `Kolejka`.
2. **Tabela dat** (Modelowanie → Nowa tabela):

   ```dax
   Kalendarz = CALENDAR ( DATE ( 2026, 1, 1 ), DATE ( 2027, 12, 31 ) )
   ```

   Relacja: `Kalendarz[Date]` 1 → * `Kolejka[DATA AWIZACJI]`.
3. **Miary** (Nowa miara):

   ```dax
   Kontenery = COUNTROWS ( Kolejka )

   W obiegu =
       CALCULATE ( [Kontenery], NOT Kolejka[STATUS] IN { "DOSTARCZONY", "ZREALIZOWANY" } )

   Opóźnione = CALCULATE ( [Kontenery], Kolejka[OPÓŹNIONY] = TRUE () )

   % opóźnionych = DIVIDE ( [Opóźnione], [W obiegu] )

   Ryzyko kary =
       CALCULATE ( [W obiegu], Kolejka[DNI WOLNE OD DEMURRAGE] <= 3 )

   Braki dokumentów przed ETA =
       CALCULATE ( [W obiegu], Kolejka[DOKUMENTY] = FALSE (), Kolejka[DNI DO ETA] <= 7 )

   Komplet dokumentów % =
       DIVIDE ( CALCULATE ( [W obiegu], Kolejka[DOKUMENTY] = TRUE () ), [W obiegu] )
   ```

4. **Strona raportu** (propozycja układu):
   - karty: `W obiegu`, `% opóźnionych`, `Ryzyko kary`, `Braki dokumentów przed ETA`,
   - słupki skumulowane: oś `Kalendarz[Date]` (tydzień), wartość `Kontenery`, legenda `MAGAZYN` — obciążenie magazynów,
   - słupki poziome: `STATUS` × `Kontenery` — gdzie stoi kolejka,
   - tabela: `NR KONTENERA`, `STATUS`, `ETA`, `DNI WOLNE OD DEMURRAGE`, `DOKUMENTY` z filtrem `Ryzyko kary` > 0.
5. **Publikacja i odświeżanie:** opublikuj w usłudze Power BI; źródło SharePoint nie wymaga bramy (gateway).
   Odświeżanie zaplanowane albo z Power Automate (niżej, przepływ B).

Gotowego pliku `.pbit` nie dołączamy: szablon zależy od adresu witryny SharePoint i układu, który i tak się
dostosowuje — zapytanie i miary wyżej odtwarzają model w kilka minut.

## 3. Power Automate (15 min)

### Przepływ A — powiadomienie z aplikacji → zadanie w Plannerze / wiadomość w Teams

1. Wyzwalacz **„When an HTTP request is received”** (Premium). Skopiuj adres wyzwalacza do zmiennej aplikacji
   `AUTOMATION_WEBHOOK_URL` (to ten sam kanał co n8n — aplikacja wysyła tam każde powiadomienie).
2. Schemat JSON treści — wklej przykład z [`ZDARZENIA-N8N.md`](ZDARZENIA-N8N.md) („Generate from sample”).
3. **Condition:** `event` równa się `demurrage` albo `docs-missing`.
4. Tak → **Create a task** (Planner): tytuł = `title`, opis = `body`; albo **Post message in a chat or channel** (Teams).
5. Ponowienia: zapisz `id` zdarzenia (np. w liście SharePoint) i pomiń, jeśli już jest — wysyłka może się powtórzyć.

**Podpis HMAC:** Power Automate nie ma wbudowanej weryfikacji HMAC. Adres wyzwalacza zawiera własny podpis (`sig=`)
— traktuj go jak hasło i nie wklejaj nigdzie poza zmienną aplikacji. Gdy potrzebna jest pełna weryfikacja
podpisu, przepuść zdarzenia przez n8n ([`WLASNA-AUTOMATYZACJA-15-MIN.md`](WLASNA-AUTOMATYZACJA-15-MIN.md)) albo
Azure Function z przykładem w Pythonie z [`ZDARZENIA-N8N.md`](ZDARZENIA-N8N.md).

### Przepływ B — nowy eksport w folderze → odśwież raport Power BI

1. Wyzwalacz **„When a file is created in a folder”** (SharePoint), folder `Eksporty TIMPORYE`.
2. **Condition:** nazwa pliku zaczyna się od `kolejka_`.
3. **Refresh a dataset** (Power BI) — wybierz zestaw danych z raportu z sekcji 2.
4. Opcjonalnie **Post message** do kanału logistyki: „Raport kolejki odświeżony (plik …)”.

## Czego te instrukcje nie robią

- Nie pobierają danych z aplikacji automatycznie — eksport robi człowiek (decyzja PO, bez nowego dostępu do API).
- Nie zapisują niczego do aplikacji — Excel i Power BI są tylko do odczytu.
- Pełna automatyzacja bez ręcznego eksportu wymaga publicznego API z kluczami per spółka (ADR-0004, czeka na PO).
