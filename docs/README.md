# Mapa dokumentacji

## 0. Proces zespołowy (BA / DEV / SEC) — od 2026-10-16

Nowa struktura to **indeksy** do dokumentów niżej plus to, czego dotąd nie było (ADR-0001). Proces i konwencje:
[`../CONTRIBUTING.md`](../CONTRIBUTING.md). Stan wyjściowy: [AUDYT.md](AUDYT.md).

| Katalog | Pliki |
|---|---|
| [analiza/](analiza/) [BA] | [WIZJA](analiza/WIZJA.md), [INTERESARIUSZE](analiza/INTERESARIUSZE.md), [PROCESY](analiza/PROCESY.md), [WYMAGANIA](analiza/WYMAGANIA.md), [HISTORYJKI](analiza/HISTORYJKI.md), [SLOWNIK](analiza/SLOWNIK.md), [ZALOZENIA](analiza/ZALOZENIA.md), [SLEDZENIE](analiza/SLEDZENIE.md), specyfikacje funkcji: [wysyłka dokumentów do agencji](analiza/spec/WYSYLKA-DOKUMENTOW-DO-AGENCJI.md) |
| [architektura/](architektura/) [DEV] | [ARCHITEKTURA](architektura/ARCHITEKTURA.md), [MODEL_DANYCH](architektura/MODEL_DANYCH.md), [API](architektura/API.md), [adr/](architektura/adr/README.md) |
| [bezpieczenstwo/](bezpieczenstwo/) [SEC] | [KLASYFIKACJA_DANYCH](bezpieczenstwo/KLASYFIKACJA_DANYCH.md), [THREAT_MODEL](bezpieczenstwo/THREAT_MODEL.md), [RYZYKA](bezpieczenstwo/RYZYKA.md), [RODO](bezpieczenstwo/RODO.md), [CHECKLISTA_ASVS](bezpieczenstwo/CHECKLISTA_ASVS.md) |
| [testy/](testy/) | [STRATEGIA_TESTOW](testy/STRATEGIA_TESTOW.md), [E2E](testy/E2E.md), [ETAP-0-PLAN](testy/ETAP-0-PLAN.md) |
| [operacje/](operacje/) | [RUNBOOK](operacje/RUNBOOK.md) |

## 1. Dokumentacja analityczna — zacznij tutaj

Stan odtworzony z kodu; przy rozbieżności z innymi plikami ma pierwszeństwo.

| Dokument | Co zawiera |
|---|---|
| [01. Problem i zakres](01-problem-i-zakres.md) | problem, interesariusze, zakres i czego system nie robi |
| [02. Proces](02-proces.md) | proces przed i po, aktorzy, statusy, punkty decyzyjne |
| [03. User flow](03-user-flow.md) | mapa ekranów i przejść |
| [04. Model danych](04-model-danych.md) | ERD, encje, reguły integralności |
| [05. Wymagania](05-wymagania.md) | wymagania z kryteriami akceptacji i testami |
| [06. Decyzje](06-decyzje.md) | dziennik decyzji projektowych |
| [07. Ograniczenia](07-ograniczenia.md) | znane problemy, luki, co dalej |

## 2. Źródła wymagań

| Dokument | Co zawiera |
|---|---|
| [SPECYFIKACJA.md](SPECYFIKACJA.md) | zapis wywiadu projektowego (50 pytań, 02.07.2026), aktualizowany przy zmianach |
| [REGULY-PROCESU.md](REGULY-PROCESU.md) | rejestr reguł procesu z datą decyzji |
| [superpowers/](superpowers/README.md) | robocze specyfikacje i plany funkcji — źródło uzasadnień w 06 |

## 3. Procesy i moduły (opisy szczegółowe, częściowo starsze niż kod)

[mapa-procesu-timporye.md](mapa-procesu-timporye.md),
[mapa-procesow-szczegolowa.md](mapa-procesow-szczegolowa.md),
[workflow-aplikacji-2026-09-16.md](workflow-aplikacji-2026-09-16.md),
[bpmn/](bpmn/timporye-proces.bpmn),
[MODUL_SPEDYCJA_AGENCJA_CELNA.md](MODUL_SPEDYCJA_AGENCJA_CELNA.md),
[REKLAMACJE.md](REKLAMACJE.md),
[SAD-Z-POCZTY.md](SAD-Z-POCZTY.md),
[POCZTA-DO-POCZEKALNI.md](POCZTA-DO-POCZEKALNI.md),
[XML-SADUE-Z-FAKTUR.md](XML-SADUE-Z-FAKTUR.md),
[SHAREPOINT-SYNC.md](SHAREPOINT-SYNC.md),
[AUTOMATYZACJA-IMPORTY.md](AUTOMATYZACJA-IMPORTY.md),
[JAKOSC-DANYCH.md](JAKOSC-DANYCH.md).
Rozbieżności z kodem są wypisane w [07](07-ograniczenia.md#dokumentacja-niezgodna-z-kodem).

## 4. Technika i utrzymanie

[TECHNICZNE.md](TECHNICZNE.md),
[ARCHITEKTURA.md](ARCHITEKTURA.md),
[ONBOARDING-DEV.md](ONBOARDING-DEV.md),
[ZMIENNE-SRODOWISKOWE.md](ZMIENNE-SRODOWISKOWE.md),
[DEPLOY_COOLIFY.md](DEPLOY_COOLIFY.md),
[BACKUPY.md](BACKUPY.md),
[BEZPIECZENSTWO.md](BEZPIECZENSTWO.md),
[JEDNA-INSTANCJA.md](JEDNA-INSTANCJA.md),
[N8N.md](N8N.md),
[CLAUDE-GITHUB.md](CLAUDE-GITHUB.md),
[testy/](testy/E2E.md).

## 5. Audyty i pomysły

[AUDYT.md](AUDYT.md) — audyt repozytorium z trzech perspektyw (BA / DEV / SEC), stan na 2026-10-15,
z listą ryzyk i pytaniami do Product Ownera.

[audyt-nielsen-kolejka.md](audyt-nielsen-kolejka.md),
[audyt-tracking-przeplywy-2026-09-15.md](audyt-tracking-przeplywy-2026-09-15.md),
[PROMPT-AUDYT-UX.md](PROMPT-AUDYT-UX.md),
[pomysly-automatyzacje.md](pomysly-automatyzacje.md),
[pomysly-automatyzacje-2000.md](pomysly-automatyzacje-2000.md).
