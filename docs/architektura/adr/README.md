# Architecture Decision Records

Decyzje istotne albo trudno odwracalne zapisujemy **przed kodem** jako ADR: kontekst, rozważane opcje,
decyzja, konsekwencje, status (proponowana / przyjęta / zastąpiona przez ADR-nnnn). Jeden plik = jedna
decyzja, nazwa `NNNN-krotki-tytul.md`. Decyzje biznesowe (reguły procesu) idą do `docs/REGULY-PROCESU.md`,
nie tutaj; decyzje o akceptacji ryzyka — do `docs/bezpieczenstwo/RYZYKA.md`.

## Decyzje sprzed procesu

D1–D12 w [`../../06-decyzje.md`](../../06-decyzje.md) mają ten sam format (kontekst, opcje, wybór, skutki,
źródło) i pozostają tam (Z-012). Odwołujemy się do nich jako **D1…D12**.

| ID | Decyzja |
|---|---|
| D1 | jedno pole daty dostawy plus status planu |
| D2 | zamrożenie uzgodnionej daty zamiast przeliczania po zmianie ETA |
| D3 | spedytor bez konta — jednorazowe linki |
| D4 | braki dokumentów: ostrzeżenie, nie blokada |
| D5 | limit dzienny magazynu: ostrzeżenie, nie blokada |
| D6 | okres przejściowy z Excelem: aplikacja nie jest cofana przez arkusz |
| D7 | powtórny przyjazd kontenera = nowy rekord |
| D8 | magazyn potwierdza rozładunek, logistyka zamyka dostawę |
| D9 | izolacja danych w jednym miejscu (`deps.py`) |
| D10 | wyłączenie zewnętrznego trackingu kontenerów na obecny etap |
| D11 | usunięcie publicznych linków dla klienta i kierowcy |
| D12 | FastAPI + PostgreSQL + React |

## ADR procesu zespołowego

| ID | Tytuł | Status |
|---|---|---|
| [ADR-0001](0001-indeksy-dokumentacji-zamiast-przenoszenia.md) | Nowa struktura `docs/` jako indeksy do istniejących dokumentów | przyjęta warunkowo (Z-012, do potwierdzenia PO) |
| [ADR-0002](0002-proces-zespolowy-ba-dev-sec.md) | Proces zespołowy BA / DEV / SEC z Product Ownerem | przyjęta |
| [ADR-0003](0003-oczekiwany-status-przy-zmianie-statusu.md) | Oczekiwany status przy przejściach statusu (ochrona przed cichym nadpisaniem) | przyjęta |
| [ADR-0004](0004-publiczne-api-z-kluczami-per-firma.md) | Publiczne API tylko do odczytu z kluczami per firma (pomysł 7) | proponowana — czeka na PO |
| [ADR-0005](0005-wlasna-kopia-demo-dla-goscia.md) | Własna kopia demo dla każdego odwiedzającego (pomysł 9) | proponowana — czeka na PO |
| [ADR-0006](0006-izolacja-spolek-w-kodzie-i-strazniku.md) | Izolacja spółek: kontrola w `deps.py` + strażnik tras, bez RLS | proponowana — czeka na PO |

## Decyzje czekające na ADR (z backlogu)

- US-015: jedna wersja Pythona (3.12 vs 3.14) i Node.
