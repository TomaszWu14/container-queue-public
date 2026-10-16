# Klasyfikacja danych

Wersja 0.1 (2026-10-16), [SEC]. Źródło inwentarza: modele `backend/app/models/`, `config.py`,
`docs/AUDYT.md` §3.3. Właściciel klasyfikacji: PO; przegląd przy każdej nowej encji lub integracji
(pytanie w szablonie historyjki).

## Klasy i zasady postępowania

| Klasa | Definicja | Przechowywanie | Przekazywanie | Logi / Sentry | Kopie | Testy i demo |
|---|---|---|---|---|---|---|
| **P — publiczne** | wolno pokazać każdemu | bez ograniczeń | bez ograniczeń | dowolnie | — | dowolnie |
| **W — wewnętrzne** | dla zalogowanych użytkowników w ramach separacji spółek | baza, wolumen `/data` | tylko po uwierzytelnieniu i w zakresie roli (`deps.py`) | identyfikatory tak, treść pól nie | szyfrowane `age` | tylko dane syntetyczne |
| **F — poufne (handlowe)** | ceny, faktury, dane klientów, stany; szkoda biznesowa przy wycieku | jak W | jak W + ukryte przed rolami bez potrzeby (`hidden_fields`) | nigdy w treści logów | szyfrowane | syntetyczne |
| **O — dane osobowe** | identyfikują osobę (RODO) | jak W + retencja z `config.py` | minimalizacja: tylko odbiorcy procesu (spedytor → magazyn) | maskowane (`redaction.py`, `audit._MASKED_FIELDS`); zakaz imion w komunikatach błędów | szyfrowane; retencja kopii = retencja GFS | **zakaz** danych rzeczywistych |
| **S — sekrety** | klucze, hasła, tokeny | wyłącznie zmienne środowiskowe (Coolify); w bazie tylko hash albo Fernet | nigdy w repo, logach, PR, zrzutach | nigdy | poza kopią bazy (env nie jest backupowany — RUNBOOK) | wartości testowe oznaczone `gitleaks:allow` |

Zasada łączenia: rekord dziedziczy najwyższą klasę swoich pól (kontener z danymi kierowcy = **O**).

## Inwentarz

