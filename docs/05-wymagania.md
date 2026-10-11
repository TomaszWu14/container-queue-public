# 05. Wymagania z kryteriami akceptacji

Wymagania rdzenia procesu, odtworzone z kodu. Każde ma kryterium akceptacji, które da się
sprawdzić, oraz miejsce realizacji i test, który go pilnuje. Testy są w `backend/tests/`;
ścieżki `backend/app/` skrócone do nazwy pliku.

Format kryterium: **Dane** (stan wyjściowy) → **Gdy** (akcja) → **Wtedy** (oczekiwany wynik).

## Kontener i statusy

| ID | Wymaganie | Kryterium akceptacji | Gdzie zrealizowane | Test |
|---|---|---|---|---|
| W-01 | System przyjmuje tylko numer kontenera zgodny z ISO 6346. | Gdy logistyk zapisze numer z błędną cyfrą kontrolną (np. `MSKU1234560`), wtedy zapis jest odrzucony z komunikatem; spacje i małe litery są normalizowane. | `iso6346.py:4-49`, `schemas/containers.py:67-74` | `test_api.py::test_iso6346_validation`, `test_iso6346_remainder10.py` |
| W-02 | Numer kontenera jest unikalny w spółce wśród kontenerów niezrealizowanych. | Dany kontener ZREALIZOWANY o numerze X, gdy przyjedzie znowu kontener X, wtedy powstaje nowy rekord; dwa aktywne kontenery X w jednej spółce są odrzucane. | `models/container.py:79-81` | `test_import_repeat_number.py` |
| W-03 | Status kontenera przechodzi przez 10 etapów; cofnięcie wymaga uzasadnienia. | Gdy użytkownik cofa status o 1 krok bez notatki, wtedy zapis jest odrzucony; o więcej niż 1 krok — odrzucony dla każdego poza administratorem. | `containers_common.py:333-343` | `test_status_flow.py` |
| W-04 | Magazyn potwierdza tylko rozładunek. | Gdy użytkownik z rolą magazynu ustawi status inny niż DOSTARCZONY, wtedy dostaje 403; gdy potwierdza rozładunek kontenera nieawizowanego, musi podać notatkę. | `containers_write.py:216-226` | `test_api.py::test_warehouse_role_limited_to_unload_confirmation` |
| W-05 | Status kontenera wynika ze statusu odprawy, tylko do przodu. | Dany kontener W_PORCIE, gdy agencja ustawi ODPRAWIONY i jest data awizacji, wtedy kontener ma AWIZOWANY; bez daty — ODPRAWA. Automat nigdy nie cofa statusu. | `containers_common.py:443-458` | `test_status_from_customs.py` |
| W-06 | Każda zmiana pola zostaje w historii. | Gdy ktokolwiek zmieni pole kontenera, wtedy historia pokazuje: kto, kiedy, poprzednią i nową wartość oraz notatkę. Dane osobowe kierowcy są maskowane. | `audit.py`, `models/system.py:22` | `test_audit_history.py`, `test_audit_coverage.py` |

## Odprawa celna i dokumenty

