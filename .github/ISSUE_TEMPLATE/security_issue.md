---
name: "Zgłoszenie bezpieczeństwa [SEC]"
about: "Śledzenie ustalenia bezpieczeństwa BEZ szczegółów exploita (repozytorium jest publiczne)"
title: "[SEC] <obszar>: <krótki opis bez szczegółów technicznych>"
labels: ["bezpieczeństwo"]
---

<!-- UWAGA: to repozytorium jest publiczne. Szczegóły podatności (kroki, payload, dane) przekazuj
     PRYWATNIE wg SECURITY.md. To issue służy tylko do śledzenia prac po tym, jak zgłoszenie dotarło
     prywatnie i SEC uznał, że można je ujawnić w tej formie. -->

## Obszar

uwierzytelnianie / autoryzacja i izolacja danych / walidacja wejścia / pliki / sekrety i konfiguracja /
nagłówki i sesje / zależności i CI / RODO / inne

## Opis (bez exploita)

<co jest nie tak, jakiego aktywa dotyczy; klasa danych z `docs/bezpieczenstwo/KLASYFIKACJA_DANYCH.md`>

## Wstępna ocena [SEC]

- **Waga:** krytyczna / wysoka / średnia / niska
- **Prawdopodobieństwo:** niskie / średnie / wysokie · **Skutek:** niski / średni / wysoki / krytyczny
- **Kategoria STRIDE:** S / T / R / I / D / E
- **Odniesienie:** OWASP Top 10 <A0x> · ASVS <rozdział> · `RYZYKA.md` <R-xx, jeśli już jest>

## Decyzja

- [ ] poprawka — historyjka US-xxx (Must przy wadze wysokiej/krytycznej)
- [ ] akceptacja ryzyka przez PO — wyjątek E-xx w `RYZYKA.md` z datą przeglądu
- [ ] fałszywy alarm — uzasadnienie:

## Weryfikacja

<test odtwarzający przed poprawką i po; narzędzie, które powinno to wykrywać w CI>
