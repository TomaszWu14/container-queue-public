# Interesariusze

Wersja 0.1 (2026-10-16), [BA]. Role systemowe i zakres widoczności: `docs/01-problem-i-zakres.md`,
`backend/app/deps.py`. Przedstawiciele: do potwierdzenia przez PO (Z-003).

Wpływ / zainteresowanie: **W** wysokie, **Ś** średnie, **N** niskie.

| Interesariusz | Rola w systemie | Cel / oczekiwanie | Wpływ | Zaint. | Przedstawiciel | Kanał |
|---|---|---|---|---|---|---|
| Product Owner | decyduje o zakresie, priorytetach, ryzykach, wydaniach | aplikacja zastępuje Excel; proces widoczny w repo | W | W | właściciel repozytorium | PR, issues, rozmowa |
| Logistyka spółki | `logistics` | mniej pracy ręcznej, jeden stan kontenera, pewne terminy | W | W | do potwierdzenia | PO |
| Logistyka grupy („wszystkie spółki”) | `logistics` + `view_all_companies` | jeden obraz kolejki wszystkich spółek, importy SAP | W | W | do potwierdzenia | PO |
| Magazyn własny | `warehouse` | wiedzieć, co i kiedy przyjedzie; potwierdzić rozładunek z tabletu na hali | Ś | W | do potwierdzenia | PO |
| Magazyn zewnętrzny (MAG-1) | `warehouse` zawężony do magazynu; link wywołań palet | widzieć tylko swoje dostawy; wywołania palet bez logowania | Ś | Ś | do potwierdzenia | PO |
| Spedytor (3 firmy) | `forwarder` albo jednorazowy link | dostać zlecenie, potwierdzić termin, podać kierowcę bez zakładania konta | Ś | Ś | do potwierdzenia | PO; e-mail z aplikacji |
| Agencja celna | `customs` | zlecone odprawy, komplet dokumentów, raportowanie statusu | Ś | Ś | do potwierdzenia | PO |
| Zakupy | `purchasing` | zamówienia i dokumenty handlowe | N | Ś | do potwierdzenia | PO |
| Sprzedaż | `sales` (tylko odczyt) | kiedy towar będzie dostępny | N | Ś | do potwierdzenia | PO |
| Kierowca | brak konta; dane osobowe w awizacji | SMS z terminem; jego dane znikają po 90 dniach | N | N | — | SMS |
| Administrator aplikacji | `admin` | konta, słowniki, konfiguracja, audyt, kopie | W | W | PO | — |
| IT grupy (M365 / Entra ID) | brak roli; właściciel tenanta | bezpieczeństwo integracji; odmówiło rejestracji aplikacji w Entra ID (D6) | W | N | do potwierdzenia | przez PO |
| Zespół BA / DEV / SEC | prowadzi repozytorium | spójny proces, mierzalne kryteria, brak regresji | Ś | W | ten proces | PR, docs |
| Odbiorcy repo publicznego (rekruter, audytor, nowy członek zespołu) | czytelnicy | dojrzały, czytelny proces; demo działające | N | Ś | — | README, demo |
| Organ nadzorczy (RODO) | — | zgodność przetwarzania danych kierowców i użytkowników | W | N | — | `../bezpieczenstwo/RODO.md` |

## Konflikty interesów do pilnowania

- **Logistyka vs magazyn:** limit dzienny rozładunków to ostrzeżenie, nie blokada (D5) — magazyn musi widzieć,
  kto limit przekroczył.
- **Spedytor vs agencja celna:** firma może być jednym i drugim (osobne konta); wiadomości jednej strony
  ukryte przed drugą (`REGULY-PROCESU.md`).
- **Spółki między sobą:** separacja danych jest wymaganiem krytycznym (FR-022, R-01).
- **Partner bez konta vs bezpieczeństwo:** link jednorazowy i krótko ważny; publiczne linki dla klienta
  i kierowcy usunięte (D11).