| ID | Wymaganie | Kryterium akceptacji | Gdzie zrealizowane | Test |
|---|---|---|---|---|
| W-07 | Status odprawy zmienia agencja celna; logistyka tylko awaryjnie; spedytor nigdy. | Gdy spedytor spróbuje zmienić status odprawy, wtedy dostaje 403. Gdy agencja ustawia REWIZJA bez notatki, wtedy zapis jest odrzucony. | `containers_common.py:347-369` | `test_customs.py` (REWIZJA), `test_document_tiles.py::test_sad_upload_by_forwarder_keeps_customs_status`; brak testu na 403 dla spedytora |
| W-08 | Cofnięcie odprawy z ODPRAWIONY / ZWOLNIONY / ROZLICZONY jest wyjątkiem. | Gdy agencja cofa ODPRAWIONY, wtedy zapis jest odrzucony; logistyka może, ale tylko z notatką. | `containers_common.py:363-369` | `test_customs.py` |
| W-09 | Wysyłka dokumentów do agencji ostrzega o brakach. | Dany kontener bez wymaganego typu dokumentu, gdy logistyk wyśle dokumenty, wtedy dostaje 409 z listą braków; po potwierdzeniu „wyślij mimo to” wysyłka przechodzi, a audyt zapisuje „MIMO braków”. | `customs.py:381-430` | `test_customs.py` |
| W-10 | Brak dokumentów nie blokuje zmiany statusu. | Gdy kontener bez wymaganych dokumentów dostaje DOSTARCZONY albo odprawę ODPRAWIONY / ZWOLNIONY, wtedy status się zapisuje, użytkownik widzi ostrzeżenie, a historia ma wpis z listą braków. | `document_tiles.py:164-181` | `test_required_docs.py` |
| W-11 | Wymagane dokumenty zależą od etapu kontenera. | Dany kontener W_PRODUKCJI wymaga PI; od W_TRANSPORCIE także CI, PL i BL; draft SAD od DRAFT_WYSLANY. Profil dostawcy może zawęzić zestaw. | `document_tiles.py:35-63` | `test_document_tiles.py` |
| W-12 | Dokument z numerem innego kontenera nie trafia do złego kontenera. | Gdy użytkownik wgra PDF, w którym jest poprawny numer innego kontenera, wtedy plik jest odrzucony (409). Uszkodzony PDF — 422. Skan bez tekstu — przyjęty z ostrzeżeniem. | `document_gate.py:19-60` | `test_document_gate.py` |
| W-13 | Wgranie SAD przesuwa odprawę do przodu. | Gdy uprawniona rola wgra dokument SAD-PZ, wtedy odprawa ma ODPRAWIONY; SAD-PW → ZWOLNIONY. Plik od spedytora nie zmienia statusu. | `document_tiles.py:184-193`, `forwarding_files.py:216-222` | `test_document_tiles.py` |

## Plan dostawy i awizacja

| ID | Wymaganie | Kryterium akceptacji | Gdzie zrealizowane | Test |
|---|---|---|---|---|
| W-14 | System proponuje datę dostawy. | Gdy logistyk zakłada kontener z ETA i bez daty awizacji, wtedy data dostawy = ETA + 4 dni w stanie PROPOZYCJA. | `planning.py:17-23` | `test_planning.py` |
| W-15 | Uzgodniona data nie zmienia się sama. | Dany plan WYSLANE lub POTWIERDZONE, gdy zmieni się ETA, wtedy data dostawy zostaje. Gdy człowiek zmieni datę ręcznie, plan wraca do PROPOZYCJA. | `planning.py:51-135`, `containers_write.py:144-148` | `test_planning_confirm.py` |
| W-16 | Limit dzienny magazynu ostrzega, ale nie blokuje. | Dany magazyn z limitem 7 i 7 potwierdzonymi dostawami, gdy logistyk potwierdzi ósmą, wtedy zapis przechodzi, a audyt notuje przekroczenie limitu. Tranzyty i propozycje nie liczą się do limitu. | `planning.py:92-115`, `containers_common.py:410-428` | `test_api.py::test_queue_limits_and_free_days` |
| W-17 | Kalendarz zna dni wolne kraju magazynu. | Dany magazyn w PT, wtedy weekendy i święta portugalskie są dniami wolnymi; magazyn może mieć własne wyjątki. | `holidays.py:21-46` | `test_holidays_snapshot.py` |
| W-18 | Sloty rozładunku mają pojemność. | Dany magazyn z oknem 08:00 i pojemnością 1, gdy dwie odpowiedzi chcą tego samego okna, wtedy druga dostaje „slot zajęty”. | `slots.py:14-51` | `test_avizo_slots.py` |
| W-19 | Awizacja idzie przez jednorazowe linki, bez konta spedytora. | Link etapu 1 jest ważny 7 dni, etapu 2 — 5 dni; po użyciu daje 409, po wygaśnięciu 410. W bazie jest tylko skrót SHA-256 linku. | `avizo_workflow.py:84-175`, `config.py:230-231` | `test_avizo_tokens.py` |
| W-20 | Odpowiedź spedytora zmienia plan dopiero po decyzji logistyki. | Gdy logistyk zatwierdzi odpowiedź, wtedy terminy i sloty są zastosowane i wychodzi jeden mail etapu 2. Gdy odrzuci z komentarzem, wtedy spedytor dostaje nowy link etapu 1. | `avizo_workflow.py:287-340` | `test_avizo_workflow.py` |
| W-21 | Publiczny formularz jest chroniony przed nadużyciem. | Gdy z jednego adresu IP przyjdzie ponad 30 żądań na minutę, wtedy kolejne dostają 429; żądanie z obcego `Origin` jest odrzucane. | `routers/avizo.py:44-70` | `test_avizo_public.py` |

