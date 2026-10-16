# RODO — wersja 0.1

2026-10-16, [SEC] z [BA]. Dokument opisuje, **co aplikacja robi z danymi osobowymi** i czego organizacja
musi jeszcze ustalić. Pola „do potwierdzenia” wymagają odpowiedzi PO (Z-009) i weryfikacji prawnej —
zespół nie zastępuje prawnika ani inspektora ochrony danych.

## 1. Role

| Rola | Kto | Status |
|---|---|---|
| Administrator danych | spółka z grupy, której logistyka prowadzi kolejkę (albo każda spółka dla swoich kontenerów — współadministrowanie?) | **do potwierdzenia** |
| Podmiot przetwarzający (hosting) | dostawca VPS/serwera z Coolify | **do potwierdzenia** (umowa powierzenia) |
| Osoba kontaktowa / IOD | — | **do potwierdzenia** |
| Operator aplikacji | administrator aplikacji (rola `admin`) | PO |

## 2. Kategorie osób i danych

Inwentarz z klasą i retencją: `KLASYFIKACJA_DANYCH.md` (klasa **O**).

| Osoby | Dane | Źródło | Cel |
|---|---|---|---|
| Użytkownicy (pracownicy spółek, partnerów) | login, e-mail, imię i nazwisko, rola, awatar, IP logowań, sekret 2FA | zakładane przez admina / zaproszenie | uwierzytelnianie, rozliczalność zmian |
| **Kierowcy** (osoby trzecie, bez konta) | imię, telefon, nr dokumentu, nr auta i naczepy | podaje spedytor (formularz awizacji etap 2 lub panel) | awizacja dostawy, wpuszczenie na bramę, SMS z terminem |
| Osoby kontaktowe u partnerów i dostawców | imię, e-mail, telefon | słowniki (logistyka) | kontakt operacyjny |
| Osoby fizyczne jako klienci (jeśli występują) | nazwa odbiorcy, dane zamówienia | kontener / zamówienie klienta | realizacja dostawy |

## 3. Cele i podstawy prawne (propozycja do weryfikacji prawnej)

| Czynność | Podstawa (propozycja) | Uwagi |
|---|---|---|
| Prowadzenie kont użytkowników i audyt zmian | art. 6 ust. 1 lit. b (umowa/współpraca) lub lit. f (uzasadniony interes: bezpieczeństwo, rozliczalność) | pracownicy partnerów: lit. f |
| Dane kierowców do awizacji i wpuszczenia na magazyn | art. 6 ust. 1 lit. f (uzasadniony interes: organizacja i bezpieczeństwo dostawy) | kierowca nie jest stroną; obowiązek informacyjny przez spedytora — **do potwierdzenia** |
| SMS do kierowcy z terminem i linkiem | lit. f | treść bez zbędnych danych |
| Log logowań (IP, loginy) | lit. f (bezpieczeństwo) | 90 dni |
| Telemetria błędów (Sentry, jeśli włączone) | lit. f | scrubbing PII; lokalizacja serwerów Sentry — **do potwierdzenia** (transfer poza EOG?) |

## 4. Retencja (wdrożona w kodzie, `retention.py`, `avizo_workflow.py`)

| Dane | Okres | Zmienna | Co się dzieje |
|---|---|---|---|
| Dane kierowcy (kontener + kopie w powiadomieniach i SMS) | 90 dni po zamknięciu awizacji / ZREALIZOWANY | `DRIVER_DATA_RETENTION_DAYS` | anonimizacja, wpis w audycie |
| Log logowań (`audit_log` typu `auth`) | 90 dni | `AUDIT_AUTH_RETENTION_DAYS` | usunięcie |
| Historia SMS | 90 dni | `SMS_RETENTION_DAYS` | usunięcie |
| Refresh tokeny i tokeny resetu po wygaśnięciu | 30 dni | `TOKEN_RETENTION_DAYS` | usunięcie |
| Błędy JS z przeglądarki | 30 dni | `CLIENT_ERROR_RETENTION_DAYS` | usunięcie |
| Przeczytane powiadomienia | 90 dni | `NOTIFICATION_RETENTION_DAYS` | usunięcie |
| Konto użytkownika | do usunięcia przez admina | — | anonimizacja (`usuniety-<id>`), historia zostaje z pseudonimem |
| Kontakty partnerów, dokumenty handlowe | bez retencji | — | **do ustalenia** (O-3 w `WYMAGANIA.md`) |
| Kopie zapasowe | GFS: 14 ostatnich + 8 tygodni + 12 miesięcy | `BACKUP_KEEP*` | dane w kopii żyją dłużej niż retencja w bazie — **do odnotowania w informacji dla osób** |

## 5. Prawa osób — jak realizujemy

