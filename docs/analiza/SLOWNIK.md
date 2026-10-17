# Słownik pojęć

Wersja 0.1 (2026-10-16), [BA]. Jedno miejsce na pojęcia procesu i systemu; przy wątpliwości obowiązuje
definicja z tego pliku. Nazwy w kodzie i tłumaczeniach UI (`frontend/src/i18n/`) mają być z nim zgodne.

| Pojęcie | Definicja | W kodzie / dokumencie |
|---|---|---|
| **Kolejka (kontenerów)** | lista dostaw kontenerowych pogrupowana datami awizacji; zastąpiła arkusz `KOLEJKA KONTENERÓW` | `routers/containers.py`, ekran `/kolejka` |
| **Kontener** | jedna dostawa fizycznego kontenera; powtórny przyjazd tego samego numeru to nowy rekord (D7) | `models/container.py` |
| **Numer kontenera** | 4 litery + 6 cyfr + cyfra kontrolna wg ISO 6346; walidacja blokująca | `iso6346.py`, FR-001 |
| **Status kontenera** | etap z 10: ZAPOWIEDZIANY → W_PRODUKCJI → TRANSPORT_WSTEPNY → W_TRANSPORCIE → W_PORCIE → ODPRAWA → AWIZOWANY → W_DOSTAWIE → DOSTARCZONY → ZREALIZOWANY | `ContainerStatus` |
| **Status odprawy** | osobne pole: BRAK → DOKUMENTY_KOMPLETNE → ZLECONA → DRAFT_WYSLANY → DRAFT_POTWIERDZONY → ODPRAWIONY → ZWOLNIONY → ROZLICZONY, oraz REWIZJA | `CustomsStatus` |
| **Otwarty w kolejce** | kontener w każdym statusie poza ZREALIZOWANY (DOSTARCZONY czeka na rozliczenie) | `Container.open_in_queue()` (BIZ-004) |
| **Fizycznie zakończony** | DOSTARCZONY albo ZREALIZOWANY — nie liczy się do limitów, demurrage, SMS | `Container.FINISHED` |
| **Spółka** | firma z grupy, właściciel kontenerów; oś separacji danych | `Company`, `company_id` |
| **Separacja danych** | reguła: spółka widzi swoje kontenery, partner tylko zlecone mu; obcy rekord = 404 | `deps.py` (D9), FR-022…FR-024 |
| **Partner** | firma zewnętrzna bez spółki: spedytor albo agencja celna | `PARTNER_ROLES` |
| **Spedytor (forwarder)** | organizuje transport i awizację; może działać bez konta przez link | rola `forwarder` |
| **Agencja celna (customs)** | prowadzi odprawę; jedyna rola, która zmienia status odprawy (logistyka awaryjnie) | rola `customs` |
| **Magazyn** | miejsce rozładunku; konto magazynu widzi tylko swój magazyn; potwierdza wyłącznie DOSTARCZONY | rola `warehouse`, `Warehouse` |
| **MAG-1** | magazyn zewnętrzny (firma logistyczna) obsługujący wywołania palet | `routers/mag1.py`, `pallets.py` |
| **ETA / ETD** | szacowany czas przybycia / wypłynięcia statku | `Container.eta`, `etd` |
| **Data awizacji (notify_date)** | planowana data dostawy do magazynu; jedno pole ze statusem planu (D1) | `Container.notify_date` |
| **Status planu** | PROPOZYCJA (system) → WYSLANE (do spedytora) → POTWIERDZONE (po uzgodnieniu); ręczna zmiana daty cofa do PROPOZYCJA | `PlanningStatus`, FR-014, FR-015 |
| **Awizacja** | uzgodnienie terminu dostawy ze spedytorem; dwa etapy: 1 — termin, 2 — dane kierowcy | `avizo_workflow.py` |
| **Link awizacji** | jednorazowy, publiczny link dla spedytora bez konta; etap 1 ważny 7 dni, etap 2 — 5 dni; w bazie tylko SHA-256 | FR-019 |
| **Slot** | okno godzinowe rozładunku z pojemnością per magazyn | `slots.py`, FR-018 |
| **Limit dzienny magazynu** | domyślna liczba rozładunków dziennie z nadpisaniem na dzień; przekroczenie = ostrzeżenie (D5) | FR-016 |
| **Dni wolne** | weekendy, święta kraju magazynu (PL/PT) i wyjątki per magazyn | `holidays.py`, FR-017 |
| **Demurrage** | opłata za przetrzymanie kontenera w porcie po dniach wolnych armatora; alert ≤ 3 dni przed końcem | FR-028 |
| **Tranzyt** | kontener nieliczony do limitu magazynu (przejazd przez magazyn) | `Container.is_transit` |
| **Kafelek dokumentu** | wymagany typ dokumentu zależny od etapu (PI, CI, PL, BL, SAD) z profilem dostawcy | `document_tiles.py`, FR-011 |
| **PI / CI / PL / BL** | proforma, faktura handlowa, packing list, konosament (bill of lading) | `DocumentType` |
| **SAD, draft SAD, SAD-PZ, SAD-PW** | zgłoszenie celne; szkic od agencji; dokument po odprawie (PZ) i zwolnieniu (PW) — wgranie przesuwa odprawę (FR-013) | `sad_drafts.py`, `invoices/sad_*` |
| **CMR** | list przewozowy; jedyny typ dokumentu widoczny dla spedytora poza własnymi plikami | `forwarder_may_see` |
| **Bramka zgodności** | odrzucenie PDF z numerem innego kontenera (409) | `document_gate.py`, FR-012 |
| **Poczekalnia dokumentów** | wgranie paczki plików (także z poczty) przed przypisaniem do kontenera | `routers/intake*.py` |
| **Zlecenie transportowe** | obieg zlecenia dla spedytora: WYSTAWIONE → ZAAKCEPTOWANE → W_REALIZACJI → WYKONANE → POTWIERDZONE; bez anulowania | `TransportOrder` |
| **Wycena (RFQ)** | zapytanie o cenę transportu do kilku spedytorów; wybór oferty nie przypisuje spedytora (P-10) | `TransportJob`, `Quote` |
| **Wywołanie palet** | zamówienie dostawy palet z magazynu zewnętrznego na podstawie stanów (Power BI) | `pallets.py`, `PalletCall` |
| **PAZ** | plan/cel zapasu materiałów importowany z pliku | `routers/paz.py` |
| **REF / MARM / EKKO / LFA1** | dane SAP: indeks materiału, jednostki miary, zamówienia zakupu, dostawcy | `importers/`, `invoices/` |
| **Historia zmian (audyt)** | wpis kto/kiedy/było/jest/powód dla każdego pola; dane kierowcy maskowane | `audit.py`, FR-006 |
| **Obserwator** | użytkownik śledzący kontener lub statek; dostaje alerty | `WatchedContainer` |
| **Konto serwisowe (n8n)** | konto, na które podpisują się automatyzacje z tokenem `X-Automation-Token`; nie może być adminem | `automation_policy.py` |
| **Demo** | publiczna instancja z danymi syntetycznymi i kontem tylko do odczytu | `DEMO_READONLY_LOGINS` |
| **Okres przejściowy** | praca równoległa Excel ↔ aplikacja; synchronizacja ręczna, Excel nie cofa stanu (D6) | `SHAREPOINT_AUTO_SYNC` |
| **FR / NFR / SR** | wymaganie funkcjonalne / niefunkcjonalne / bezpieczeństwa | `WYMAGANIA.md` |
| **US** | historyjka użytkownika w backlogu | `HISTORYJKI.md` |
| **R-xx / E-xx** | ryzyko / zaakceptowany wyjątek w rejestrze | `../bezpieczenstwo/RYZYKA.md` |
| **P-xx / T-xx / B-xxx** | znany problem / granica bez walidacji (`07-ograniczenia.md`) / błąd z `BUGS-FOUND.md` | — |
| **D1…D12** | decyzje projektowe rdzenia | `../06-decyzje.md` |
