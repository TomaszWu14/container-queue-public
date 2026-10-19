# Decyzje do podjęcia przez PO

Jedna lista wszystkiego, co czeka na „tak / nie” Product Ownera. Szczegóły i uzasadnienia: kolumna „Gdzie”.
Pełny rejestr założeń (38 pozycji „do potwierdzenia”): [`ZALOZENIA.md`](ZALOZENIA.md).
Pełny rejestr założeń (38 pozycji „do potwierdzenia”): [`ZALOZENIA.md`](ZALOZENIA.md).
Pełny rejestr założeń (38 pozycji „do potwierdzenia”): [`ZALOZENIA.md`](ZALOZENIA.md).

Jak odpowiedzieć: wystarczy numer i decyzja, np. „Z-027 tak, ADR-0004 nie”. [BA] przepisze odpowiedź do
rejestru (status „potwierdzone” / „odrzucone” z datą) i zaktualizuje dokumenty, które się na nią powołują.

## Architektura (ADR) — zmieniają zakres systemu

| Nr | Propozycja | Rekomendacja zespołu | Skutek „nie” | Gdzie |
|---|---|---|---|---|
| ADR-0004 | Publiczne API **tylko do odczytu** z kluczem per spółka (`/api/v1/public/…`), klucz odwoływany jednym klikiem | **tak** — odblokowuje automatyczne odświeżanie Power BI / Excel / Power Automate bez ręcznego eksportu | zostaje eksport ręczny (`docs/MICROSOFT-365.md`) | [ADR-0004](../architektura/adr/0004-publiczne-api-z-kluczami-per-firma.md) |
| ADR-0005 | Własna kopia demo dla każdego odwiedzającego (może zapisywać, kasowana po czasie) | **później** — dziś „Symuluj dzień” pokazuje automaty bez zapisu | demo zostaje tylko do odczytu | [ADR-0005](../architektura/adr/0005-wlasna-kopia-demo-dla-goscia.md) |
| ADR-0006 | Izolacja spółek w kodzie (`deps.py`) + strażnik tras w testach, bez RLS w bazie | **tak** — już działa i jest pilnowane testem | trzeba zaplanować RLS w PostgreSQL | [ADR-0006](../architektura/adr/0006-izolacja-spolek-w-kodzie-i-strazniku.md) |

## Automatyzacje — założenia z ostatnich zmian

| Nr | Założenie (dziś działa tak) | Rekomendacja | Alternatywa | Gdzie |
|---|---|---|---|---|
| Z-023 | Ekran Automatyzacje widzą admin i logistyka | tak | także agencja / spedytor (tylko swoje obiegi) | [ZALOZENIA](ZALOZENIA.md) |
| Z-024 | Minuty pracy ręcznej na efekt automatu (np. faktura 15, alert 5) | **podać własne wartości** — to najsłabszy punkt licznika oszczędności | zostają wartości zespołu | ekran Automatyzacje → „Założenia minut” |
| Z-025 | Mierniki „przed” jako założenia, oznaczone wprost | tak, do czasu danych PO | dane z okresu przed aplikacją | [MIERNIKI-PRZED-PO](../dla-rekrutera/MIERNIKI-PRZED-PO.md) |
| Z-026 | Kreator reguł: 4 warunki, sprawdzanie co godzinę, zmienia tylko admin | tak | więcej warunków / zmiany także przez logistykę | [ZALOZENIA](ZALOZENIA.md) |
| Z-027 | „Dłużej niż zwykle” = powyżej 90. percentyla etapu z 90 dni, dni kalendarzowe; kontenery po dostawie na magazyn pomijane | tak | mediana × 2, dni robocze | panel „Przebieg procesu” |
| Z-028 | Asystent bez modelu AI odpowiada z szablonu po polsku, także po awarii modelu | tak | szablon tylko w demo, wersje EN/PT | [ZALOZENIA](ZALOZENIA.md) |
| Z-030 | Automat włącza / wyłącza tylko admin; RODO, retencja, pliki, kopia i strażnik chronione | tak | także logistyka | [ZALOZENIA](ZALOZENIA.md) |
| Z-031 | „Co jeśli statek się spóźni” liczy tylko w pamięci (1–21 dni), plan zostaje bez zmian | tak | przycisk „zapisz nowy plan” | [ZALOZENIA](ZALOZENIA.md) |
| Z-032 | Reguła wybiera kanały (dzwonek / e-mail / Teams / n8n), domyślnie wszystkie; Teams to jeden wspólny kanał | tak | osobny kanał Teams na regułę | [ZALOZENIA](ZALOZENIA.md) |
| Z-033 | Przy awarii NBP kursy najwyżej 5-dniowe, starsze = bez przeliczenia | tak | inny limit | [ZALOZENIA](ZALOZENIA.md) |
| Z-034 | „Nie przypominaj”: 1 / 3 / 7 dni, tylko dla siebie, wzmianki przechodzą | tak | inne okresy | [ZALOZENIA](ZALOZENIA.md) |
| Z-035 | Koszt w „co jeśli”: 150 EUR/dzień za kontener ponad limit magazynu | **podać stawkę** | stawki per armator | [ZALOZENIA](ZALOZENIA.md) |
| Z-036 | Ponawianie wysyłek 1/5/30 min, kolejka w pamięci (restart gubi oczekujące) | tak | trwała kolejka w bazie (migracja) | [ZALOZENIA](ZALOZENIA.md) |
| Z-037 | Test reguły: przybliżenie (etap z historii, daty dzisiejsze), próg „dużo” = 10 dziennie | tak | inny próg | [ZALOZENIA](ZALOZENIA.md) |
| Z-038 | Realne ETA = ETA + mediana spóźnienia armatora (min. 3 przypłynięcia), tylko podpowiedź | tak | automatyczna zmiana planu | [ZALOZENIA](ZALOZENIA.md) |
| Z-039 | Raport miesięczny: zestaw liczb za ostatnie 30 dni, PDF przez przeglądarkę | **podać, co ma być w raporcie** | miesiąc kalendarzowy, wysyłka e-mailem | [ZALOZENIA](ZALOZENIA.md) |
| Z-029 | „Symuluj dzień” nic nie zapisuje — pokazuje kroki w oknie | tak (bezpieczniej dla demo) | zapis w „piaskownicy” demo (ADR-0005) | [ZALOZENIA](ZALOZENIA.md) |

## Proces i bezpieczeństwo — starsze, wciąż otwarte

| Nr | Założenie | Dlaczego ważne | Gdzie |
|---|---|---|---|
| Z-007 | Fail-fast produkcji dla `DATABASE_URL` i `DATA_ENCRYPTION_KEY` — merge po potwierdzeniu zmiennych w Coolify | bez tego zła konfiguracja uruchamia się po cichu | [ZALOZENIA](ZALOZENIA.md), US-001/US-002 |
| Z-008 | 2FA administratorów nieobowiązkowe | ryzyko przejęcia konta admina | [RYZYKA](../bezpieczenstwo/RYZYKA.md) |
| Z-009 | Administrator danych osobowych i kontakt RODO nieznani | wymagane przez RODO | [RODO](../bezpieczenstwo/RODO.md) |
| Z-010 | Demo publiczne, nigdy z danymi rzeczywistymi | podstawa bezpieczeństwa portfolio | [ZALOZENIA](ZALOZENIA.md) |