| Dane | Klasa | Gdzie | Retencja | Kto widzi | Maskowanie |
|---|---|---|---|---|---|
| Konta użytkowników: login, e-mail, imię i nazwisko, rola, awatar | O | `users` | do usunięcia konta → anonimizacja (`usuniety-<id>`) | admin; własne dane użytkownik | — |
| Hasła (bcrypt), sekret TOTP, kody zapasowe (SHA-256) | S | `users` | jak konto | nikt (hash) | n/d |
| Refresh tokeny (JTI), tokeny resetu hasła (SHA-256) | S | `refresh_tokens`, `password_reset_tokens` | 30 dni po wygaśnięciu (`TOKEN_RETENTION_DAYS`) | nikt | n/d |
| Log logowań: IP, wpisany login (skrót dla nieistniejących) | O | `audit_log` (`entity_type=auth`), `login_failures` (SHA-256) | 90 dni (`AUDIT_AUTH_RETENTION_DAYS`); okno limitera 15 min | admin | skrót loginu |
| **Dane kierowcy:** imię, telefon, nr dokumentu, nr auta i naczepy | O | `containers.driver_*`, kopie w powiadomieniach i SMS | 90 dni po zamknięciu awizacji / ZREALIZOWANY (`DRIVER_DATA_RETENTION_DAYS`) | logistyka, magazyn, spedytor danego kontenera | `•••` w historii zmian; brak w treści maili/Teams/n8n |
| Historia SMS (telefon, treść z linkiem) | O | `sms_messages` | 90 dni (`SMS_RETENTION_DAYS`) | admin | — |
| Kontakty partnerów (spedytor, agencja, dostawca: e-mail, telefon, osoba) | O | słowniki (`forwarders`, `customs_agencies`, `suppliers`, master data) | bez retencji (dane kontaktowe firm) | logistyka, admin | — |
| Powiadomienia użytkowników, wiadomości przy kontenerze, wzmianki | W (O, gdy zawierają dane kierowcy) | `notifications`, `messages` | przeczytane 90 dni (`NOTIFICATION_RETENTION_DAYS`); wiadomości bez retencji | adresaci; agencja ↔ spedytor wzajemnie ukryte | dane kierowcy nie trafiają do treści |
| Kolejka: kontener, statusy, daty, magazyn, port, statek | W | `containers` i powiązane | bez retencji (archiwum = ZREALIZOWANY) | wg separacji spółek i roli | — |
| Dokumenty transportowe (CMR, packing list, zdjęcia rozładunku) | W | `attachments`, wolumen `/data/uploads` | bez retencji | wg roli (`forwarder_may_see`) | — |
| Dokumenty handlowe i celne (PI, CI, BL, SAD, draft SAD), faktury i pozycje | F | `attachments`, `invoices*`, `sad_drafts` | bez retencji | logistyka, zakupy, agencja (odprawowe); **nie** spedytor, **nie** magazyn | ukryte kafelki |
| Wyceny transportu, ceny, oferty | F | `quotes`, `transport_jobs` | bez retencji | logistyka, admin; spedytor tylko swoje oferty | — |
| Zamówienia SAP (EKKO), materiały (MARM, REF), stany DLT, PAZ, dane Power BI | F | `sap_orders`, `materials`, `pallet_*`, cache | bez retencji; cache 15 min | logistyka grupy, admin; inne spółki tylko odczyt wspólnych | — |
| Dane klientów na kontenerze (odbiorca, zamówienie klienta) | F (O, gdy osoba fizyczna) | `containers.customer_*`, `customer_orders` | bez retencji | logistyka, sprzedaż (bez kosztów) | — |
| Historia zmian (kto, kiedy, było → jest, powód) | W | `audit_log` | bez retencji (rozliczalność) | wg separacji spółek (ACL-002) | pola kierowcy `•••` |
| Dziennik serwera, metryki zadań, błędy JS z przeglądarki | W | `applog`, `job_runs`, `client_errors` | błędy JS 30 dni (`CLIENT_ERROR_RETENTION_DAYS`) | admin | tokeny linków `[token]` |
| Sekrety konfiguracji: `SECRET_KEY`, `DATA_ENCRYPTION_KEY`, hasła DB/SMTP, tokeny M365, SMSAPI, AIS, n8n, klucz `age` | S | zmienne środowiskowe Coolify | — | operator | n/d |
| Cache MSAL (refresh token M365) | S | baza, Fernet (`crypto.py`) | do wylogowania integracji | nikt | szyfrowane |
| Tokeny linków publicznych (awizacja, DLT) | S | baza: tylko SHA-256; w URL u odbiorcy | 7/5 dni, maks. 90 (`PUBLIC_LINK_MAX_DAYS`) | odbiorca linku | `[token]` w logach, `no-referrer`, `noindex` |
| Dane demo (150 kontenerów, konto `demo`) | P | instancja demo | reset nocny | każdy | syntetyczne; **zakaz danych rzeczywistych** (Z-010) |
| Kod, dokumentacja, zrzuty ekranu w repo | P | GitHub | — | każdy | bez danych rzeczywistych (anonimizacja 2026-10-12) |

## Luki i decyzje

- Dokumenty handlowe i celne (F) nie mają retencji ani polityki archiwizacji po ZREALIZOWANY — do decyzji PO
  (wymóg księgowy vs minimalizacja).
- Kontakty osób u partnerów (O) nie mają retencji — przyjęto „dane kontaktowe firmy”; do potwierdzenia w `RODO.md`.
- Załączniki od partnerów weryfikowane tylko po rozszerzeniu (R-03, US-004).
- Zmienne środowiskowe nie są objęte kopią zapasową — odtworzenie wymaga ich osobnego zabezpieczenia (RUNBOOK).
