# 06. Dziennik decyzji projektowych

Decyzje dotyczące rdzenia procesu. Źródła uzasadnień: specyfikacje projektowe
(`docs/superpowers/specs/`), rejestr reguł ([`REGULY-PROCESU.md`](REGULY-PROCESU.md)),
specyfikacja z wywiadu ([`SPECYFIKACJA.md`](SPECYFIKACJA.md)) i komentarze „decyzja” w kodzie.
Tam, gdzie powód nie został nigdzie zapisany, jest to zaznaczone.

---

## D1. Jedno pole daty dostawy plus status planu

- **Kontekst.** Data dostawy przechodzi od propozycji systemu do terminu potwierdzonego przez
  spedytora. Trzeba odróżnić datę pewną od niepewnej.
- **Rozważane opcje.** (a) dwa pola: propozycja i data potwierdzona; (b) jedno pole `notify_date`
  plus status PROPOZYCJA / WYSLANE / POTWIERDZONE.
- **Wybór: (b).** Dwa pola wymagałyby rozstrzygania „które jest prawdziwe” w każdym zapytaniu,
  powiadomieniu i eksporcie. Jedno pole ze statusem to jedno źródło prawdy.
- **Skutki.** Kolejka od pierwszego dnia zawiera niepewne daty; łagodzi to wizualny podział
  sekcji i to, że limit magazynu liczy tylko daty potwierdzone. Pole `proposed_delivery_date`
  zostało w modelu nieużywane.
- **Źródło.** `specs/2026-09-02-plan-dostaw-potwierdzenie-spedycji-design.md`, „Decyzje projektowe”.

## D2. Zamrożenie uzgodnionej daty zamiast przeliczania po zmianie ETA

- **Kontekst.** ETA statku zmienia się często. Data dostawy uzgodniona ze spedytorem jest obietnicą
  dla magazynu.
- **Rozważane opcje.** (a) cofać potwierdzenie przy każdej zmianie ETA; (b) zamrozić datę po
  wysłaniu planu i ostrzegać człowieka.
- **Wybór: (b).** Opcja (a) wywraca obietnicę „zaplanowane” i generuje szum przy każdym drgnięciu ETA.
- **Skutki.** Rozbieżność ETA i daty wymaga decyzji logistyka. W obecnym kodzie przeliczanie po
  zmianie ETA nie działa także w stanie PROPOZYCJA (automat opisany w `planning.py:1-7` nie
  istnieje) — patrz [07](07-ograniczenia.md).
- **Źródło.** jw.; `planning.py:51-135`.

## D3. Spedytor może działać bez konta — jednorazowe linki

- **Kontekst.** Część spedycji to małe firmy, które nie będą zakładać kont w systemie klienta.
- **Rozważane opcje.** (a) tylko portal z kontami; (b) tylko linki z e-maila; (c) portal jako
  główna droga, link jako zapas.
- **Wybór: (c).** Sam portal wykluczyłby małe spedycje z procesu planowania; same linki zostawiłyby
  moduł spedycji bez użytkowników.
- **Skutki.** Linki są jednorazowe, osobne dla etapu 1 i 2, ważne 7 i 5 dni; w bazie jest tylko
  skrót SHA-256, więc wyciek bazy nie otwiera formularzy. Publiczne endpointy mają limit żądań
  i kontrolę pochodzenia (`routers/avizo.py:44-70`). Odpowiedź w aplikacji unieważnia link tego etapu.
- **Źródło.** `specs/2026-09-02-plan-dostaw-potwierdzenie-spedycji-design.md`; `avizo_workflow.py:1-10`.

## D4. Braki dokumentów: ostrzeżenie, nie blokada

- **Kontekst.** Do odprawy i rozładunku potrzebne są dokumenty (PI, CI, PL, BL, SAD), ale fizyczny
  towar nie czeka na papier.
- **Rozważane opcje.** (a) blokować zmianę statusu i wysyłkę do agencji; (b) ostrzegać
  i zapisywać fakt w historii.
- **Wybór: (b).** Decyzja zostaje u człowieka, a system zostawia ślad, kto zdecydował mimo braków.
- **Skutki.** Status DOSTARCZONY i odprawa ODPRAWIONY / ZWOLNIONY zapisują się z ostrzeżeniem.
  Wysyłka do agencji wymaga jawnego „wyślij mimo to”.
- **Źródło.** `specs/2026-10-06-dokumenty-dostaw-design.md` (decyzja 9),
  `specs/2026-09-01-kompletnosc-dokumentow-celnych-design.md` (decyzja 3); `document_tiles.py:165`.

## D5. Limit dzienny magazynu: ostrzeżenie, nie blokada

- **Kontekst.** Magazyn ma domyślny limit rozładunków dziennie z możliwością nadpisania na dzień.
- **Wybór.** Przekroczenie limitu jest dozwolone; system ostrzega i zapisuje w historii, kto
  zignorował limit.
- **Dlaczego.** Ustalone w wywiadzie projektowym (`SPECYFIKACJA.md` §3) i potwierdzone 2026-09-28
  (`REGULY-PROCESU.md`). Pilne dostawy muszą się zmieścić mimo limitu, więc decyzja zostaje
  u człowieka; system pilnuje tylko, żeby było wiadomo, kto limit przekroczył.
- **Skutki.** Do limitu liczą się tylko dostawy potwierdzone, niezakończone i nie-tranzytowe
  (`planning.py:92-115`).

## D6. Okres przejściowy z Excelem: aplikacja nie jest cofana przez arkusz

