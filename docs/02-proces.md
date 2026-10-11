# 02. Proces biznesowy

Proces odtworzony z kodu (stan: commit `9dd73a1`). Każda reguła ma wskazane miejsce w kodzie.
Ścieżki `backend/app/...` skrócone do nazwy pliku tam, gdzie to jednoznaczne.

## Aktorzy

| Aktor | Rola | Kluczowe akcje w procesie |
|---|---|---|
| Logistyka | `logistics` | zakłada kontenery i zamówienia, zmienia statusy, zleca odprawę, planuje datę dostawy, wysyła i zatwierdza awizację, ustawia ZREALIZOWANY |
| Agencja celna | `customs` | prowadzi odprawę i zmienia jej status; REWIZJA tylko z notatką |
| Spedytor | `forwarder` lub link z e-maila | potwierdza termin dostawy, podaje dane kierowców, realizuje zlecenie transportowe |
| Magazyn | `warehouse` | przyjmuje auto na bramie, rozładowuje, ustawia **wyłącznie** DOSTARCZONY |
| Zakupy | `purchasing` | wgrywa dokumenty, prowadzi status zakupowy |
| System | automaty | wylicza status kontenera z odprawy, wysyła alerty, wygasza linki, anonimizuje dane kierowców |

Spedytor nie musi mieć konta: awizacja działa też przez jednorazowe linki w e-mailu
(`avizo_workflow.py:84-175`). Szczegóły w [06-decyzje.md](06-decyzje.md), D3.

## Proces PRZED aplikacją

Odtworzony z importera arkusza i dokumentów projektu, nie z rozmowy z użytkownikami.
Dowody: kolumny arkusza w `importers/queue.py:41-61`, plik na SharePoincie (`config.py:223`),
drafty SAD z poczty (`tools/outlook-sad/Zbierz-SAD.ps1`), `docs/superpowers/specs/2026-08-31-excel-sharepoint-sync-design.md`.

```mermaid
flowchart TD
    subgraph LOG["Logistyka"]
        A1["Wpis kontenera do arkusza<br/>KOLEJKA KONTENERÓW"]
        A2["Ręczne śledzenie ETA<br/>i zmiana dat w arkuszu"]
        A3["Mail do agencji celnej<br/>z dokumentami"]
        A4["Mail lub telefon do spedytora<br/>w sprawie terminu"]
        A5["Rozesłanie nowej wersji arkusza"]
    end
    subgraph AG["Agencja celna"]
        B1["Draft SAD w załączniku maila"]
    end
    subgraph SP["Spedytor"]
        C1["Odpowiedź z terminem<br/>i danymi kierowcy"]
    end
    subgraph MAG["Magazyn"]
        D1["Własna kopia arkusza"]
        D2["Rozładunek"]
    end
    A1 --> A2 --> A3 --> B1 --> A4 --> C1 --> A5 --> D1 --> D2
    D2 -.->|"informacja zwrotna mailem"| A2
```

Problemy tego układu opisuje [01-problem-i-zakres.md](01-problem-i-zakres.md).
Skala: ok. 200 kontenerów miesięcznie, arkusz prowadziły 4 osoby w logistyce, łącznie ok. 30 godzin
tygodniowo na utrzymanie arkusza i uzgadnianie wersji.

## Proces PO wdrożeniu

