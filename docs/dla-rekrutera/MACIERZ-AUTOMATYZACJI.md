# Macierz automatyzacji

Co aplikacja robi sama, co robi razem z człowiekiem, a co zostaje decyzją człowieka — i dlaczego.
Stan na żywo (czy automat działa, ile razy, z jakim efektem): ekran **Automatyzacje** w aplikacji
(`backend/app/automation_catalog.py`). Minuty na efekt to założenia Z-024 (do potwierdzenia przez PO),
zmieniane przez admina na tym samym ekranie.

Admin może wyłączyć automat jednym przełącznikiem (z wpisem w historii zmian); automatów chroniących dane —
usuwania danych kierowców, retencji, osieroconych plików, testu kopii i strażnika — nie da się wyłączyć z ekranu.

**Poziomy:**
- **Pełna** — automat działa i kończy sprawę sam (człowiek tylko widzi wynik).
- **Z człowiekiem** — automat przygotowuje, człowiek zatwierdza jednym kliknięciem.
- **Wspiera decyzję** — automat ostrzega albo podpowiada; decyzja i działanie zostają u człowieka.

## Alerty i pilnowanie terminów

| Automat | Wyzwalacz | Poziom | Co zostaje u człowieka | Min/efekt |
|---|---|---|---|---|
| Ostrzeżenie o karze za przestój | zostało ≤ N dni wolnego czasu w porcie | Wspiera decyzję | czy przyspieszyć odbiór, czy przyjąć koszt | 5 |
| Przeciągająca się odprawa | odprawa zlecona / w rewizji dłużej niż próg | Wspiera decyzję | telefon do agencji, eskalacja | 5 |
| Braki dokumentów przed ETA | ETA za ≤ N dni, brak wymaganego dokumentu | Wspiera decyzję | zdobycie dokumentu od dostawcy | 5 |
| Prognoza przeciążenia magazynu | rozładunków więcej niż limit magazynu | Wspiera decyzję | przesunięcie dostaw | 10 |
| Kamienie milowe trackingu | ETA przekroczone albo statek spóźniony (AIS) | Wspiera decyzję | nowy plan dostawy | 3 |
| Kongestia portów | statki na redzie > 2× mediana z 14 dni | Wspiera decyzję | wybór innego portu / terminu | 5 |
| Nieaktualne dane z SAP | import kartoteki starszy niż próg | Wspiera decyzję | ponowny eksport z SAP | 2 |
| Pilne wywołania palet | analiza z Power BI oznacza produkt jako pilny | Wspiera decyzję | wywołanie palet z magazynu | 5 |
| Reguły własne (kreator bez kodu) | warunek ustawiony przez admina, co godzinę | Wspiera decyzję | reakcja na powiadomienie | 5 |

**Dlaczego nie „pełna”:** każdy z tych alertów kończy się decyzją kosztową albo rozmową z partnerem —
automat ma dopilnować, żeby nikt o niej nie zapomniał, a nie podejmować jej za logistykę.

## Dokumenty i odczyt AI

| Automat | Wyzwalacz | Poziom | Co zostaje u człowieka | Min/efekt |
|---|---|---|---|---|
| Poczta → poczekalnia dokumentów | n8n: mail z załącznikami | Z człowiekiem | „Potwierdź” w poczekalni (albo wskazanie kontenera) | 5 |
| Odczyt faktur (OCR + AI) | nowa faktura w kolejce, co 30 s | Z człowiekiem | decyzja przy niepewnej podpowiedzi modelu | 15 |
| Draft SAD z poczty | n8n: mail od agencji z PDF/XML | Z człowiekiem | akceptacja draftu po porównaniu z fakturami | 10 |
| Szkic reklamacji z opóźnienia | kontener N dni po ETA bez dostawy | Z człowiekiem | sprawdzenie i wysłanie szkicu | 20 |

**Dlaczego „z człowiekiem”:** dokument trafia do zgłoszenia celnego i do rozliczeń — błąd kosztuje
więcej niż kliknięcie. Model ML ustawia dopasowanie sam tylko od progu pewności (`ML_AUTO_APPLY_THRESHOLD`,
domyślnie 90%); panel „Odczyt faktur” na ekranie Automatyzacje pokazuje, czy ten próg się sprawdza.

## Komunikacja

| Automat | Wyzwalacz | Poziom | Co zostaje u człowieka | Min/efekt |
|---|---|---|---|---|
| SMS do kierowcy | dzień przed dostawą, godzina z panelu | Pełna | — | 3 |
| Poranny przegląd dnia | codziennie o ustalonej godzinie | Pełna | — | 15 |
| Tydzień dla zakupów | poniedziałek 8:00 | Pełna | — | 10 |
| Tygodniowy raport automatów | poniedziałek 8:00 | Pełna | reakcja na automaty wymagające uwagi | 15 |
| Przypomnienie o reklamacji | brak odpowiedzi po 15 / 30 dniach | Wspiera decyzję | ponaglenie dostawcy | 3 |
| Zdarzenia do n8n | każde powiadomienie systemu | Pełna | dalsze kroki w n8n / Power Automate / Make | 0 |

## Porządek danych i bezpieczeństwo

| Automat | Wyzwalacz | Poziom | Co zostaje u człowieka | Min/efekt |
|---|---|---|---|---|
| Porządek w awizacjach | raz na dobę | Pełna | — | 0 |
| Usuwanie danych kierowców (RODO) | 30 dni po realizacji | Pełna | — | 2 |
| Retencja dzienników | raz na dobę | Pełna | — | 0 |
| Osierocone pliki | raz na dobę | Pełna | przegląd kwarantanny | 0 |
| Test kopii zapasowej | raz w tygodniu | Pełna | reakcja na raport z błędem | 0 |
| Strażnik automatów | co godzinę: automat bez udanego przebiegu dłużej niż zwykle | Wspiera decyzję | naprawa automatu | 0 |
| Synchronizacja z SharePointem | plik kolejki się zmienił | Pełna | — | 10 |

Automaty porządkowe mają 0 minut: chronią dane i spełniają RODO, ale nie zastępują pracy człowieka 1:1,
więc nie zawyżają licznika oszczędności.

## Czego celowo nie automatyzujemy

- **Zmiana daty dostawy uzgodnionej ze spedytorem** po zmianie ETA — automat ostrzega, data zostaje
  (decyzja D2 w [`06-decyzje.md`](../06-decyzje.md)): obietnica dla magazynu nie może drgać z każdą zmianą ETA.
- **Cofnięcie statusu kontenera** — tylko człowiek, z obowiązkową notatką; o więcej niż krok tylko admin.
- **Zapis przez API partnerów** — publiczne API (ADR-0004, proponowane) jest tylko do odczytu.
