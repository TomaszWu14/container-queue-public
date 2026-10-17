# Założenia przyjęte bez decyzji PO

Rejestr założeń [BA]. Każde założenie przyjęto, bo Product Owner nie odpowiedział na pytanie z serii 1
(`docs/AUDYT.md` §7) i polecił kontynuować. Założenie obowiązuje do czasu potwierdzenia albo odrzucenia
przez PO; odrzucone założenie = zmiana w dokumentach, które się na nie powołują (kolumna „Dotyka”).

Statusy: **do potwierdzenia** · potwierdzone (data) · odrzucone (data, co w zamian).

| ID | Założenie | Pytanie | Status | Skutek, jeśli błędne | Dotyka |
|---|---|---|---|---|---|
| Z-001 | Cel na najbliższe tygodnie: proces i dokumentacja w tym repozytorium; żadnych zmian na produkcji bez osobnej decyzji PO. | 1 | do potwierdzenia | priorytety backlogu do przestawienia na poprawki produktu | `HISTORYJKI.md` |
| Z-002 | Źródłem prawdy dla procesu jest to repozytorium (`container-queue-public`). Kod produkcyjny może pochodzić z repozytorium prywatnego — gdzie scalić poprawki kodu, decyduje PO przy pierwszej historyjce z kodem. | 1 | do potwierdzenia | PR-y z kodem trzeba będzie przenieść | `CONTRIBUTING.md`, `SLEDZENIE.md` |
| Z-003 | W fazie testów z aplikacji korzysta ok. 4 osób logistyki i 1 magazyn; partnerzy zewnętrzni (spedytorzy, agencja) jeszcze nie. Głosem użytkownika dla BA jest PO. | 2 | do potwierdzenia | inne priorytety UX (np. formularze spedytora) | `WIZJA.md`, `INTERESARIUSZE.md` |
| Z-004 | Mierniki sukcesu nie są dziś mierzone; definicje w `WIZJA.md` są propozycją. | 2 | do potwierdzenia | cele liczbowe do zmiany | `WIZJA.md`, US-014 |
| Z-005 | Rdzeń procesu i powiadomienia = *Must*. Moduły poboczne (faktury/SAD, reklamacje, wyceny, palety, śledzenie, analityka, baza wiedzy, asystent) = *Could*: bez nowych prac i bez spisywania dla nich wymagań, dopóki PO nie zdecyduje inaczej. | 3 | do potwierdzenia | wymagania FR-1xx do napisania, backlog do rozszerzenia | `WYMAGANIA.md`, `HISTORYJKI.md` |
| Z-006 | Kolejność bólu użytkowników przyjęta z audytu: P-01 (fałszywy sukces awizacji), B-004 (ciche nadpisanie), P-05/P-06 (Portugalia), P-09 (plan bez maila). | 3 | do potwierdzenia | inna kolejność w backlogu | `HISTORYJKI.md` |
| Z-007 | Fail-fast na produkcji dla `DATABASE_URL` i `DATA_ENCRYPTION_KEY` trafia do backlogu jako *Must*, ale **merge dopiero po potwierdzeniu PO, że zmienne są ustawione w Coolify** (inaczej następny redeploy zatrzyma aplikację). | 4a | do potwierdzenia | historyjki US-001/US-002 czekają | `HISTORYJKI.md`, `RYZYKA.md` |
| Z-008 | 2FA administratorów zostaje nieobowiązkowe (decyzja właściciela 2026-09-29). Zalecenie `REQUIRE_2FA_ADMIN=true` na produkcji pozostaje w rejestrze ryzyk jako wyjątek z datą przeglądu. | 4b | do potwierdzenia | US-019 wchodzi do *Should* | `RYZYKA.md` (E-01) |
| Z-009 | Administrator danych osobowych i osoba kontaktowa RODO nie są znani; `RODO.md` ma pola „do potwierdzenia”, podstawy prawne są propozycją do weryfikacji prawnej. | 4c | do potwierdzenia | `RODO.md` do uzupełnienia | `../bezpieczenstwo/RODO.md` |
| Z-010 | Instancja demo zostaje publiczna i **nigdy** nie dostaje danych rzeczywistych. | 4d | do potwierdzenia | demo do wyłączenia lub ukrycia za hasłem | `RYZYKA.md` (E-05) |
| Z-011 | Język: dokumentacja po polsku; kod, nazwy, commity po angielsku (Conventional Commits). Dotychczasowe polskie opisy commitów zostają w historii. | 5a | do potwierdzenia | zmiana konwencji w `CONTRIBUTING.md` | `../../CONTRIBUTING.md` |
| Z-012 | Nowa struktura `docs/analiza`, `architektura`, `bezpieczenstwo`, `testy`, `operacje` powstaje jako **cienkie indeksy** linkujące do istniejących `01–07` i dokumentów technicznych; nic nie jest przenoszone ani kasowane. | 5b | do potwierdzenia | przeniesienie plików i aktualizacja linków | ADR-0001 |
| Z-013 | Próg pokrycia backendu zostaje 92 % linii; frontend bez progu liczbowego (każde kryterium akceptacji ma test). | 5c | do potwierdzenia | zmiana `pyproject.toml` / CI frontendu | `../testy/STRATEGIA_TESTOW.md` |
| Z-014 | Merge wyłącznie po akceptacji PO. PR-y powstają jako draft i tak zostają do akceptacji; auto-merge po „CI OK” nie obowiązuje w tym repozytorium. | 5d | do potwierdzenia | powrót do auto-merge | `../../CONTRIBUTING.md` |
| Z-015 | Nazwy gałęzi funkcji: `feature/<US-id>-<krótka-nazwa>` (np. `feature/US-001-prod-requires-postgres`). Sesje Claude w chmurze pracują na gałęziach wyznaczonych przez narzędzie (`claude/...`), jak w `CLAUDE.md`. | — | do potwierdzenia | zmiana nazw gałęzi | `../../CONTRIBUTING.md` |
| Z-016 | Zmiany w workflowach CI (bramka Trivy, Semgrep, wyrównanie wersji) idą osobną historyjką (US-007), nie w PR dokumentacyjnym. Wyjątek: `.github/dependabot.yml` — konfiguracja bez wpływu na przebieg CI, deklarowana wcześniej w `SECURITY.md`. | — | do potwierdzenia | przeniesienie `dependabot.yml` do US-007 | `../../.github/dependabot.yml` |
| Z-017 | Poziom OWASP ASVS: **L2** (aplikacja przetwarza dane osobowe osób trzecich i dane handlowe kilku firm). | — | do potwierdzenia | checklista do przeskalowania na L1/L3 | `../bezpieczenstwo/CHECKLISTA_ASVS.md` |
| Z-018 | Pole „pola obowiązkowe konfigurowane per spółka” z wywiadu (`SPECYFIKACJA.md` §2) nie jest realizowane, dopóki PO nie potwierdzi potrzeby. | — | do potwierdzenia | nowa historyjka | `WYMAGANIA.md` (otwarte) |
| Z-020 | Panel „Ile to oszczędza”: jedna zmiana zapisana w aplikacji (status, dokument, odprawa, plan…) oszczędza **3 minuty** w porównaniu z wpisem w Excelu i mailem do zainteresowanych. Wartość pokazana na ekranie jako założenie. | — | do potwierdzenia | inna liczba minut (stała `MINUTES_PER_CHANGE`) | `backend/app/routers/stats_value.py` |
| Z-019 | Specyfikacja wysyłki dokumentów do agencji opisuje stan obecny; luki L-1…L-8 nie są naprawiane, dopóki PO nie odpowie na pytania §11. | — | do potwierdzenia | historyjki z luk L-1…L-8 | `spec/WYSYLKA-DOKUMENTOW-DO-AGENCJI.md` |
| Z-021 | Skaner na bramie (US-030) wpuszcza tylko auta z **dzisiejszej** listy bramy; kontener spoza niej dostaje ostrzeżenie zamiast przycisku. Odczyt kodu w aplikacji działa w Chrome na Androidzie; na iPhonie ochrona skanuje zwykłym aparatem (otwiera kartę kontenera) albo wpisuje numer. | — | do potwierdzenia | wpuszczanie aut spoza listy / osobna biblioteka do odczytu kodów na iPhonie | `frontend/src/pages/gate/` |
| Z-022 | Kraj numeru kierowcy bez kierunkowego = kraj magazynu rozładunku (PL +48, PT +351); magazyn tworzony z kolejki dziedziczy kraj, gdy wszystkie magazyny spółki są w jednym kraju, inaczej PL. | — | do potwierdzenia | wybór kraju przy numerze w formularzu kierowcy | `backend/app/phones.py` |
| Z-023 | Ekran „Automatyzacje” (US-032) widzą **admin i logistyka** (konto demo to logistyka); partnerzy (spedytor, agencja, magazyn) go nie widzą. Liczniki z ostatnich **7 dni**. | — | do potwierdzenia | inne role / inne okno | `backend/app/automation_catalog.py` |
| Z-024 | Licznik oszczędności per automat (US-034): minuty pracy ręcznej na jeden efekt automatu — wartości startowe do podania przez PO, do tego czasu jawne założenia ustawiane w panelu admina. | — | do potwierdzenia | wartości PO | US-034 |
| Z-025 | Mierniki „przed wdrożeniem” (US-050): bez danych PO pokazujemy je jako założenia, oznaczone wprost na ekranie i w dokumentach. | — | do potwierdzenia | dane PO z okresu przed aplikacją | US-050 |

## Jak potwierdzić

PO odpowiada w PR, w issue albo w rozmowie; BA wpisuje datę i status, a przy odrzuceniu — co obowiązuje
zamiast założenia. Założenia potwierdzone zostają w tabeli (ślad decyzji).