- **Kontekst.** Arkusz kolejki na SharePoincie był używany równolegle z aplikacją. Na etapie
  projektu IT nie zgodziło się na rejestrację aplikacji w Entra ID, co wykluczyło serwerowy dostęp
  do SharePointa.
- **Rozważane opcje.** Faza A: Excel źródłem prawdy, synchronizacja jednokierunkowa.
  Faza B: synchronizacja dwukierunkowa z porównaniem trójstronnym (stan bazowy, Excel, aplikacja)
  i regułą „wygrywa nowsza zmiana”.
- **Wybór (2026-09-28).** Synchronizacja tylko ręczna, a arkusz nigdy nie cofa statusu ani
  odprawy z aplikacji. Konflikty pól rozstrzyga porównanie trójstronne.
- **Skutki.** Czas zmiany po stronie Excela to czas modyfikacji całego pliku — świadomie
  zaakceptowane przybliżenie. Zapis zwrotny do arkusza jest zaprojektowany, ale w repozytorium
  nie ma agenta, który by go wykonywał.
- **Źródło.** `specs/2026-08-31-excel-sharepoint-sync-design.md`, `specs/2026-08-31-excel-sync-faza-b-design.md`;
  `config.py:227`, `importers/queue.py:172-177`.

## D7. Powtórny przyjazd kontenera = nowy rekord

- **Kontekst.** Ten sam fizyczny kontener (ten sam numer ISO) wraca z kolejną dostawą.
- **Wybór.** Numer jest unikalny w spółce tylko wśród kontenerów niezrealizowanych. Kontener
  ZREALIZOWANY to archiwum; nowa dostawa tworzy nowy rekord z uwagą „powtórny numer”.
- **Skutki.** Częściowy indeks unikalny w bazie (`models/container.py:79-81`); import pomija wiersz,
  który jest tą samą, zamkniętą dostawą (ta sama data awizacji lub ETA).
- **Źródło.** `REGULY-PROCESU.md` (N-20, doprecyzowanie 2026-10-05).

## D8. Magazyn potwierdza rozładunek, logistyka zamyka dostawę

- **Kontekst.** Fizyczne przyjęcie towaru i zamknięcie formalności (faktury, dokumenty) to dwa
  różne zdarzenia i dwie różne osoby.
- **Wybór (2026-09-28).** Magazyn ustawia wyłącznie DOSTARCZONY; ZREALIZOWANY ustawia logistyka po
  zamknięciu formalności. Rozładunek kontenera nieawizowanego wymaga od magazynu notatki.
- **Skutki.** DOSTARCZONY zostaje w kolejce do rozliczenia; archiwum to dopiero ZREALIZOWANY.
- **Źródło.** `REGULY-PROCESU.md`; `routers/containers_write.py:214-226`.

## D9. Izolacja danych w jednym miejscu

- **Kontekst.** System obsługuje kilka spółek i partnerów zewnętrznych na jednej bazie.
- **Wybór.** Wszystkie reguły widoczności są w `deps.py` (`scope_containers`, `get_scoped`);
  routery ich nie powielają. Rekord spoza zakresu daje 404, jak rekord nieistniejący.
- **Dlaczego.** Jedna reguła w jednym miejscu jest łatwiejsza do przetestowania niż kopie w każdym
  endpoincie; 404 zamiast 403 nie zdradza, że rekord istnieje.
- **Skutki.** Baza nie wymusza zgodności spółki między tabelami — bezpieczeństwo zależy od tej
  jednej warstwy ([04](04-model-danych.md), niespójność 9).
- **Źródło.** `deps.py:60-142`, `deps.py:363-468`; `CLAUDE.md` repozytorium.

## D10. Wyłączenie zewnętrznego trackingu kontenerów na obecny etap

- **Wybór.** Integracja z dostawcą trackingu kontenerów została usunięta z obecnej wersji; pozycje statków daje AIS,
  a status kontenera zmienia człowiek.
- **Dlaczego.** „Decyzja biznesowa” (`SPECYFIKACJA.md` §4): integracja wyłączona w obecnej wersji,
  a tracking kontenerów jest planowany w kolejnym etapie rozwoju.
- **Źródło.** `tracking/service.py:1-4`.

## D11. Usunięcie publicznych linków dla klienta i kierowcy

- **Wybór (2026-10-07).** Usunięto link „mój kontener” dla klienta i stronę dostawy dla kierowcy.
  Publiczne zostały tylko formularze awizacji i wywołania palet.
- **Dlaczego.** Ryzyko udostępnienia danych osobom trzecim: link przesłany dalej otwierał dane
  dostawy bez logowania. Publiczne zostały tylko formularze, które są jednorazowe i krótko ważne.
- **Skutki.** Informacja o przyjeździe auta do logistyki idzie teraz z bramy magazynu
  (`routers/warehouse_ops.py:139`).
- **Źródło.** `models/links.py:1`.

## D12. FastAPI + PostgreSQL + React

- **Rozważane opcje.** Django, FastAPI, Flask (`SPECYFIKACJA.md` §8).
- **Wybór.** FastAPI: typowane API z automatyczną dokumentacją OpenAPI, z której korzystają panel,
  automatyzacje n8n i integracje. SQLAlchemy z Alembic: ten sam model na SQLite (lokalnie i w testach)
  i na PostgreSQL (produkcja), wersjonowane migracje. React + TypeScript: panel w trzech językach
  serwowany przez backend pod jednym adresem.
- **Źródło.** `README.md` (sekcja o stacku), `SPECYFIKACJA.md` §8.
