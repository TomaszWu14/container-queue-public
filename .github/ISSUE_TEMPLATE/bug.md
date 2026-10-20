---
name: "Błąd"
about: "Aplikacja robi coś innego, niż powinna (bez podatności bezpieczeństwa — te zgłaszaj wg SECURITY.md)"
title: "[BUG] <krótki opis>"
labels: ["błąd"]
---

<!-- Bez danych osobowych i danych produkcyjnych: numery kontenerów, nazwy firm i osoby zastąp fikcyjnymi.
     Podatność bezpieczeństwa? NIE tutaj — SECURITY.md. -->

## Co się dzieje

<opis>

## Kroki odtworzenia

1. zaloguj się jako rola <…> (konto testowe / demo)
2. …
3. …

**Oczekiwane:** …
**Faktyczne:** … (komunikat, kod odpowiedzi, `X-Request-ID` z nagłówka odpowiedzi, jeśli jest)

## Waga (jak w `docs/testy/BUGS-FOUND.md`)

krytyczna (utrata/wyciek danych, prod nie działa) · wysoka (błędne dane, obejście uprawnień) ·
średnia (awaria przy nietypowych danych, ryzyko DoS) · niska (niespójność, martwy kod)

## Środowisko

- instancja: produkcja / demo / lokalnie (`/api/health` → `version`)
- przeglądarka / urządzenie:
- rola użytkownika:

## Naruszone wymaganie / reguła

<FR-xxx z `docs/analiza/WYMAGANIA.md` albo wiersz z `docs/REGULY-PROCESU.md`; „brak” = kandydat na nowe wymaganie>

## Test potwierdzający (wypełnia [DEV])

<ścieżka testu, który będzie czerwony przed poprawką i zielony po>
