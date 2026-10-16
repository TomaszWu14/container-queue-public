---
name: "Historyjka użytkownika [BA]"
about: "Nowa funkcja lub zmiana zachowania: analiza BA, wymagania bezpieczeństwa SEC, priorytet PO"
title: "[US-xxx] Jako <rola> chcę <cel>, aby <korzyść>"
labels: ["historyjka"]
---

<!-- Wypełnia [BA]. Sekcję „Bezpieczeństwo” wypełnia [SEC] przed Definition of Ready. Priorytet nadaje PO.
     Po akceptacji historyjka trafia do docs/analiza/HISTORYJKI.md i SLEDZENIE.md. -->

## Historyjka

**Jako** <rola z `docs/analiza/INTERESARIUSZE.md`>
**chcę** <cel>
**aby** <korzyść>.

**Źródło:** <P-xx / T-xx / R-xx / rozmowa z PO dd.mm.rrrr>
**Wymagania:** <FR-xxx / NFR-xxx / SR-xxx z `docs/analiza/WYMAGANIA.md`>
**Priorytet (MoSCoW):** Must / Should / Could / Won't — nadaje PO
**Rozmiar:** XS / S / M / L

## Kryteria akceptacji (każde = test)

1. **Dane:** <stan wyjściowy> → **Gdy:** <akcja> → **Wtedy:** <wynik, kod odpowiedzi, komunikat>.
2. **Dane:** … → **Gdy:** … → **Wtedy:** …
3. Przypadek odmowy: **Dane:** rola <X> / obca spółka → **Gdy:** … → **Wtedy:** 403 / 404.

## Wymagania niefunkcjonalne

- wydajność / dostępność / użyteczność / RODO: <albo „bez zmian”>

## Bezpieczeństwo [SEC]

- **Klasa danych** (`docs/bezpieczenstwo/KLASYFIKACJA_DANYCH.md`): P / W / F / O / S
- **Nowy przepływ danych?** tak → tabela STRIDE w `THREAT_MODEL.md` / nie
- **Mini-STRIDE:** S: … · T: … · R: … · I: … · D: … · E: …
- **Kryteria bezpieczeństwa (dopisane do testów):** …
- **Ryzyko pozostające otwarte:** <R-xx w `RYZYKA.md` / brak>

## Definition of Ready

- [ ] cel jasny
- [ ] kryteria testowalne
- [ ] zależności znane
- [ ] dane i uprawnienia określone
- [ ] klasa danych i kryteria SEC
- [ ] priorytet od PO

## Pytania do PO

1. …
