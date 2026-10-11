# 07. Ograniczenia, znane problemy, co dalej

Obserwacje z analizy kodu (commit `9dd73a1`). To lista stanu, nie plan prac.
Ścieżki `backend/app/` skrócone, `frontend/src/` jako `FE/`.

## Czego system nie robi

Pełna lista z uzasadnieniem: [01-problem-i-zakres.md](01-problem-i-zakres.md#poza-zakresem--czego-system-świadomie-nie-robi).
W skrócie: nie zapisuje do SAP, nie śledzi kontenerów u armatora, nie blokuje statusu przy brakach
dokumentów ani przy przekroczonym limicie magazynu, nie ma publicznego linku dla klienta.

## Ograniczenia architektury

- **Jedna instancja.** Część stanu (limity żądań, wynik ostatniej integracji) jest w pamięci
  procesu. Kilka instancji wymaga przejścia kontraktu z [`JEDNA-INSTANCJA.md`](JEDNA-INSTANCJA.md).
- **Izolacja danych tylko w aplikacji.** Baza nie wymusza zgodności spółki między tabelami
  ([04](04-model-danych.md)).
- **Zależność od usług zewnętrznych.** Śledzenie statków wymaga klucza AIS, wysyłka maili
  awizacji — konfiguracji poczty (Microsoft 365 albo SMTP).

## Znane problemy

| # | Problem | Skutek | Kod |
|---|---|---|---|
| P-01 | Odpowiedź na awizację w aplikacji pokazuje sukces przy błędzie 409 | spedytor myśli, że odpowiedział, a nic nie zapisano | `FE/pages/AvizoFormPage.tsx:185`, `routers/avizo_forwarder.py:54-58` |
| P-02 | Dwie różne reguły „ETA + N”: 4 dni przy zakładaniu kontenera, 3 dni w podpowiedzi daty | dwie różne proponowane daty dla tej samej sytuacji | `planning.py:18`, `routers/containers_planning.py:119-121` |
| P-03 | Zmiana ETA nie przelicza propozycji daty, choć opis w kodzie mówi, że powinna | propozycja daty starzeje się po zmianie ETA | `planning.py:1-7`, `routers/containers_write.py:63-64` |
| P-04 | Import z Excela: tekst „nieodprawiony” daje status ODPRAWIONY | błędny status odprawy po imporcie | `importers/queue.py:215-216` |
| P-05 | Numer 9-cyfrowy kierowcy zawsze dostaje prefiks +48 | numer portugalski staje się polskim, SMS nie dochodzi | `routers/avizo.py:322-323` |
| P-06 | Nowe magazyny zawsze z krajem PL | magazyn w Portugalii dostaje polskie święta | `routers/containers_write.py:266`, `importers/queue.py:207-208` |
| P-07 | Alert przeciągającej się odprawy pomija statusy DRAFT_* | odprawa może wisieć bez alertu | `notification_alerts.py:240` |
| P-08 | Alert „ETA minęło” ma okno jednego dnia | jeśli zadanie nie przebiegnie danego dnia, alertu nie będzie | `notification_alerts.py:157-160` |
| P-09 | „Wyślij plan do spedycji” nie wysyła maila, tylko zmienia status | spedytor dowie się o planie dopiero z aplikacji | `routers/containers_planning.py:40-65` |
| P-10 | Wybór zwycięskiej oferty nie przypisuje spedytora do kontenera | potrzebny osobny ręczny krok | `routers/quotes_offers.py:173-228` |
| P-11 | Zdarzenia do n8n ignorują odpowiedzi 4xx/5xx | nieudane zdarzenie znika bez śladu | `notifications.py:263` |
| P-12 | Maile powiadomień (SMTP) bez ponawiania; bez skonfigurowanego serwera pomijane po cichu | utracone powiadomienia | `notifications.py:121-144` |
| P-13 | Edycje równoległe statusu, odprawy i zleceń transportowych bez kontroli wersji | ostatni zapis nadpisuje poprzedni bez ostrzeżenia | `routers/containers_write.py:243-253`, `routers/customs.py:434` |
| P-14 | Dokumentacja projektu częściowo nieaktualna (sloty, ważność linków, liczba etapów) | czytelnik dostaje sprzeczne reguły | patrz niżej |

Rejestr błędów zgłoszonych wcześniej: [`BUGS-FOUND.md`](../BUGS-FOUND.md); długi UX: [`UX_AUDIT.md`](../UX_AUDIT.md).

## Miejsca bez walidacji lub obsługi błędów

Granice, przez które do systemu wchodzą dane z zewnątrz.

| # | Granica | Obserwacja | Kod |
|---|---|---|---|
| T-01 | Publiczny link wywołania palet | brak własnego limitu żądań i kontroli pochodzenia (awizacja je ma) | `routers/dlt.py:71-136` |
| T-02 | Publiczny formularz awizacji | limit żądań w pamięci procesu — przy kilku instancjach mnoży się | `routers/avizo.py:46-55` |
| T-03 | Wolne sloty z linku awizacji | parametr daty bez zakresu | `routers/avizo.py:217-225` |
| T-04 | Poczta przychodząca do poczekalni | brak listy zaufanych nadawców | `routers/intake_mail.py:32-45` |
| T-05 | Upload załącznika | typ pliku rozpoznawany tylko po rozszerzeniu | `routers/forwarding_files.py:177-186` |
| T-06 | Archiwum ZIP | limit rozmiaru liczony z deklaracji w nagłówku archiwum | `routers/archive_upload.py:47-69` |
| T-07 | Import Excela | wiersze z błędnym numerem pomijane tylko w logu; użytkownik nie dostaje listy | `importers/queue.py:347-351` |
| T-08 | SharePoint (Microsoft Graph) | nieoczekiwana odpowiedź kończy się błędem 500 | `sharepoint.py:64,76` |
| T-09 | Serwis paletyzacji | odpowiedź bez walidacji, błąd parsowania = 500 | `routers/containers.py:313-323` |
| T-10 | AIS (websocket) | ramka w innym formacie niż słownik przerywa obsługę | `tracking/ais.py:196-200` |
| T-11 | Pogoda (Open-Meteo) | brak sprawdzenia kodu odpowiedzi | `tracking/weather.py:88-99` |
| T-12 | Kursy NBP | przy awarii zwracane kursy bez limitu wieku | `nbp.py:42-46` |
| T-13 | Dane kierowcy w panelu | brak walidacji telefonu i rejestracji (formularz publiczny je ma) | `schemas/dictionaries.py:236-244` |
| T-14 | Dni wolne demurrage | brak dolnej granicy — wartość ujemna przesuwa termin wstecz | `schemas/containers.py:51,111` |
| T-15 | Pola tekstowe kontenera | brak limitu długości w schemacie (limit tylko w bazie → 500) | `schemas/containers.py:23-61` |
| T-16 | Zlecenie transportowe | brak sprawdzenia, że odbiór jest przed dostawą | `schemas/transport.py:12-19` |
| T-17 | Ustawienia administratora jako tekst | brak odrzucenia wartości ujemnych | `routers/containers_planning.py:118-121` |
| T-18 | Token automatyzacji (n8n) | ograniczenie do sieci jest opcjonalne | `automation_policy.py:66-70` |
| T-19 | Power BI | timeout kończy się błędem 500 zamiast ostatnich danych z pamięci podręcznej | `pallets_cache.py:117-130` |
| T-20 | Wywołanie palet | status „wysłane” ustawiany, zanim mail faktycznie wyjdzie | `routers/pallets.py:345-347` |

## Dokumentacja niezgodna z kodem

| Dokument | Co mówi | Co jest w kodzie |
|---|---|---|
| `SPECYFIKACJA.md` §3 | awizacja bez slotów godzinowych | sloty z pojemnością (`slots.py`) |
| `mapa-procesow-szczegolowa.md`, `workflow-aplikacji-2026-09-16.md` | link awizacji ważny 14 dni; brak maszyny stanów; magazyn ustawia ZREALIZOWANY | 7 i 5 dni; maszyna stanów (`containers_common.py:333-343`); ZREALIZOWANY ustawia logistyka |
| `REGULY-PROCESU.md` | linki publiczne dla klienta i kierowcy | usunięte 2026-10-07 |
| `mapa-procesu-timporye.md` | 6 ról, mapa Google Maps | 7 ról (jest `sales`), mapa z kafelków lokalnych |
| `SHAREPOINT-SYNC.md` | synchronizacja automatyczna | domyślnie ręczna (`config.py:229`) |

Dokumenty 01–07 opisują stan z kodu i mają pierwszeństwo przed starszymi opisami w `docs/`.

## Co dalej

`<DO UZUPEŁNIENIA: priorytety dalszego rozwoju — np. zamknięcie okresu przejściowego z Excelem,
decyzja o maszynie stanów odprawy, ujednolicenie reguły ETA + N>`

Lista pomysłów na automatyzację: [`pomysly-automatyzacje.md`](pomysly-automatyzacje.md).