## Separacja danych

| ID | Wymaganie | Kryterium akceptacji | Gdzie zrealizowane | Test |
|---|---|---|---|---|
| W-22 | Spółka widzi tylko swoje kontenery. | Gdy logistyk spółki A otworzy kontener spółki B, wtedy dostaje 404 (jak dla nieistniejącego rekordu). Konto z widokiem wszystkich spółek widzi wszystko. | `deps.py:35-81`, `deps.py:363-468` | `test_isolation.py`, `test_idor_containers.py` |
| W-23 | Partner widzi tylko kontenery, które mu zlecono. | Spedytor widzi kontenery przypisane do swojej firmy, agencja — kontenery, których odprawę jej zlecono; konto magazynu bez przypisanego magazynu nie widzi nic. | `deps.py:60-142` | `test_partner_company_scope.py`, `test_deps_container_access.py` |
| W-24 | Role widzą tylko potrzebne pola. | Spedytor nie widzi danych odprawy; magazyn i agencja nie widzą danych handlowych; po ukrytym polu nie da się wyszukiwać. | `containers_common.py:128-195` | `test_forwarder_no_customs.py` |

## Import z Excela i dane osobowe

| ID | Wymaganie | Kryterium akceptacji | Gdzie zrealizowane | Test |
|---|---|---|---|---|
| W-25 | Import z Excela nie cofa danych z aplikacji. | Dany kontener ODPRAWA w aplikacji, gdy arkusz ma dla niego wcześniejszy etap, wtedy status zostaje. | `importers/queue.py:172-184` | `test_sync_status_forward_only.py` |
| W-26 | Konflikt Excel kontra aplikacja rozstrzyga nowsza zmiana. | Gdy to samo pole zmieniono w arkuszu i w aplikacji, wtedy zostaje zmiana nowsza (czas pliku kontra czas wpisu w historii). | `importers/queue.py:374-421` | `test_sync_keeps_app_changes.py` |
| W-27 | Dane kierowców są usuwane po zakończeniu. | 90 dni po zamknięciu awizacji dane kierowcy (także kopie w powiadomieniach i SMS) są anonimizowane, a fakt trafia do audytu. | `avizo_workflow.py:402-441` | `test_gdpr_driver_copies.py` |
| W-28 | Alert przed końcem czasu wolnego w porcie. | Gdy do końca dni wolnych demurrage zostają ≤ 3 dni, wtedy obserwatorzy kontenera dostają alert raz dziennie; po rozładunku alert ustaje. | `notification_alerts.py:65-133` | `test_demurrage_batch.py` |

## Wymagania z wywiadu, których kod nie realizuje wprost

| Wymaganie ze specyfikacji | Stan w kodzie |
|---|---|
| „Awizacja na datę, bez slotów godzinowych” (`SPECYFIKACJA.md` §3) | kod ma sloty z pojemnością (W-18) — specyfikacja jest nieaktualna |
| „Pola obowiązkowe konfigurowane per spółka (do doprecyzowania)” (§2) | brak takiej konfiguracji; wymagany jest tylko numer kontenera |
