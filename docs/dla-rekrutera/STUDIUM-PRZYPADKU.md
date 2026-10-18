# Studium przypadku: z arkusza Excel do jednego obrazu dostaw z automatami

**Branża:** import kontenerowy, grupa kilku spółek · **Rola:** analityk / developer, projekt prowadzony sam
(lipiec–październik 2026) · **Demo:** [container.queue.twapp.pl/demo](https://container.queue.twapp.pl/demo)

## Problem

Kolejka dostaw — ok. **200 kontenerów miesięcznie**, 4 spółki, 2 magazyny, 3 spedytorów — żyła w jednym
arkuszu Excel rozsyłanym mailem. Arkusz nie miał statusu kontenera, historii ani walidacji; partnerzy pracowali
na kopiach. Utrzymanie arkusza, uzgadnianie wersji i wyjaśnianie mailowe zajmowało **4 osobom ok. 30 godzin
tygodniowo**.

## Jak doszedłem do rozwiązania

1. **Wywiad projektowy** — 50 pytań z logistyką ([`SPECYFIKACJA.md`](../SPECYFIKACJA.md)), mapa procesu
   przed i po ([`02-proces.md`](../02-proces.md)), 28 wymagań z kryteriami akceptacji
   ([`05-wymagania.md`](../05-wymagania.md)).
2. **Model danych i reguły** — 10 statusów kontenera z regułami cofania, osobny status odprawy, izolacja
   danych per spółka i partner w jednym miejscu kodu.
3. **Decyzje zapisane wprost** — 12 decyzji z rozważanymi opcjami ([`06-decyzje.md`](../06-decyzje.md)), np.
   jedno pole daty dostawy ze statusem zamiast dwóch pól, zamrożenie uzgodnionej daty mimo zmian ETA.
4. **Automatyzacja tam, gdzie zwraca się najszybciej** — najpierw przepisywanie (poczta, faktury), potem
   pilnowanie terminów (alerty), na końcu komunikacja (SMS, przeglądy dnia). Każdy automat ma właściciela
   decyzji: [macierz automatyzacji](MACIERZ-AUTOMATYZACJI.md).

## Rozwiązanie

- **Jeden stan kontenera** dla logistyki, magazynów, spedytorów i agencji celnej — każdy widzi tylko swoje.
- **Historia każdej zmiany** (kto, kiedy, było → jest, powód) i walidacja numeru kontenera (ISO 6346).
- **21 automatów z harmonogramu i 3 obiegi z n8n**, m.in.:
  - poczta → poczekalnia dokumentów: numer kontenera z treści maila, człowiek klika „Potwierdź”,
  - odczyt faktur: OCR + reguły + model ML uczony na decyzjach operatorów, z progiem pewności,
  - alerty: kara za przestój, braki dokumentów przed ETA, przeciążenie magazynu, opóźnienia statków (AIS),
  - kreator reguł bez kodu: admin sam ustawia „gdy warunek → powiadom”,
  - zdarzenia z podpisem HMAC do n8n / Power Automate / Make.
- **Awizacja przez jednorazowy link** dla spedytora — bez zakładania mu konta.

Szczegóły obiegu dokumentu przed i po: [`OBIEG-DOKUMENTU-PRZED-PO.md`](OBIEG-DOKUMENTU-PRZED-PO.md).

## Wynik i jak go mierzę

- Aplikacja sama liczy zmiany zapisane zamiast Excela + maila i efekty każdego automatu; przelicznik na minuty
  to jawne założenia widoczne na ekranie (Z-020, Z-024), zmieniane przez admina.
- Szacunek rzędu wielkości (tylko zmiany statusu): 200 kontenerów × 9 przejść × 3 min ≈ **21 h tygodniowo** —
  zgodny z 30 h z analizy. Dokładny pomiar czeka na dane PO: [`MIERNIKI-PRZED-PO.md`](MIERNIKI-PRZED-PO.md).
- Jakość automatu jest widoczna, nie deklarowana: udział pozycji faktur dopasowanych automatycznie, trafność
  modelu w przedziałach pewności, czas w etapach procesu i kontenery „dłużej niż zwykle” — ekran Automatyzacje.

## Jakość i bezpieczeństwo

Testy backendu i frontendu w CI (ponad 3000), skany Semgrep / Trivy / Bandit i sekretów, macierz uprawnień
rola × trasa sprawdzana testem, model zagrożeń STRIDE i rejestr ryzyk ([`../bezpieczenstwo/`](../bezpieczenstwo/)),
RODO: automatyczne usuwanie danych kierowców po 30 dniach.

## Czego się nauczyłem

- Automat bez widocznego stanu to ryzyko — dlatego ekran Automatyzacje pokazuje, co działa, co się spóźnia
  i co padło, a każda awaria zapala dzwonek admina.
- Najtrudniejsze były decyzje „czego nie automatyzować” (data uzgodniona ze spedytorem, cofanie statusu) —
  spisane w macierzy, żeby nie wracały w każdej rozmowie.
- Liczby „ile to oszczędza” muszą mieć założenie na wierzchu — inaczej nikt im nie uwierzy.
