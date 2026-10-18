# Mierniki przed i po

> **Uwaga (Z-025, do potwierdzenia przez PO).** Liczby „przed” pochodzą z analizy problemu
> ([`../01-problem-i-zakres.md`](../01-problem-i-zakres.md)). Liczby „po” aplikacja liczy sama z dziennika
> zmian i dziennika zadań; tam, gdzie potrzebny jest przelicznik na minuty, używa **jawnych założeń**
> (Z-020, Z-024) pokazanych na ekranie i zmienianych przez admina. Nic tu nie jest pomiarem stoperem.

## Stan przed (fakty z analizy)

| Miernik | Wartość |
|---|---|
| Kontenery | ok. 200 miesięcznie, 4 spółki, 2 magazyny, 3 spedytorów |
| Osoby prowadzące arkusz | 4 w logistyce |
| Czas na utrzymanie arkusza, wersje i maile | ok. 30 h tygodniowo łącznie |
| Status kontenera | brak (tylko status odprawy: 3 wartości) |
| Historia zmian | brak |
| Walidacja numeru kontenera | brak |

## Stan po — gdzie aplikacja to liczy

| Miernik | Skąd | Ekran |
|---|---|---|
| Zmiany zapisane w aplikacji zamiast Excela + maila | dziennik zmian (`audit_log`) | Pulpit → „Ile to oszczędza” |
| Godziny oszczędzone na zmianach | zmiany × 3 min (Z-020) | Pulpit → „Ile to oszczędza” |
| Godziny oszczędzone przez automaty | efekty × minuty na efekt (Z-024) | Automatyzacje → KPI „zaoszczędzone” |
| Dostawy na czas | data statusu DOSTARCZONY vs plan | Pulpit → „Ile to oszczędza” |
| Kontenery z kompletem dokumentów | checklista dokumentów | Pulpit → „Ile to oszczędza” |
| Odsetek pozycji faktur dopasowanych automatycznie | źródło dopasowania pozycji | Automatyzacje → „Odczyt faktur” |
| Trafność modelu wg pewności | decyzje operatorów | Automatyzacje → „Odczyt faktur” |
| Czas w etapie (mediana, 90. percentyl) i cofnięcia | historia statusów | Automatyzacje → „Przebieg procesu” |

## Szacunek rzędu wielkości (do potwierdzenia)

Tylko zmiany statusu, bez dokumentów, odprawy i awizacji:

- 200 kontenerów × 9 przejść między 10 statusami = **1 800 zmian miesięcznie**,
- × 3 minuty na zmianę (Z-020: wpis w Excelu + mail do zainteresowanych) = **90 h miesięcznie ≈ 21 h tygodniowo**.

To porównywalne z 30 h tygodniowo z analizy — rząd wielkości się zgadza, ale dokładna liczba wymaga
pomiaru u PO (Z-025): ile zmian robi się dziś naprawdę i ile czasu zajmowała jedna zmiana w Excelu.

## Czego potrzebujemy od PO, żeby zamienić założenia na pomiar

1. Potwierdzenie albo korekta 3 minut na zmianę (Z-020) i minut na efekt automatu (Z-024).
2. Jedna próbka z okresu przed aplikacją: liczba maili o kontenerach w typowym tygodniu.
3. Zgoda na porównanie „dostawy na czas” z okresem przed wdrożeniem (jeśli dane istnieją w SAP).