```mermaid
flowchart TD
    subgraph SRC["Źródła danych"]
        X1["Arkusz kolejki xlsx<br/>import lub SharePoint"]
        X2["Arkusz ETD / eksport SAP"]
    end

    subgraph LOG["Logistyka"]
        L1["Zamówienie transportowe<br/>N kontenerów ZAPOWIEDZIANY"]
        L5["Statusy ręczne:<br/>W_PRODUKCJI, TRANSPORT_WSTEPNY,<br/>W_TRANSPORCIE, W_PORCIE"]
        L6["Zlecenie odprawy agencji<br/>odprawa ZLECONA"]
        L7["Plan: data = ETA + 4 dni<br/>PROPOZYCJA"]
        L8["Awizacja etap 1<br/>link lub aplikacja"]
        L9{"Zatwierdzić odpowiedź<br/>spedytora?"}
        L10["Ustaw W_DOSTAWIE<br/>ręcznie"]
        L11["Zamknięcie formalności<br/>ZREALIZOWANY = archiwum"]
    end

    subgraph SPED["Spedytor"]
        F3["Etap 1: termin, slot<br/>lub problem"]
        F4["Etap 2: dane kierowców"]
    end

    subgraph AG["Agencja celna"]
        A1["Draft SAD"]
        A2{"Rewizja?"}
        A3["REWIZJA z notatką"]
        A4["ODPRAWIONY lub ZWOLNIONY"]
    end

    subgraph SYS["Automaty systemu"]
        S1["Status kontenera = ODPRAWA"]
        S2{"Odprawiony i jest<br/>data awizacji?"}
        S3["Status kontenera = AWIZOWANY"]
        S4["SMS do kierowcy"]
        S5["Alerty: ETA, demurrage,<br/>odprawa, braki dokumentów"]
    end

    subgraph MAG["Magazyn"]
        M1["Brama: check-in<br/>rampa PODSTAWIONY"]
        M2["Rozładunek start/stop"]
        M3{"Kontener awizowany<br/>lub w dostawie?"}
        M4["Notatka wymagana"]
        M5["DOSTARCZONY"]
    end

    X2 --> L1
    X1 -->|"status tylko w przód"| L5
    L1 --> L5
    L5 --> L6 --> A1 --> S1
    A1 --> A2
    A2 -->|"tak"| A3 --> A4
    A2 -->|"nie"| A4
    A4 --> S2
    L5 --> L7 --> L8 --> F3 --> L9
    L9 -->|"odrzuć z komentarzem"| L8
    L9 -->|"zatwierdź: dzień + slot"| F4
    S2 -->|"tak"| S3
    S2 -->|"nie: czeka na datę"| L7
    F4 --> S4
    S3 --> L10 --> M1 --> M2 --> M3
    M3 -->|"tak"| M5
    M3 -->|"nie"| M4 --> M5
    M5 --> L11
    S5 -.-> LOG
```

Kolejność AWIZOWANY → W_DOSTAWIE → DOSTARCZONY nie jest wymuszona: logistyka może przeskoczyć
etapy w przód, a magazyn może potwierdzić DOSTARCZONY z każdego statusu (wtedy z notatką).

## Cykl życia kontenera

Kolejność wartości w kodzie = kolejność procesu (`models/enums.py:86-97`).

```mermaid
stateDiagram-v2
    [*] --> ZAPOWIEDZIANY
    ZAPOWIEDZIANY --> W_PRODUKCJI: ręcznie
    W_PRODUKCJI --> TRANSPORT_WSTEPNY: ręcznie
    TRANSPORT_WSTEPNY --> W_TRANSPORCIE: ręcznie lub Excel gdy jest ETA
    W_TRANSPORCIE --> W_PORCIE: ręcznie lub Excel gdy ETA minęła
    W_PORCIE --> ODPRAWA: automat gdy odprawa w toku
    ODPRAWA --> AWIZOWANY: automat gdy odprawiony i jest data awizacji
    AWIZOWANY --> W_DOSTAWIE: tylko ręcznie
    W_DOSTAWIE --> DOSTARCZONY: magazyn lub logistyka
    DOSTARCZONY --> ZREALIZOWANY: tylko logistyka lub admin
    ZREALIZOWANY --> [*]
```

Reguły przejść (`routers/containers_common.py:333-343`):

- do przodu — dowolnie, także o kilka etapów;
- wstecz o 1 krok — tylko z notatką;
- wstecz o więcej niż 1 krok — tylko administrator, też z notatką;
- magazyn może ustawić wyłącznie DOSTARCZONY (`routers/containers_write.py:216-218`).