| Prawo | Mechanizm | Kto wykonuje |
|---|---|---|
| Dostęp i przenoszenie (art. 15, 20) | `GET /api/admin/data-subject?…` — JSON ze wszystkich miejsc (konto, wiadomości, powiadomienia, audyt, kontenery z danymi kierowcy, SMS); `data_subject.py` | admin na wniosek |
| Usunięcie (art. 17) | użytkownik: `DELETE /api/users/{id}` = anonimizacja; kierowca: `POST /api/admin/data-subject/anonymize-driver` (ta sama ścieżka co retencja) | admin na wniosek |
| Sprostowanie (art. 16) | edycja w panelu (profil, słowniki, dane kierowcy) z wpisem w historii | użytkownik / logistyka |
| Sprzeciw, ograniczenie (art. 18, 21) | brak flagi „ograniczenie przetwarzania” w systemie | ręcznie — **luka do decyzji** |
| Informacja (art. 13, 14) | brak tekstu informacyjnego w aplikacji i w formularzu awizacji | **do przygotowania** (US-012) |

Termin odpowiedzi: 30 dni. Procedura obsługi wniosku: `../operacje/RUNBOOK.md` §„Wniosek osoby (RODO)”.

## 6. Odbiorcy i powierzenia

| Odbiorca | Dane | Rola | Umowa / status |
|---|---|---|---|
| Hosting (VPS z Coolify) | wszystkie (baza, pliki, kopie) | procesor | **do potwierdzenia** |
| SMSAPI.pl | telefon kierowcy, treść SMS | procesor | **do potwierdzenia** |
| Microsoft 365 (Graph mail, SharePoint, Power BI) | adresy e-mail spedytorów, treść maili awizacji; arkusz kolejki | procesor (tenant grupy) | umowa M365 grupy — **do potwierdzenia** |
| Sentry (gdy `SENTRY_DSN`) | zdarzenia błędów po scrubbingu (bez haseł, tokenów, e-maili, telefonów) | procesor | **do potwierdzenia**; region przechowywania |
| Teams webhook | treść powiadomień (bez danych kierowcy) | w tenancie grupy | — |
| aisstream.io, Open-Meteo, NBP | brak danych osobowych (pozycje statków, pogoda, kursy) | — | n/d |
| Ollama (LLM) | fakty o kontenerach bez pól ukrytych; model lokalny na własnym serwerze | brak powierzenia | n/d (wymuszony adres wewnętrzny) |
| n8n (własny serwer) | treść zdarzeń (bez danych kierowcy), maile z poczekalni | w infrastrukturze administratora | n/d |
| Spedytorzy, agencja celna, magazyn zewnętrzny | dane kontenerów i kierowców w zakresie zlecenia | odrębni administratorzy / odbiorcy | **do potwierdzenia** |

Transfery poza EOG: potencjalnie Sentry i Microsoft 365 — **do potwierdzenia** (standardowe klauzule).

## 7. Minimalizacja i bezpieczeństwo

- Nie zbieramy: adresów domowych kierowców, dat urodzenia, zdjęć osób; numer dokumentu tylko do wpuszczenia na bramę.
- Dane kierowcy nie trafiają do historii zmian (`•••`), maili, Teams ani zdarzeń n8n; tokeny linków maskowane w logach.
- Testy i instancja demo wyłącznie na danych syntetycznych; repozytorium anonimizowane (2026-10-12).
- Kontrole techniczne: `../../SECURITY.md`, `THREAT_MODEL.md`, `CHECKLISTA_ASVS.md`.

## 8. Incydent

Naruszenie ochrony danych: ocena ryzyka dla osób, zgłoszenie do organu w **72 h** od stwierdzenia (gdy
ryzyko), zawiadomienie osób (gdy wysokie ryzyko). Kroki techniczne: `../operacje/RUNBOOK.md` §„Incydent”.
Rejestr naruszeń: **do założenia** (US-012).

## 9. Rejestr czynności przetwarzania (szkielet, art. 30)

| # | Czynność | Osoby | Dane | Cel | Podstawa | Odbiorcy | Retencja | Zabezpieczenia |
|---|---|---|---|---|---|---|---|---|
| 1 | Konta i logowanie | użytkownicy | §2 | uwierzytelnianie, rozliczalność | §3 | hosting, Sentry | konto / 90 dni (logi) | bcrypt, 2FA, audyt |
| 2 | Awizacja dostaw | kierowcy, spedytorzy | §2 | organizacja dostawy | §3 | hosting, SMSAPI, M365, magazyn | 90 dni | maskowanie, retencja, linki jednorazowe |
| 3 | Powiadomienia | użytkownicy | e-mail, treść | informowanie o zdarzeniach | §3 | M365/SMTP, Teams | 90 dni (przeczytane) | bez danych kierowcy |
| 4 | Kopie zapasowe | wszyscy | wszystkie | ciągłość | lit. f | hosting | GFS | szyfrowanie `age` |

## 10. DPIA

Ocena wstępna: przetwarzanie nie jest systematycznym monitorowaniem ani profilowaniem na dużą skalę; dane
kierowców to dane zwykłe. **Wstępnie DPIA niewymagana** — do potwierdzenia przez IOD/prawnika (Z-009).