Dwa pojęcia „zakończenia” (`models/container.py:251-273`): **DOSTARCZONY** = fizycznie
rozładowany (koniec demurrage, limitów, SMS), ale nadal w kolejce do rozliczenia;
**ZREALIZOWANY** = archiwum.

## Tory równoległe

Kontener ma obok statusu głównego kilka niezależnych statusów.

| Tor | Wartości | Reguły | Kod |
|---|---|---|---|
| Odprawa celna | BRAK → DOKUMENTY_KOMPLETNE → ZLECONA → DRAFT_WYSLANY → DRAFT_POTWIERDZONY → ODPRAWIONY → ZWOLNIONY → ROZLICZONY, oraz REWIZJA | zmienia agencja (logistyka awaryjnie, spedytor nigdy); REWIZJA i cofnięcie z ODPRAWIONY tylko z notatką; kolejność **nie** jest wymuszona | `containers_common.py:347-369` |
| Dokumenty | BRAK → ZALACZONE → WYSLANE | pierwszy dokument z typem → ZALACZONE; wysyłka do agencji → WYSLANE | `forwarding_files.py:210-213`, `customs.py:381-430` |
| Plan dostawy | PROPOZYCJA → WYSLANE → POTWIERDZONE | wysłanie planu zamraża datę; zmiana daty po uzgodnieniu cofa do PROPOZYCJA | `planning.py:51-135` |
| Awizacja | DRAFT → SENT_STAGE1 → CONFIRMED_BY_FORWARDER → APPROVED_BY_US → SENT_STAGE2 → DRIVERS_SUBMITTED → CLOSED, oraz REJECTED, EXPIRED, CANCELLED | jedna maszyna stanów, przejście warunkowe chroni przed podwójnym kliknięciem | `avizo_workflow.py:40-81` |
| Rampa | PODSTAWIONY, ROZLADOWANY, PRZYJETY | check-in na bramie ustawia PODSTAWIONY; nie zmienia statusu kontenera | `warehouse_ops.py:104-189` |

## Punkty decyzyjne

| Decyzja | Warunek | Skutek | Kod |
|---|---|---|---|
| Status kontenera z odprawy | odprawa w toku / odprawiony + data awizacji | ODPRAWA / AWIZOWANY (tylko w przód) | `containers_common.py:443-458` |
| Rewizja celna | status REWIZJA | notatka obowiązkowa | `containers_common.py:360-362` |
| Wysłać dokumenty agencji mimo braków? | brak typów z checklisty | blokada 409, chyba że użytkownik potwierdzi „mimo braków” (zapis w audycie) | `customs.py:409-416` |
| Zatwierdzić awizację etap 1? | wszystkie kontenery „problem” → 409; slot zajęty → 409 | zatwierdzenie wysyła etap 2, odrzucenie wysyła nowy link etapu 1 | `avizo_workflow.py:287-340` |
| Przekroczony limit dzienny magazynu? | liczba potwierdzonych dostaw > limit | ostrzeżenie i wpis w audycie, bez blokady | `planning.py:92-115` |
| Data zmieniona po uzgodnieniu? | plan ≠ PROPOZYCJA | plan wraca do PROPOZYCJA | `containers_write.py:144-148` |
| Rozładunek bez awizacji? | magazyn, status poza AWIZOWANY / W_DOSTAWIE / DOSTARCZONY | notatka obowiązkowa | `containers_write.py:223-226` |
| Cofnięcie statusu | wstecz 1 krok / więcej | notatka / tylko admin | `containers_common.py:333-343` |
| Kontener tranzytowy? | numer zamówienia zaczyna się od „47” | flaga tranzytu, poza limitem dziennym, automatyczny szkic wyceny | `quotes_core.py:50-74` |
| Excel kontra aplikacja | to samo pole zmienione w obu miejscach | wygrywa nowsza zmiana; status i odprawa tylko w przód | `importers/queue.py:374-421` |
